from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import engine, Base
from backend.services.logging_service import api_logger

# Import Modular Routers
from backend.routes import (
    auth, 
    job_descriptions, 
    analysis, 
    candidates, 
    interviews, 
    analytics, 
    public, 
    audit
)

api_logger.info("Starting Smart Resume Matcher - Modular Enterprise API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Smart Resume Matcher API",
    description="Enterprise-grade AI-Powered Recruitment Intelligence Ecosystem",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base API Prefix
PREFIX = "/api/v1"

# Mount Domain Routers
app.include_router(auth.router, prefix=PREFIX)
app.include_router(job_descriptions.router, prefix=PREFIX)
app.include_router(analysis.router, prefix=PREFIX)
app.include_router(candidates.router, prefix=PREFIX)
app.include_router(interviews.router, prefix=PREFIX)
app.include_router(analytics.router, prefix=PREFIX)
app.include_router(public.router, prefix=PREFIX)
app.include_router(audit.router, prefix=PREFIX)

@app.get("/")
def root():
    return {
        "message": "Institutional Talent Singularity API", 
        "docs": "/docs", 
        "version": "1.1.0",
        "status": "Operational"
    }

@app.get("/health")
def health():
    from datetime import datetime
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "ecosystem": "Universal Singularity"
    }
