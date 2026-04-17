import pytest
from backend.models import Analysis, Candidate, JobDescription

def test_intelligence_report_export(client, auth_header, db):
    # 1. Setup mock analysis with AI evaluation
    jd = JobDescription(title="Manager", content="Need a manager", user_id=1)
    db.add(jd)
    db.commit()
    
    cand = Candidate(name="John Report", job_description_id=jd.id)
    db.add(cand)
    db.commit()
    
    analysis = Analysis(
        user_id=1,
        job_description_id=jd.id,
        candidate_id=cand.id,
        match_score=85.0,
        status="Shortlisted",
        ai_evaluation={
            "summary": "Excellent leadership potential.",
            "strengths": ["Strategic thinking", "Team management"],
            "weaknesses": ["None"],
            "recommendation": "Ready to Hire",
            "hiring_status": "Ready to Hire"
        }
    )
    db.add(analysis)
    db.commit()
    
    # 2. Test Export Endpoint
    res = client.get(f"/api/v1/analyze/export/{analysis.id}", headers=auth_header)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000 # Basic check for non-empty PDF
