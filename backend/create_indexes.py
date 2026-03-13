"""
Script to create MongoDB indexes for applications collection
Run this once to set up database indexes for optimal performance
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("❌ Error: MONGO_URI not found in .env file")
    exit(1)

# Connect to MongoDB
print("🔌 Connecting to MongoDB...")
client = MongoClient(MONGO_URI)

# Get database (ai_resume_matching)
db = client.get_database()

print(f"✅ Connected to database: {db.name}")

# Create applications collection if it doesn't exist
applications_collection = db.applications

print("\n📊 Creating indexes for 'applications' collection...")

try:
    # Index 1: Unique constraint on candidateId + jobId (prevent duplicate applications)
    print("\n1️⃣ Creating unique index: (candidateId + jobId)")
    applications_collection.create_index(
        [("candidateId", ASCENDING), ("jobId", ASCENDING)],
        unique=True,
        name="unique_application"
    )
    print("   ✅ Index 'unique_application' created")
    
    # Index 2: Fast recruiter queries (sorted by match score)
    print("\n2️⃣ Creating index: (jobId + snapshotMatchScore)")
    applications_collection.create_index(
        [("jobId", ASCENDING), ("snapshotMatchScore", DESCENDING)],
        name="recruiter_view_sorted"
    )
    print("   ✅ Index 'recruiter_view_sorted' created")
    
    # Index 3: Fast candidate queries (sorted by application date)
    print("\n3️⃣ Creating index: (candidateId + appliedAt)")
    applications_collection.create_index(
        [("candidateId", ASCENDING), ("appliedAt", DESCENDING)],
        name="candidate_applications"
    )
    print("   ✅ Index 'candidate_applications' created")
    
    print("\n" + "="*50)
    print("✅ All indexes created successfully!")
    print("="*50)
    
    # List all indexes
    print("\n📋 Current indexes on 'applications' collection:")
    for index in applications_collection.list_indexes():
        print(f"   - {index['name']}: {index['key']}")
    
except Exception as e:
    print(f"\n❌ Error creating indexes: {str(e)}")
    
finally:
    client.close()
    print("\n🔌 Connection closed")
