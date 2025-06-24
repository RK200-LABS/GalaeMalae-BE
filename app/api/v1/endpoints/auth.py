from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from jose import jwt

from jose import jwt
from datetime import datetime, timedelta

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
from app.core.config import settings

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

@router.post("/google/decode")
def google_decode_credential(
    credential: str = Body(..., embed=True),
    db: Session = Depends(get_db)
    ):
    """구글 credential(JWT)에서 이메일, 이름 추출 (서명 검증 생략)"""
    try:
        # 서명 검증 없이 decode (verify=False)
        payload = jwt.get_unverified_claims(credential)
        email = payload.get("email")
        name = payload.get("name")
        
        # 사용자 조회
        user = db.query(User).filter(User.email == email).first()
        # 없으면 생성
        if not user:
            nickname=email.split("@")[0]
            user = User(email=email, name=nickname)
            db.add(user)
            db.commit()
            db.refresh(user)

        # JWT 발급
        token = create_jwt(email=user.email, name=user.name)
        return {"access_token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid credential: {str(e)}")


def create_jwt(email: str, name: str):
    now = datetime.utcnow()
    payload = {
        "sub": email,
        "name": name,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp())
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token