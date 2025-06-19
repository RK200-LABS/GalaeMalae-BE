from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.oauth import (
    get_google_auth_url,
    get_google_token,
    get_google_user_info,
    get_or_create_google_user
)
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema, Token

router = APIRouter()

@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """회원가입"""
    # 이메일 중복 확인
    db_user = db.query(User).filter(User.email == user.email, User.deleted_at.is_(None)).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 새 사용자 생성
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password=hashed_password,
        nickname=user.nickname or user.email.split("@")[0]
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """로그인"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """로그아웃 (클라이언트에서 토큰 삭제)"""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    """현재 사용자 정보 조회"""
    return current_user

@router.get("/google/login")
def google_login():
    """Google OAuth 로그인 URL 반환"""
    auth_url = get_google_auth_url()
    return {"auth_url": auth_url}

@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    """Google OAuth 콜백 처리"""
    # 액세스 토큰 교환
    token_data = get_google_token(code)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get access token from Google"
        )
    
    # 사용자 정보 조회
    user_info = get_google_user_info(token_data["access_token"])
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from Google"
        )
    
    # 사용자 조회 또는 생성
    user = get_or_create_google_user(db, user_info)
    
    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"} 