from sqlalchemy import Column, Integer, String
from app.db.session import Base

class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    label = Column(String(100), index=True)