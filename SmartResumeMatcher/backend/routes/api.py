from fastapi import APIRouter, Depends, HTTPException, status
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
    job_description: str,
    threshold: float = 65.0,
    files: List = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from PyPDF2 import PdfReader
    from io import BytesIO

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

    return {
        "job_description_id": jd.id,
        "candidates": results,
        "summary": generate_summary(results),
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
