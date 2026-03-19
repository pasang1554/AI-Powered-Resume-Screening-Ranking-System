from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import engine, Base
from backend.routes.api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Smart Resume Matcher API",
    description="AI-Powered Resume Screening & Ranking System - Production API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1", tags=["Resume Matcher"])


@app.get("/")
def root():
    return {"message": "Smart Resume Matcher API", "docs": "/docs", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
