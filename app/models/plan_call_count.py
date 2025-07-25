from sqlalchemy import Column, Integer
from app.db.session import Base

class PlanCallCount(Base):
    __tablename__ = "plan_call_count"
    id = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, default=0)