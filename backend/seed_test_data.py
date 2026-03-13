"""
Main seed script - Registers users, uploads resumes, posts jobs, submits applications
Run: python seed_test_data.py
Prerequisites: Backend running on localhost:8000, fpdf2 installed
"""
import requests
import os
import sys
import time

from seed_data import CANDIDATES, RECRUITERS, PASSWORD, BASE_URL
from seed_data2 import CANDIDATES_PART2, JOBS, APPLICATION_MAP
from pdf_generator import generate_resume_pdf

ALL_CANDIDATES = CANDIDATES + CANDIDATES_PART2
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated_resumes")


def register_user(user_data):
    """Register a user, skip if already exists"""
    payload = {
        "name": user_data["name"],
        "email": user_data["email"],
        "password": user_data.get("password", PASSWORD),
        "role": user_data["role"],
    }
    if user_data.get("company"):
        payload["company"] = user_data["company"]

    resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
    if resp.status_code == 200:
        return True, "registered"
    elif resp.status_code == 400 and "already" in resp.text.lower():
        return True, "exists"
    else:
        return False, resp.text


def login_user(email, password=PASSWORD):
    """Login and return JWT token"""
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if resp.status_code == 200:
        data = resp.json()
        return data.get("access_token") or data.get("token")
    return None


def upload_resume(token, pdf_path):
    """Upload resume PDF"""
    headers = {"Authorization": f"Bearer {token}"}
    with open(pdf_path, "rb") as f:
        files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
        resp = requests.post(f"{BASE_URL}/resumes/upload", headers=headers, files=files)
    return resp.status_code in (200, 201), resp.text[:200]


def create_job(token, job_data):
    """Create a job posting"""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "title": job_data["title"],
        "company": job_data["company"],
        "location": job_data["location"],
        "jobType": job_data["jobType"],
        "workplaceType": job_data["workplaceType"],
        "numberOfOpenings": job_data["numberOfOpenings"],
        "description": job_data["description"],
        "requiredSkills": job_data["requiredSkills"],
        "preferredSkills": job_data.get("preferredSkills", []),
        "minExperience": job_data["minExperience"],
        "maxExperience": job_data.get("maxExperience"),
        "educationLevel": job_data.get("educationLevel", "Bachelor's Degree"),
        "salaryMin": job_data.get("salaryMin"),
        "salaryMax": job_data.get("salaryMax"),
    }
    resp = requests.post(f"{BASE_URL}/jobs/create", headers=headers, json=payload)
    if resp.status_code in (200, 201):
        data = resp.json()
        return True, data.get("jobId") or data.get("job_id") or data.get("id")
    return False, resp.text[:200]


def get_all_jobs(token):
    """Get all open jobs"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/jobs/open", headers=headers)
    if resp.status_code == 200:
        return resp.json()
    # Try alternate endpoint
    resp = requests.get(f"{BASE_URL}/jobs/all", headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return []


def apply_to_job(token, job_id):
    """Apply to a specific job"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/applications/apply",
                         headers=headers, json={"jobId": job_id})
    if resp.status_code in (200, 201):
        data = resp.json()
        score = data.get("snapshotMatchScore", "?")
        return True, score
    elif resp.status_code == 409:
        return True, "already applied"
    return False, resp.text[:150]


