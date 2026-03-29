from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from backend.database import get_db
from backend.models import User, JobDescription, Candidate, Analysis
from backend.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    JobDescriptionCreate,
    JobDescriptionUpdate,
    JobDescriptionResponse,
    AnalysisRequest,
    AnalysisResult,
)
from backend.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    decode_token,
)
from backend.services.analysis import analyze_resume, generate_summary

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = (
        db.query(User)
        .filter((User.email == user.email) | (User.username == user.username))
        .first()
    )
    if db_user:
        raise HTTPException(
            status_code=400, detail="Email or username already registered"
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, username=user.username, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/job-descriptions", response_model=JobDescriptionResponse)
def create_job_description(
    jd: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from backend.services.analysis import extract_skills

    required_skills = extract_skills(jd.content)
    db_jd = JobDescription(
        user_id=current_user.id,
        title=jd.title,
        content=jd.content,
        required_skills=required_skills,
        threshold=jd.threshold,
    )
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd


@router.get("/job-descriptions", response_model=List[JobDescriptionResponse])
def list_job_descriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(JobDescription)
        .filter(JobDescription.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/job-descriptions/{jd_id}", response_model=JobDescriptionResponse)
def get_job_description(
    jd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    jd = (
        db.query(JobDescription)
        .filter(JobDescription.id == jd_id, JobDescription.user_id == current_user.id)
        .first()
    )
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    return jd


@router.delete("/job-descriptions/{jd_id}")
def delete_job_description(
    jd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    jd = (
        db.query(JobDescription)
        .filter(JobDescription.id == jd_id, JobDescription.user_id == current_user.id)
        .first()
    )
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")

    db.delete(jd)
    db.commit()
    return {"message": "Job description deleted successfully"}


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_resumes(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from PyPDF2 import PdfReader
    from io import BytesIO

    results = []
    jd = JobDescription(
        user_id=current_user.id,
        title=f"Analysis {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        content=request.job_description,
        threshold=request.threshold,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)

    return AnalysisResult(
        candidates=[], summary={"total_candidates": 0}, job_description_id=jd.id
    )


@router.post("/analyze/pdf")
async def analyze_pdf_resumes(
    job_description: str = Form(...),
    threshold: float = Form(65.0),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from utils import (
        extract_text_from_pdf,
        calculate_detailed_match,
        calculate_ats_score,
        detect_experience_years,
        extract_semantic_skills
    )
    from datetime import datetime
    import io

    results = []
    jd = JobDescription(
        user_id=current_user.id,
        title=f"PDF Analysis {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        content=job_description,
        threshold=threshold,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)

    for f in files:
        file_bytes = await f.read()
        file_obj = io.BytesIO(file_bytes)
        text = extract_text_from_pdf(file_obj)
        
        if text and len(text) > 50:
            detailed = calculate_detailed_match(job_description, text)
            ats = calculate_ats_score(text)
            exp = detect_experience_years(text)
            req_skills = extract_semantic_skills(job_description)
            cand_skills = detailed.get("all_resume_skills", [])
            missing = list(set(req_skills) - set([s.lower() for s in cand_skills]))
            
            cand = Candidate(
                job_description_id=jd.id,
                name=f.filename.replace(".pdf", "").replace(".txt", ""),
                resume_text=text,
                resume_filename=f.filename,
                skills=cand_skills
            )
            db.add(cand)
            db.commit()
            db.refresh(cand)
            
            status = "Shortlisted" if detailed["total"] >= threshold else "Not Selected"
            
            analysis = Analysis(
                user_id=current_user.id,
                job_description_id=jd.id,
                candidate_id=cand.id,
                match_score=detailed["total"],
                semantic_similarity=detailed.get("keyword_score", 0.0),
                skill_depth=detailed.get("skill_score", 0.0),
                missing_skills=missing[:5],
                matched_skills=cand_skills[:6],
                status=status
            )
            db.add(analysis)
            db.commit()

            results.append({
                "Rank": 0,
                "Candidate": cand.name,
                "Score": round(detailed["total"], 1),
                "Skill_Score": detailed.get("skill_score", 0),
                "Exp_Score": detailed.get("experience_score", 0),
                "KW_Score": detailed.get("keyword_score", 0),
                "ATS": ats,
                "Experience": exp,
                "Skills_Count": len(cand_skills),
                "Missing": missing[:5],
                "Missing_Count": len(missing),
                "Status": status,
                "Top_Skills": cand_skills[:6],
            })

    results = sorted(results, key=lambda x: x["Score"], reverse=True)
    for i, r in enumerate(results):
        r["Rank"] = i + 1

    return {
        "job_description_id": jd.id,
        "candidates": results,
        "summary": {"total_candidates": len(results)}
    }


@router.get("/analyses")
def list_analyses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/health")
def health_check():
    from datetime import datetime

    return {"status": "healthy", "version": "1.0.0", "timestamp": datetime.utcnow()}
