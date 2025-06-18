import requests
from typing import Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.auth import create_access_token, get_password_hash
import os

# Google OAuth 설정
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")

def get_google_auth_url() -> str:
    """Google OAuth 인증 URL 생성"""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

def get_google_token(code: str) -> Optional[Dict]:
    """Google OAuth 코드로 액세스 토큰 교환"""
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_google_user_info(access_token: str) -> Optional[Dict]:
    """Google 사용자 정보 조회"""
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_or_create_google_user(db: Session, google_user_info: Dict) -> User:
    """Google 사용자 정보로 사용자 조회 또는 생성"""
    email = google_user_info.get("email")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google"
        )
    
    # 기존 사용자 조회
    user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
    
    if user:
        return user
    
    # 새 사용자 생성
    user = User(
        email=email,
        nickname=google_user_info.get("name", email.split("@")[0]),
        password=get_password_hash("google_oauth_user")  # 임시 비밀번호
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user 