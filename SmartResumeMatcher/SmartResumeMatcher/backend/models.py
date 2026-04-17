from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    JSON,
    LargeBinary,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="Admin") # Admin, Recruiter, Interviewer
    created_at = Column(DateTime, default=datetime.utcnow)

    job_descriptions = relationship("JobDescription", back_populates="owner")
    analyses = relationship("Analysis", back_populates="user")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    content = Column(Text)
    required_skills = Column(JSON, default=list)
    threshold = Column(Float, default=65.0)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="job_descriptions")
    candidates = relationship("Candidate", back_populates="job_description")
    analyses = relationship("Analysis", back_populates="job_description")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"))
    name = Column(String(255))
    email = Column(String(255))
    resume_text = Column(Text)
    resume_filename = Column(String(255))
    resume_data = Column(LargeBinary, nullable=True)
    skills = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    job_description = relationship("JobDescription", back_populates="candidates")
    analysis = relationship("Analysis", back_populates="candidate", uselist=False)
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))

    match_score = Column(Float)
    ats_score = Column(Float, nullable=True)
    experience_years = Column(Float, nullable=True)
    semantic_similarity = Column(Float)
    skill_depth = Column(Float)
    missing_skills = Column(JSON, default=list)
    matched_skills = Column(JSON, default=list)
    skills_found = Column(JSON, default=list)
    bias_indicators = Column(JSON, default=list)
    status = Column(String(50))
    ai_evaluation = Column(JSON, nullable=True)
    radar_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")
    job_description = relationship("JobDescription", back_populates="analyses")
    candidate = relationship("Candidate", back_populates="analysis")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    interview_date = Column(DateTime)
    medium = Column(String(100))
    notes = Column(Text, nullable=True)
    interviewer_score = Column(Float, nullable=True)
    feedback_summary = Column(Text, nullable=True)
    status = Column(String(50), default="Scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="interviews")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255))
    module = Column(String(100))
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
