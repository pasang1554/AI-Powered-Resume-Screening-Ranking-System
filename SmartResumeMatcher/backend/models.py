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
    skills = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    job_description = relationship("JobDescription", back_populates="candidates")
    analysis = relationship("Analysis", back_populates="candidate", uselist=False)


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))

    match_score = Column(Float)
    semantic_similarity = Column(Float)
    skill_depth = Column(Float)
    missing_skills = Column(JSON, default=list)
    matched_skills = Column(JSON, default=list)
    bias_indicators = Column(JSON, default=list)
    status = Column(String(50))
    ai_evaluation = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")
    job_description = relationship("JobDescription", back_populates="analyses")
    candidate = relationship("Candidate", back_populates="analysis")
