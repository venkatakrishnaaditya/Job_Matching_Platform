import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Login as candidate (use an existing candidate account)
login_data = {
    "email": "student@test.com",  # Replace with actual candidate email
    "password": "password123"
}

print("1. Logging in as candidate...")
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✓ Logged in successfully")
    headers = {"Authorization": f"Bearer {token}"}
else:
    print(f"✗ Login failed: {response.text}")
    exit()

# Get an open job
print("\n2. Getting open jobs...")
response = requests.get(f"{BASE_URL}/jobs/browse", headers=headers)
if response.status_code == 200:
    jobs = response.json()
    open_job = next((j for j in jobs if j.get("status") == "Open"), None)
    if open_job:
        job_id = open_job["_id"]
        print(f"✓ Found open job: {job_id}")
    else:
        print("✗ No open jobs found")
        exit()
else:
    print(f"✗ Failed to get jobs: {response.text}")
    exit()

# Apply to the job
print("\n3. Applying to job...")
apply_data = {"jobId": job_id}
response = requests.post(f"{BASE_URL}/applications/apply", json=apply_data, headers=headers)

if response.status_code == 201:
    application = response.json()
    print(f"✓ Application successful!")
    print(f"\nApplication Details:")
    print(f"  ID: {application['_id']}")
    print(f"  Match Score: {application['snapshotMatchScore']:.2f}%")
    print(f"  Status: {application['status']}")
    
    # Check resume files
    print(f"\nResume Files:")
    resume_files = application.get('resumeFiles', {})
    print(f"  File URL: {resume_files.get('resumeFileUrl', 'Not found')}")
    print(f"  Download URL: {resume_files.get('resumeDownloadUrl', 'Not found')}")
    print(f"  Preview URL: {resume_files.get('resumePreviewUrl', 'Not found')}")
    
    if resume_files.get('resumeFileUrl'):
        print("\n✓ Resume URLs stored successfully!")
    else:
        print("\n✗ Resume URLs not found in application")
    
elif response.status_code == 409:
    print(f"✓ Already applied to this job (testing with existing application)")
    
    # Get my applications to check the data
    print("\n4. Getting my applications...")
    response = requests.get(f"{BASE_URL}/applications/my-applications", headers=headers)
    if response.status_code == 200:
        applications = response.json()
        if applications:
            app = applications[0]
            print(f"\nFirst Application:")
            print(f"  ID: {app['_id']}")
            print(f"  Match Score: {app['snapshotMatchScore']:.2f}%")
            
            # Check resume files
            print(f"\nResume Files:")
            resume_files = app.get('resumeFiles', {})
            print(f"  File URL: {resume_files.get('resumeFileUrl', 'Not found')}")
            print(f"  Download URL: {resume_files.get('resumeDownloadUrl', 'Not found')}")
            print(f"  Preview URL: {resume_files.get('resumePreviewUrl', 'Not found')}")
            
            if resume_files.get('resumeFileUrl'):
                print("\n✓ Resume URLs found in existing application!")
            else:
                print("\n✗ Resume URLs not found - might be an old application")
else:
    print(f"✗ Application failed: {response.text}")
