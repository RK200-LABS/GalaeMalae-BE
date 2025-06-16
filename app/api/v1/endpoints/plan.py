from fastapi import APIRouter, Depends
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.schemas.plan import destination

router = APIRouter()

@router.post("/plan", )
def recommend_plan(destination : destination, db: Session = Depends(get_db)):
    
    return "test"