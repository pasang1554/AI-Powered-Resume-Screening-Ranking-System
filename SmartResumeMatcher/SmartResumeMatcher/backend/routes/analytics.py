from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
from collections import Counter

from backend.database import get_db
from backend.models import User, JobDescription, Analysis, Candidate, Interview
from backend.schemas import AnalysisResponse, AnalysisStatusUpdate
from backend.routes.dependencies import get_current_user, log_action

router = APIRouter(prefix="/analytics", tags=["Talent Singularity & Analytics"])

@router.get("/list", response_model=List[dict])
def list_analyses(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    min_score: float = None,
    candidate_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    if status: query = query.filter(Analysis.status == status)
    if min_score is not None: query = query.filter(Analysis.match_score >= min_score)
    if candidate_id: query = query.filter(Analysis.candidate_id == candidate_id)
        
    analyses = query.order_by(Analysis.created_at.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": a.id,
        "job_description_id": a.job_description_id,
        "candidate_id": a.candidate_id,
        "candidate_name": a.candidate.name if a.candidate else "Unknown Candidate",
        "match_score": a.match_score,
        "status": a.status,
        "created_at": a.created_at
    } for a in analyses]

@router.get("/skills")
def get_skill_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidates = db.query(Candidate).all()
    all_skills = []
    for c in candidates:
        if c.skills: all_skills.extend(c.skills)
    return Counter(all_skills)

@router.post("/project/{jd_id}/synthesis")
async def get_talent_synthesis(
    jd_id: int,
    groq_api_key: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from groq import Groq
    jd = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    if not jd: raise HTTPException(status_code=404, detail="Job description not found")
        
    top_analyses = db.query(Analysis).filter(Analysis.job_description_id == jd_id, Analysis.match_score >= 80).limit(5).all()
    if not top_analyses: return {"synthesis": "Strategic AI Insight: Not enough top-tier candidates to generate a high-fidelity synthesis yet."}
        
    candidate_summaries = "\n".join([f"- {a.candidate.name}: {', '.join(a.matched_skills)}" for a in top_analyses])
    prompt = f"Analyze candidates against JD: {jd.title}. Candidates: {candidate_summaries}. Synthesize the 'Ideal Candidate Profile' and suggest 3 JD improvements."
    
    try:
        client = Groq(api_key=groq_api_key)
        response = await asyncio.to_thread(client.chat.completions.create,
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return {"synthesis": response.choices[0].message.content}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# --- Singularity Legacy Endpoints (Mocked for v8.1 demo) ---

@router.get("/quantum-simulator")
async def get_quantum_simulator(
    current_user: User = Depends(get_current_user)
):
    return {
        "horizon": "5 Years",
        "velocity_impact": "+24% R&D Speed predicted by Year 3",
        "financial_roi": "$4.5M NPV from mobility optimization",
        "simulation_confidence": "98.4%"
    }

@router.get("/succession-regent/{jd_id}")
async def get_succession_regent(
    jd_id: int,
    current_user: User = Depends(get_current_user)
):
    return {
        "jd_id": jd_id,
        "succession_strength": "Robust (92%)",
        "primary_successor": "Candidate #452 (Internal)",
        "regent_action": "Nomination finalized. Training modules dispatched."
    }

@router.get("/market-scarcity")
async def get_market_scarcity_benchmarking(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    SCARCITY_MARKERS = ["Rust", "Golang", "Kubernetes", "Machine Learning", "PyTorch", "Terraform"]
    candidates = db.query(Candidate).all()
    all_skills = [s for c in candidates if c.skills for s in c.skills]
    counts = Counter(all_skills)
    total_talent = len(candidates)
    
    return sorted([
        {
            "skill": skill,
            "vault_count": counts.get(skill, 0),
            "scarcity_index": round(min(100, 100 - (counts.get(skill, 0) / (total_talent or 1) * 100)), 1)
        } for skill in SCARCITY_MARKERS
    ], key=lambda x: x["scarcity_index"], reverse=True)

@router.patch("/status/{analysis_id}", response_model=AnalysisResponse)
def update_analysis_status(
    analysis_id: int,
    status_update: AnalysisStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis: raise HTTPException(status_code=404, detail="Analysis record not found")
    analysis.status = status_update.status
    db.commit()
    db.refresh(analysis)
    log_action(db, current_user.id, f"Updated status for Analysis {analysis_id} to {status_update.status}", "Pipeline")
    return analysis

@router.get("/culture-radar/{candidate_id}")
async def get_cultural_alignment(candidate_id: int):
    import random
    categories = ["Innovation", "Collaboration", "Integrity", "Excellence", "Agility"]
    return {
        "candidate_id": candidate_id,
        "categories": categories,
        "candidate_vector": [random.randint(70, 100) for _ in categories],
        "company_vector": [85, 90, 95, 80, 88],
        "alignment_index": random.randint(85, 98)
    }

@router.get("/roi")
async def get_recruitment_roi():
    return {
        "total_time_saved_hours": 1240,
        "estimated_cost_savings_usd": 45000,
        "roi_multiple": "4.2x"
    }

@router.post("/notify")
async def notify_candidate(
    candidate_name: str = Form(...),
    score: float = Form(...),
    role: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    # Simulated notification node
    return {
        "status": "success", 
        "message": f"Strategic invitation dispatched to {candidate_name}",
        "timestamp": datetime.utcnow()
    }

@router.post("/hris-sync")
async def simulate_hris_sync(system_name: str = Form("Workday")):
    return {
        "target_system": system_name,
        "sync_status": "Successful",
        "records_synchronized": 452,
        "last_sync": datetime.utcnow().isoformat(),
        "api_gateway": "Unified Talent Nervous System v1.1"
    }

@router.get("/cognitive-nudges/{candidate_id}")
async def get_cognitive_nudges(candidate_id: int):
    return {
        "candidate_id": candidate_id,
        "suggested_nudges": [
            {"topic": "Scalability", "nudges": "Ask about cross-shard consistency frameworks."},
            {"topic": "Leadership", "nudges": "Explore their conflict resolution style in decentralized teams."}
        ]
    }

@router.get("/workforce-roadmap")
async def get_workforce_roadmap():
    return {
        "horizon": "24 Months",
        "predicted_gaps": [{"skill": "AI Safety", "urgency": "High", "time_to_need": "8 Months"}],
        "hiring_roadmap": "Initiate Q3 Leadership Search for 'Talent Ethics' lead."
    }

@router.get("/multiverse-strategy")
async def get_multiverse_strategy():
    return {
        "simulated_timelines": 1024,
        "optimal_path": "Aggressive APAC Skill Ingestion -> Global Sovereignty",
        "strategy_confidence": "99.98%"
    }

@router.get("/singularity-governance")
async def get_singularity_governance():
    return {
        "ethical_alignment": "Perfect (100%)",
        "destiny_status": "LOCKED - On Path to North Star",
        "heartbeat": "Eternal"
    }
