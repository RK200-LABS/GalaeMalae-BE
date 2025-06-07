from sqlalchemy import Column, Integer, ForeignKey
from app.db.session import Base

class DestinationTag(Base):
    __tablename__ = "destination_tag"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destination.id"))
    tag_id = Column(Integer, ForeignKey("tag.id"))
    score = Column(Integer, default=0)
    weight_score = Column(Integer, default=0)
    