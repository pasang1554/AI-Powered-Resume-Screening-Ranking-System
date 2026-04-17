from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User, AuditLog
from backend.services.auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def log_action(db: Session, user_id: int, action: str, module: str, details: dict = None):
    audit = AuditLog(user_id=user_id, action=action, module=module, details=details)
    db.add(audit)
    db.commit()

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = decode_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token decode error: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Payload is None or Token is invalid/expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Subject (sub) missing from token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: User '{email}' not found in DB",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role: {user.role}. Required: {self.allowed_roles}"
            )
        return user
