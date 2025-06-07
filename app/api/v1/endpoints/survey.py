from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.survey import build_profile, run_recommendation
from app.db.session import get_db
from app.schemas.survey import SurveySubmit, SurveyResult
router = APIRouter()

@router.post("/submit", response_model=SurveyResult)
def survey_submit(survey: SurveySubmit, db: Session = Depends(get_db)):
    # 1) 설문 → profile 생성
    profile = build_profile(survey.dict())

    # 2) DB 조회 + 점수 계산 → 추천 리스트
    recs = run_recommendation(profile, db)

    # 3) 결과 반환
    return SurveyResult(recommendations=recs)