import requests
import io
import time

API_URL = "http://localhost:8000/api/v1"
res = requests.post(f"{API_URL}/register", json={"email": "s-test@test.com", "username": "s-test", "password": "abc"})
res = requests.post(f"{API_URL}/token", data={"username": "s-test@test.com", "password": "abc"})
token = res.json()["access_token"]
print("Streamlit Token:", token)

headers = {"Authorization": f"Bearer {token}"}
res = requests.get(f"{API_URL}/analyses", headers=headers)
print("Analyses GET via requests:", res.status_code)

files_payload = [("files", ("test.txt", io.BytesIO(b"dummy text"), "text/plain"))]
data = {"job_description": "dummy jd", "threshold": 50.0}
res = requests.post(f"{API_URL}/analyze/pdf", data=data, files=files_payload, headers=headers)
print("Analyze POST via requests:", res.status_code, res.text)
