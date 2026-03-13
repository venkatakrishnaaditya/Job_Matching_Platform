from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv

# Load .env file FIRST
load_dotenv()

# Get MONGO_URI and validate
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI not found in .env file")

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=30000,
    retryWrites=True,
    w="majority"
)

# Extract database name from URI or use default
db = client.get_database("ai_resume_matching")


def get_db():
    return db
