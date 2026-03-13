import requests
import os
from pdf_generator import generate_resume_pdf

BASE_URL = "http://localhost:8000"
PASSWORD = "Test@123"

def test_diag():
    # 1. Candidate data
    candidate = {
        "name": "Diag User",
        "email": "diag@test.com",
        "phone": "1234567890",
        "skills": ["Python", "JavaScript"],
        "exp": [],
        "edu": {"degree": "B.Tech", "univ": "Test Univ", "year": "2024", "cgpa": "9.0"},
        "summary": "This is a diagnostic test candidate.",
        "format": "A"
    }
    
    # 2. Generate real PDF
    print("Generating PDF...")
    pdf_path = generate_resume_pdf(candidate, "diag_resumes")
    print(f"PDF generated: {pdf_path}")

    # 3. Register
    payload = {"name": "Diag User", "email": "diag@test.com", "role": "CANDIDATE", "password": PASSWORD}
    r = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print(f"Register: {r.status_code}") # 200 if OK, 400 if exists

    # 4. Login
    r = requests.post(f"{BASE_URL}/auth/login", json={"email": "diag@test.com", "password": PASSWORD})
    print(f"Login: {r.status_code}")
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 5. Upload
    print("Uploading resume...")
    with open(pdf_path, "rb") as f:
        files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
        r = requests.post(f"{BASE_URL}/resumes/upload", headers=headers, files=files)
    print(f"Upload: {r.status_code} {r.text[:500]}")

    # 6. Check DB
    if r.status_code == 200:
        print("\nChecking DB...")
        os.system("python -c \"from app.db.mongo import get_db; db=get_db(); u=db.users.find_one({'email':'diag@test.com'}); uid=str(u['_id']); print('User UID:', uid); r=db.resumes.find_one({'candidateId':uid}); print('Resume in DB:', bool(r))\"")

if __name__ == "__main__":
    test_diag()
