from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class JobDescriptionBase(BaseModel):
    title: str
    content: str
    required_skills: Optional[List[str]] = []
    threshold: Optional[float] = 65.0


class JobDescriptionCreate(JobDescriptionBase):
    pass


class JobDescriptionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    required_skills: Optional[List[str]] = None
    threshold: Optional[float] = None


class JobDescriptionResponse(JobDescriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateBase(BaseModel):
    name: str
    email: Optional[str] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: int
    job_description_id: int
    resume_filename: Optional[str] = None
    skills: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisBase(BaseModel):
    match_score: float
    semantic_similarity: float
    skill_depth: float
    missing_skills: List[str] = []
    matched_skills: List[str] = []
    bias_indicators: List[str] = []
    status: str
    ai_evaluation: Optional[Dict[str, Any]] = None


class AnalysisCreate(AnalysisBase):
    job_description_id: int
    candidate_id: int


class AnalysisResponse(AnalysisBase):
    id: int
    user_id: int
    job_description_id: int
    candidate_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateWithAnalysis(CandidateResponse):
    analysis: Optional[AnalysisResponse] = None


class AnalysisRequest(BaseModel):
    job_description: str
    threshold: Optional[float] = 65.0


class AnalysisResult(BaseModel):
    candidates: List[Dict[str, Any]]
    summary: Dict[str, Any]
    job_description_id: int


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
