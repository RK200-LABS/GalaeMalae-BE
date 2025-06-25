from fastapi import APIRouter, HTTPException, Request, Body, Response
from jose import jwt
from app.core.config import settings
import os

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
router = APIRouter()

@router.post("/google/decode")
def google_decode_credential(
    response: Response,
    credential: str = Body(..., embed=True)
):
    try:
        payload = jwt.get_unverified_claims(credential)
        email = payload.get("email")
        name = payload.get("name")
        if not email or not name:
            raise HTTPException(status_code=400, detail="Invalid credential payload")
        token = create_jwt(email=email, name=name)
        return {"access_token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid credential: {str(e)}")

@router.get("/me")
def get_me(request: Request):
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("email")
        name = payload.get("name")
        if not email or not name:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"email": email, "name": name}
    except Exception as e:
        print("JWT decode error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")

def create_jwt(email: str, name: str):
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    payload = {
        "sub": email,
        "name": name,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=24)).timestamp())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token