from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Header, HTTPException
from bson import ObjectId

from app.db.mongo import get_db

# ---------------- JWT CONFIG ----------------
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_LATER"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ---------------- TOKEN CREATION ----------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- TOKEN DECODE ----------------
def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# ---------------- CURRENT USER DEPENDENCY ----------------
def get_current_user(authorization: str = Header(None)):
    # 1️⃣ Check header
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]

    # 2️⃣ Decode token
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 3️⃣ Fetch user from DB (IMPORTANT FIX)
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)})

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
