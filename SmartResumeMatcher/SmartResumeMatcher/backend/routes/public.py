from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import io

from backend.database import get_db
from backend.models import JobDescription, Candidate, Analysis
from backend.routes.dependencies import log_action

router = APIRouter(prefix="/public", tags=["Public Gateway"])

@router.get("/jobs")
def list_public_jobs(db: Session = Depends(get_db)):
    """
    Returns open job postings for external candidates.
    """
    return db.query(JobDescription).filter(JobDescription.is_archived == False).all()

@router.post("/apply/{jd_id}")
async def public_application_gateway(
    jd_id: int,
    file: UploadFile = File(...),
    email: str = Form(...),
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Candidate self-application gateway.
    Analyzes resume and injects directly into the recruitment pipeline.
    """
    from backend.services.analysis import analyze_resume
    from utils import extract_text_from_pdf
    
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job posting not found")
        
    contents = await file.read()
    if file.filename.lower().endswith(".pdf"):
        text_content = extract_text_from_pdf(io.BytesIO(contents))
    else:
        text_content = contents.decode("utf-8", errors="ignore")
        
    if not text_content:
        raise HTTPException(status_code=400, detail="Could not extract text from resume")

    # Perform analysis
    analysis_res = analyze_resume(jd.content, text_content)
    
    # Check for existing candidate
    existing_cand = db.query(Candidate).filter(Candidate.email == email).first()
    if existing_cand:
        cand = existing_cand
    else:
        cand = Candidate(
            job_description_id=jd_id,
            name=name,
            email=email,
            resume_text=text_content,
            resume_filename=file.filename,
            resume_data=contents,
            skills=analysis_res["matched_skills"]
        )
        db.add(cand)
        db.commit()
        db.refresh(cand)
        
    # Auto-log this public action
    log_action(db, jd.user_id, f"Public Application: {name}", "PublicGateway", {"jd_id": jd_id})
    
    analysis = Analysis(
        user_id=jd.user_id,
        job_description_id=jd_id,
        candidate_id=cand.id,
        match_score=analysis_res["match_score"],
        semantic_similarity=analysis_res["semantic_similarity"],
        skill_depth=analysis_res["skill_depth"],
        matched_skills=analysis_res["matched_skills"],
        missing_skills=analysis_res["missing_skills"],
        status=analysis_res["status"],
        ai_evaluation={"summary": "Public submission via neural gateway."}
    )
    db.add(analysis)
    db.commit()
    
    return {
        "status": "Application Received", 
        "match_score": analysis_res["match_score"],
        "assigned_id": analysis.id
    }
