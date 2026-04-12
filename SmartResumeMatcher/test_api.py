from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

res = client.post("/api/v1/register", json={"email": "test99@example.com", "username": "test99", "password": "abc"})
print("Register:", res.status_code)

res = client.post("/api/v1/token", data={"username": "test99@example.com", "password": "abc"})
print("Token:", res.status_code, res.json())
token = res.json()["access_token"]

res = client.get("/api/v1/analyses", headers={"Authorization": f"Bearer {token}"})
print("Analyses GET:", res.status_code)

import io
files = [("files", ("test.txt", io.BytesIO(b"John Doe, Senior Software Engineer with 10 years of experience in Python, FastAPI, and SQLAlchemy. Expert in building scalable backends and AI-powered intelligence systems using Large Language Models like Llama 3."), "text/plain"))]
data = {"job_description": "some dummy jd here", "threshold": 50.0}

res = client.post("/api/v1/analyze/pdf", headers={"Authorization": f"Bearer {token}"}, data=data, files=files)
print("Analyze POST:", res.status_code, res.text)
