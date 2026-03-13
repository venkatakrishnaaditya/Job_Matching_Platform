# 🎯 AI-Powered Job Matching Platform

A full-stack web application that intelligently matches job seekers with job postings using **NLP-based resume parsing**, **TF-IDF + Cosine Similarity skill matching**, and a **weighted scoring algorithm**.

---

## 🚀 Features

### For Candidates
- 📄 Upload resume (PDF/DOCX) — auto-parsed with spaCy + Regex
- 🤖 AI match score for every job (Skills 70% + Experience 20% + Education 10%)
- 📊 View ranked jobs by match percentage
- 🔍 See matching skills, missing skills, and breakdown per job
- 📝 Apply to jobs with a frozen match score snapshot
- 📬 Track application status (Applied → Reviewed → Shortlisted / Rejected)
- 💡 Skill recommendations based on job market demand

### For Recruiters
- 💼 Post jobs with AI-assisted JD parsing (auto-fills skills, experience, education)
- 📈 View applicants ranked by match score
- 📎 Preview and download candidate resumes
- ✅ Update application status with validated transitions
- 🗃️ Manage jobs (Open / Close / Archive / Restore)

### General
- 🔐 JWT authentication (register, login, forgot/reset password)
- 👤 Role-based profiles (Candidate vs Recruiter)
- 📷 Profile photo & company logo upload (Cloudinary)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, React Router v7, Vanilla CSS |
| **Backend** | Python 3, FastAPI, Uvicorn |
| **Database** | MongoDB Atlas (PyMongo) |
| **Auth** | JWT (HS256) + Argon2 password hashing |
| **File Storage** | Cloudinary |
| **NLP / AI** | spaCy (`en_core_web_sm`), Scikit-learn (TF-IDF + Cosine Similarity) |
| **Email** | Gmail SMTP (password reset) |

---

## 📁 Project Structure

```
Job_Matching_Platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── db/mongo.py          # MongoDB connection
│   │   ├── models/              # Pydantic data models
│   │   ├── routes/              # API route handlers
│   │   │   ├── auth.py          # Register, Login, Password Reset
│   │   │   ├── resume.py        # Resume upload & parsing
│   │   │   ├── jobs.py          # Job CRUD + AI JD parsing
│   │   │   ├── matching.py      # AI match score engine
│   │   │   ├── applications.py  # Application lifecycle
│   │   │   └── profile.py       # User profile management
│   │   └── utils/
│   │       ├── resume_parser.py # Hybrid Regex + spaCy resume parser
│   │       ├── jd_parser.py     # Job description AI parser
│   │       ├── skill_matcher.py # TF-IDF + Cosine Similarity
│   │       ├── match_calculator.py # Weighted scoring engine
│   │       ├── jwt.py           # JWT utilities
│   │       ├── email_service.py # SMTP email service
│   │       └── cloudinary.py    # File upload utility
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.js               # Router + layout
        ├── pages/               # 15 page components
        ├── components/          # Reusable UI components
        └── services/api.js      # Centralized API client
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB Atlas account
- Cloudinary account

---

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Create `backend/.env`:
```
MONGO_URI=your_mongodb_atlas_uri
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
SMTP_EMAIL=your_gmail@gmail.com
SMTP_PASSWORD=your_gmail_app_password
FRONTEND_URL=http://localhost:3000
```

Run the backend:
```bash
uvicorn app.main:app --reload
```
→ API runs at `http://localhost:8000`  
→ Swagger docs at `http://localhost:8000/docs`

---

### Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:
```
REACT_APP_API_URL=http://localhost:8000
```

Run the frontend:
```bash
npm start
```
→ App runs at `http://localhost:3000`

---

## 🤖 AI Matching Algorithm

```
Final Match Score = (Skills × 70%) + (Experience × 20%) + (Education × 10%)
```

**Skills Score:**
- Required skills: Set-based exact match (with 100+ synonym mappings, e.g. `ReactJS` = `React`, `JS` = `JavaScript`)
- Preferred skills: TF-IDF Cosine Similarity bonus (max +20%)

**Experience Score:**
- `min(candidate_years / required_years, 1.0)`

**Education Score:**
- Ordinal levels: Not Required → Any Degree → Bachelor's → Master's → PhD

**Match Labels:**

| Score | Label |
|---|---|
| 90–100% | 🟢 Excellent Match |
| 70–89% | 🔵 Good Match |
| 50–69% | 🟡 Fair Match |
| 0–49% | ⚫ Weak Match |

---

## 📡 API Endpoints Summary

| Module | Endpoints |
|---|---|
| Auth | `POST /auth/register`, `/auth/login`, `/auth/forgot-password`, `/auth/reset-password` |
| Resume | `POST /resumes/upload`, `GET /resumes/status`, `GET /resumes/parsed-data`, `DELETE /resumes/remove` |
| Jobs | `POST /jobs/create`, `GET /jobs/`, `PUT /jobs/{id}`, `PATCH /jobs/{id}/status`, `DELETE /jobs/{id}/archive` |
| Matching | `GET /matching/jobs/ranked`, `GET /matching/job/{id}`, `GET /matching/candidates/{id}`, `GET /matching/skill-recommendations` |
| Applications | `POST /applications/apply`, `GET /applications/my-applications`, `PATCH /applications/{id}/status`, `DELETE /applications/{id}/withdraw` |
| Profile | `GET /users/profile`, `PUT /users/profile`, `POST /users/upload-photo` |

---

## 🔒 Security Notes

- Passwords hashed with **Argon2** (memory-hard, industry standard)
- JWT tokens expire in **60 minutes**
- Password reset tokens are **single-use** and expire in **1 hour**
- `.env` files are gitignored — never committed to version control
- Role-based access enforced on every protected endpoint

---

## 👤 Author

**Venkata Krishna Aditya**  
[GitHub](https://github.com/venkatakrishnaaditya)
