from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.routes import applications

from fastapi.openapi.utils import get_openapi

# 1️⃣ Load env vars ONCE
load_dotenv()

# 2️⃣ Configure Cloudinary ONCE
import app.utils.cloudinary

# 3️⃣ Create app
app = FastAPI(title="AI Resume Matching Backend")


# 4️⃣ Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- SWAGGER JWT CONFIG ----------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AI Resume Matching Backend",
        version="1.0.0",
        description="Backend APIs secured with JWT",
        routes=app.routes,
    )

    # 🔒 Add Bearer Auth
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply globally (Swagger Authorize button)
    openapi_schema["security"] = [
        {"BearerAuth": []}
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
# ---------------------------------------------------


# 4️⃣ Import routers AFTER config
from app.routes.auth import router as auth_router
from app.routes.resume import router as resume_router
from app.routes.jobs import router as jobs_router
from app.routes.profile import router as profile_router
from app.routes.matching import router as matching_router

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(jobs_router)
app.include_router(profile_router)
app.include_router(matching_router)
app.include_router(applications.router, prefix="/applications", tags=["applications"])


@app.get("/")
def root():
    return {"status": "Backend running"}


# Optional debug (remove later)
print("Cloudinary:", os.getenv("CLOUDINARY_CLOUD_NAME"))
print("Has API key:", bool(os.getenv("CLOUDINARY_API_KEY")))
