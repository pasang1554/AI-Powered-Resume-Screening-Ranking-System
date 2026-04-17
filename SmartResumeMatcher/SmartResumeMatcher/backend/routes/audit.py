from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User, AuditLog
from backend.routes.dependencies import get_current_user

router = APIRouter(prefix="/audit", tags=["Compliance & Audit"])

@router.get("/logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves system-wide audit logs for the current user for compliance monitoring.
    """
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
        .all()
    )

@router.post("/reset")
async def reset_database(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Administrative utility to wipe development/demo data.
    """
    from backend.models import Analysis, JobDescription, Interview
    try:
        db.query(Analysis).filter(Analysis.user_id == current_user.id).delete()
        db.query(JobDescription).filter(JobDescription.user_id == current_user.id).delete()
        db.query(Interview).delete() 
        db.commit()
        log_action(db, current_user.id, "Full Database Reset", "System")
        return {"message": "All recruitment intelligence wiped securely"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
