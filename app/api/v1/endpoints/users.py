from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user, get_password_hash
from app.schemas.user import User, UserCreate, UserUpdate
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """사용자 목록 조회 (인증 필요)"""
    users = db.query(UserModel).filter(UserModel.deleted_at.is_(None)).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """특정 사용자 조회 (인증 필요)"""
    user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.deleted_at.is_(None)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """사용자 정보 수정 (본인만 가능)"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.deleted_at.is_(None)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 업데이트할 필드들
    update_data = user_update.dict(exclude_unset=True)
    
    # 비밀번호가 포함된 경우 해싱
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """사용자 삭제 (본인만 가능)"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.deleted_at.is_(None)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Soft delete
    from datetime import datetime
    user.deleted_at = datetime.now()
    db.commit()
    
    return {"message": "User deleted successfully"} 