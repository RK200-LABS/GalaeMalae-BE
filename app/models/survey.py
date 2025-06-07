from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime
from app.db.session import Base
from datetime import datetime

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String, index=True)
    description = Column(String, index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, default=datetime.now)
