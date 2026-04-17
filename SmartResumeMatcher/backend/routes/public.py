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
        
    # Check for Groq API Key in environment
    import os
    from groq import Groq
    from utils import evaluate_resume_with_groq, redact_pii
    
    server_api_key = os.getenv("GROQ_API_KEY")
    client = None
    if server_api_key:
        try: client = Groq(api_key=server_api_key)
        except: pass

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded. Please provide a valid resume artifact.")

    if file.filename.lower().endswith(".pdf"):
        try:
            text_content = extract_text_from_pdf(io.BytesIO(contents))
        except:
            raise HTTPException(status_code=400, detail="Could not parse PDF. Secure neural core reports corruption.")
    else:
        text_content = contents.decode("utf-8", errors="ignore")
        
    if not text_content or len(text_content.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume content insufficient for neural mapping. Please provide a more detailed artifact.")

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
    
    # Run Deep AI evaluation if client exists
    ai_eval = {"summary": "Public submission via neural gateway."}
    if client:
        try:
            # We use blind hiring redaction as a safeguard for public applications
            redacted_text = redact_pii(text_content)
            ai_eval = evaluate_resume_with_groq(client, jd.content, redacted_text[:8000])
        except:
            pass

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
        ai_evaluation=ai_eval
    )
    db.add(analysis)
    db.commit()
    
    return {
        "status": "Application Received", 
        "match_score": round(analysis_res["match_score"], 1),
        "assigned_id": analysis.id
    }