def main():
    print("=" * 60)
    print("  CONNECT TALENT AI - TEST DATA SEEDER")
    print("=" * 60)

    # Check backend is running
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code != 200:
            print(f"\n[ERROR] Backend not responding at {BASE_URL}")
            sys.exit(1)
        print(f"\n[OK] Backend is running at {BASE_URL}")
    except:
        print(f"\n[ERROR] Cannot connect to {BASE_URL}. Is the backend running?")
        sys.exit(1)

    # ==================== PHASE 1: Generate PDFs ====================
    print(f"\n{'='*60}")
    print("  PHASE 1: Generating {0} PDF Resumes".format(len(ALL_CANDIDATES)))
    print(f"{'='*60}")

    pdf_paths = {}
    for i, c in enumerate(ALL_CANDIDATES, 1):
        c_with_role = {**c, "role": "CANDIDATE", "password": PASSWORD}
        try:
            path = generate_resume_pdf(c, OUTPUT_DIR)
            pdf_paths[c["email"]] = path
            print(f"  [{i:2d}/25] PDF generated: {c['name']}")
        except Exception as e:
            print(f"  [{i:2d}/25] FAILED: {c['name']} - {e}")

    # ==================== PHASE 2: Register Recruiters & Post Jobs ====================
    print(f"\n{'='*60}")
    print("  PHASE 2: Registering Recruiters & Posting Jobs")
    print(f"{'='*60}")

    recruiter_tokens = {}
    for r in RECRUITERS:
        ok, msg = register_user(r)
        status = "OK" if ok else "FAIL"
        print(f"  Register {r['name']:20s} [{status}] ({msg})")
        token = login_user(r["email"])
        if token:
            recruiter_tokens[r["email"]] = token
            print(f"  Login   {r['name']:20s} [OK]")
        else:
            print(f"  Login   {r['name']:20s} [FAIL]")

    # Post jobs
    job_ids = []
    for i, job in enumerate(JOBS, 1):
        rec_email = job["recruiter_email"]
        token = recruiter_tokens.get(rec_email)
        if not token:
            print(f"  Job {i:2d}: SKIP (no recruiter token for {rec_email})")
            job_ids.append(None)
            continue
        ok, job_id = create_job(token, job)
        if ok:
            job_ids.append(job_id)
            print(f"  Job {i:2d}: {job['title']:35s} [{job['company']:12s}] [OK] ID={job_id}")
        else:
            job_ids.append(None)
            print(f"  Job {i:2d}: {job['title']:35s} [FAIL] {job_id}")

    # ==================== PHASE 3: Register Candidates & Upload Resumes ====================
    print(f"\n{'='*60}")
    print("  PHASE 3: Registering Candidates & Uploading Resumes")
    print(f"{'='*60}")

    candidate_tokens = {}
    for i, c in enumerate(ALL_CANDIDATES, 1):
        user_data = {"name": c["name"], "email": c["email"], "password": PASSWORD, "role": "CANDIDATE"}
        ok, msg = register_user(user_data)
        token = login_user(c["email"])
        if token:
            candidate_tokens[c["email"]] = token
        status = "OK" if ok else "FAIL"
        print(f"  [{i:2d}/25] Register {c['name']:20s} [{status}]", end="")

        # Upload resume
        pdf_path = pdf_paths.get(c["email"])
        if pdf_path and token:
            ok, rmsg = upload_resume(token, pdf_path)
            rstatus = "OK" if ok else "FAIL"
            print(f"  | Resume [{rstatus}]")
        else:
            print(f"  | Resume [SKIP]")
        time.sleep(0.3)  # Small delay to not overwhelm API

    # ==================== PHASE 4: Submit Applications ====================
    print(f"\n{'='*60}")
    print("  PHASE 4: Submitting Applications (3 per candidate)")
    print(f"{'='*60}")

    total_apps = 0
    total_ok = 0

    for email, job_indices in APPLICATION_MAP.items():
        token = candidate_tokens.get(email)
        if not token:
            print(f"  {email:35s} [SKIP - no token]")
            continue

        name = next((c["name"] for c in ALL_CANDIDATES if c["email"] == email), email)
        results = []
        for idx in job_indices:
            job_idx = idx - 1  # Convert 1-indexed to 0-indexed
            if job_idx < len(job_ids) and job_ids[job_idx]:
                ok, score = apply_to_job(token, job_ids[job_idx])
                total_apps += 1
                if ok:
                    total_ok += 1
                label = JOBS[job_idx]["title"][:20]
                results.append(f"{label}={score}")
            time.sleep(0.2)

        print(f"  {name:20s} -> {' | '.join(results)}")

    # ==================== SUMMARY ====================
    print(f"\n{'='*60}")
    print("  SEEDING COMPLETE!")
    print(f"{'='*60}")
    print(f"  PDFs Generated:    {len(pdf_paths)}/25")
    print(f"  Recruiters:        {len(recruiter_tokens)}/3")
    print(f"  Jobs Created:      {sum(1 for j in job_ids if j)}/10")
    print(f"  Candidates:        {len(candidate_tokens)}/25")
    print(f"  Applications:      {total_ok}/{total_apps}")
    print(f"\n  Resumes saved to: {OUTPUT_DIR}")

    # ==================== CREDENTIALS ====================
    print(f"\n{'='*60}")
    print("  CREDENTIALS (Password for ALL: Test@123)")
    print(f"{'='*60}")
    print(f"\n  RECRUITERS:")
    for r in RECRUITERS:
        print(f"    {r['email']:30s}  ({r['name']} - {r['company']})")
    print(f"\n  CANDIDATES (showing first 5 + last 3):")
    show = ALL_CANDIDATES[:5] + ALL_CANDIDATES[-3:]
    for c in show:
        exp = c.get("exp")
        exp_str = exp[0]["dates"] if exp else "Fresher"
        print(f"    {c['email']:35s}  ({c['name']} - {c['domain']} - {exp_str})")
    print(f"\n    ... and {len(ALL_CANDIDATES) - 8} more candidates")
    print(f"\n  FULL LIST: see seed_data.py and seed_data2.py")


if __name__ == "__main__":
    main()
