from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User, JobDescription, Analysis
from backend.schemas import JobDescriptionCreate, JobDescriptionResponse
from backend.routes.dependencies import get_current_user

router = APIRouter(prefix="/job-descriptions", tags=["Job Descriptions"])

@router.post("", response_model=JobDescriptionResponse)
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

@router.get("", response_model=List[JobDescriptionResponse])
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

@router.get("/{jd_id}", response_model=JobDescriptionResponse)
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

@router.get("/{jd_id}/analyses")
def get_job_description_analyses(
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

    analyses = db.query(Analysis).filter(Analysis.job_description_id == jd_id).all()
    results = []
    for a in analyses:
        results.append({
            "id": a.id,
            "candidate_id": a.candidate_id,
            "candidate_name": a.candidate.name,
            "match_score": a.match_score,
            "ats_score": a.ats_score,
            "experience_years": a.experience_years,
            "status": a.status,
            "skills_found": a.skills_found,
            "missing_skills_count": len(a.missing_skills),
            "missing_skills": a.missing_skills,
            "ai_evaluation": a.ai_evaluation,
            "radar_data": a.radar_data,
            "resume_filename": a.candidate.resume_filename,
            "resume_text": a.candidate.resume_text,
            "created_at": a.created_at
        })
    return results

@router.delete("/{jd_id}")
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

@router.post("/{jd_id}/archive")
def archive_job_description(
    jd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.user_id == current_user.id).first()
    if not jd: raise HTTPException(status_code=404, detail="Project not found")
    jd.is_archived = not jd.is_archived
    db.commit()
    status = "archived" if jd.is_archived else "restored"
    return {"message": f"Project successfully {status}"}

@router.get("/{jd_id}/export")
def export_job_description_csv(
    jd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import csv
    import io
    from fastapi.responses import StreamingResponse

    jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.user_id == current_user.id).first()
    if not jd: raise HTTPException(status_code=404, detail="Project not found")

    analyses = db.query(Analysis).filter(Analysis.job_description_id == jd_id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Candidate Name", "Match Score", "ATS Score", "Experience", "Status", "Top Skills"])
    
    for a in analyses:
        writer.writerow([
            a.candidate.name,
            a.match_score,
            a.ats_score,
            a.experience_years,
            a.status,
            ", ".join(a.matched_skills[:5])
        ])
    
    output.seek(0)
    filename = f"export_{jd.title.replace(' ', '_')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
