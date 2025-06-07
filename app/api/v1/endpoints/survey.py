from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.survey import SurveySubmit, SurveyResult
router = APIRouter()

@router.post("/submit")
def survey_submit(survey: SurveySubmit, db: Session = Depends(get_db)):
    return {"message": "Survey submitted successfully"}