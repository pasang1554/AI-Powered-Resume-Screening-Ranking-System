import pytest
from datetime import datetime, timedelta

def test_interview_cycle(client, auth_header, db):
    # 1. Create a candidate first (need for Foreign Key)
    from backend.models import Candidate, JobDescription
    jd = JobDescription(title="Test JD", content="Test", user_id=1)
    db.add(jd)
    db.commit()
    
    cand = Candidate(name="Test Candidate", job_description_id=jd.id)
    db.add(cand)
    db.commit()
    
    # 2. Schedule Interview
    iv_data = {
        "candidate_id": cand.id,
        "interview_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "medium": "Zoom",
        "notes": "Test notes"
    }
    res = client.post("/api/v1/interviews", headers=auth_header, json=iv_data)
    assert res.status_code == 200
    iv_id = res.json()["id"]
    
    # 3. List Interviews
    res_list = client.get("/api/v1/interviews", headers=auth_header)
    assert res_list.status_code == 200
    assert any(i["id"] == iv_id for i in res_list.json())
    
    # 4. Record Feedback
    fb_data = {
        "interviewer_score": 8.5,
        "feedback_summary": "Great candidate",
        "status": "Completed"
    }
    # Backend uses Form data for this endpoint
    res_fb = client.patch(f"/api/v1/interviews/{iv_id}/feedback", headers=auth_header, data=fb_data)
    assert res_fb.status_code == 200
    assert res_fb.json()["interviewer_score"] == 8.5
    
    # 5. Export ICS
    res_ics = client.get(f"/api/v1/interviews/{iv_id}/ics", headers=auth_header)
    assert res_ics.status_code == 200
    assert "BEGIN:VCALENDAR" in res_ics.text
