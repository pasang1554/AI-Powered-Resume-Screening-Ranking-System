from fastapi import APIRouter, Depends, HTTPException, Response, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.models import User, Interview
from backend.schemas import InterviewCreate, InterviewResponse
from backend.routes.dependencies import get_current_user, log_action

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("", response_model=InterviewResponse)
async def schedule_interview(
    interview: InterviewCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_interview = Interview(**interview.model_dump())
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    
    log_action(db, current_user.id, f"Scheduled Interview for Candidate {interview.candidate_id}", "Interview")
    return db_interview

@router.get("", response_model=List[InterviewResponse])
async def list_interviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Interview).all()

@router.patch("/{interview_id}/feedback", response_model=InterviewResponse)
async def update_interview_feedback(
    interview_id: int,
    notes: Optional[str] = Form(None),
    interviewer_score: Optional[float] = Form(None),
    feedback_summary: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    if notes is not None: interview.notes = notes
    if interviewer_score is not None: interview.interviewer_score = interviewer_score
    if feedback_summary is not None: interview.feedback_summary = feedback_summary
    if status is not None: interview.status = status
    
    db.commit()
    db.refresh(interview)
    
    log_action(db, current_user.id, f"Recorded feedback for Interview {interview_id}", "Interview", {"score": interviewer_score, "status": status})
    return interview

@router.get("/{interview_id}/ics")
async def export_interview_ics(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from utils import generate_ics_content
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    cand = interview.candidate
    jd = cand.job_description
    
    ics_text = generate_ics_content(
        cand.name, 
        jd.title, 
        interview.interview_date, 
        interview.medium, 
        current_user.email
    )
    
    return Response(
        content=ics_text,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=interview_{cand.name.replace(' ', '_')}.ics"}
    )
