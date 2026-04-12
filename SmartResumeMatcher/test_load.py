import requests
import io
API_URL = "http://localhost:8000/api/v1"
res = requests.post(f"{API_URL}/register", json={"email": "load@test.com", "username": "load", "password": "abc"})
res = requests.post(f"{API_URL}/token", data={"username": "load@test.com", "password": "abc"})
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
SAMPLE_JD = "SOFTWARE ENGINEER\nLocation: Bangalore"
files_payload = []
b = io.BytesIO("Dummy resume text".encode('utf-8'))
for i in range(50):
    files_payload = [("files", ("John.txt", io.BytesIO("Dummy resume text".encode('utf-8')), "text/plain"))]
    data = {"job_description": SAMPLE_JD, "threshold": 50.0}
    res = requests.post(f"{API_URL}/analyze/pdf", data=data, files=files_payload, headers=headers)
    if res.status_code != 200:
        print("FAILED ON", i, res.status_code, res.text)
        break
else:
    print("ALL PASSED")
