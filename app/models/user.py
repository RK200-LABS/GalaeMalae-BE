from sqlalchemy import Column, String, DateTime, BigInteger
from sqlalchemy.sql import func
from app.db.session import Base
import uuid

class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    nickname = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True) 