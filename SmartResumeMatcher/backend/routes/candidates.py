from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User, Candidate
from backend.schemas import CandidateResponse
from backend.routes.dependencies import get_current_user

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.get("/vault")
def get_talent_vault(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns all candidates across all projects for cross-referenced talent pooling.
    """
    return db.query(Candidate).all()

@router.get("/{candidate_id}/resume")
def download_resume(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if not candidate.resume_data:
        raise HTTPException(status_code=404, detail="Resume file not found in database")
        
    media_type = "application/pdf" if candidate.resume_filename.lower().endswith(".pdf") else "text/plain"
    
    return Response(
        content=candidate.resume_data,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{candidate.resume_filename}"'
        }
    )
