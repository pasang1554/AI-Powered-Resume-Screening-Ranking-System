import requests
import io

API_URL = "http://localhost:8000/api/v1"
res = requests.post(f"{API_URL}/register", json={"email": "s-test22@test.com", "username": "s-test22", "password": "abc"})
res = requests.post(f"{API_URL}/token", data={"username": "s-test22@test.com", "password": "abc"})
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Analyze using the EXACT payload that demo gives
SAMPLE_JD = "SOFTWARE ENGINEER\nLocation: Bangalore"
files_payload = []
b = io.BytesIO("Dummy resume text".encode('utf-8'))
files_payload.append(("files", ("John.txt", b, "text/plain")))

data = {"job_description": SAMPLE_JD, "threshold": 50.0, "groq_api_key": None}

res = requests.post(f"{API_URL}/analyze/pdf", data=data, files=files_payload, headers=headers)
print("Analyze HTTP Status:", res.status_code)
print("Analyze Output:", res.text)
