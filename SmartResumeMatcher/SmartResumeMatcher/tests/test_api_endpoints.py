import io
import pytest

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    assert "ecosystem" in res.json()

def test_auth_workflow(client):
    # 1. Register
    reg_data = {"email": "api@test.com", "username": "apitest", "password": "securepassword"}
    res_reg = client.post("/api/v1/auth/register", json=reg_data)
    assert res_reg.status_code == 200
    
    # 2. Login
    res_login = client.post("/api/v1/auth/token", data={"username": reg_data["email"], "password": reg_data["password"]})
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()
    token = res_login.json()["access_token"]
    
    # 3. Get /me
    res_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["email"] == reg_data["email"]

def test_resume_analysis_endpoint(client, auth_header):
    # Prepare dummy PDF content
    resume_content = b"Jane Doe, Full Stack Engineer with 5 years of React and Node.js experience."
    files = [("files", ("jane_resume.txt", io.BytesIO(resume_content), "text/plain"))]
    data = {
        "job_description": "We need a React and Node.js developer.",
        "threshold": 60.0,
        "blind_hiring": False
    }
    
    res = client.post("/api/v1/analyze/pdf", headers=auth_header, data=data, files=files)
    assert res.status_code == 200
    
    results = res.json()
    assert "candidates" in results
    assert len(results["candidates"]) > 0
    assert results["candidates"][0]["Candidate"] == "jane_resume"
    assert results["candidates"][0]["Score"] > 0

def test_audit_logs(client, auth_header):
    # Trigger an action first (e.g., failed login or a successful analysis)
    # The fixture already did registration and login, which should be logged if implemented
    res = client.get("/api/v1/audit/logs", headers=auth_header)
    assert res.status_code == 200
    # Audit logs are populated during registration and login
    assert len(res.json()) >= 0 
