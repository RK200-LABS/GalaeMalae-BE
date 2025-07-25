from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.survey import build_profile, run_recommendation
from app.db.session import get_db
from app.schemas.survey import SurveySubmit, SurveyResult
from app.models.survey_call_count import SurveyCallCount

router = APIRouter()

@router.post("/submit", response_model=SurveyResult)
def survey_submit(survey: SurveySubmit, db: Session = Depends(get_db)):

    # 1) 호출 횟수 증가
    call_count = db.query(SurveyCallCount).first()
    if not call_count:
        call_count = SurveyCallCount(count=1)
        db.add(call_count)
    else:
        call_count.count += 1
    db.commit()

    # 1) 설문 → profile 생성
    profile = build_profile(survey.dict())

    # 2) DB 조회 + 점수 계산 → 추천 리스트
    recs = run_recommendation(profile, db)

    # 3) 결과 반환
    return SurveyResult(recommendations=recs)

@router.get("/submit/count")
def get_survey_submit_count(db: Session = Depends(get_db)):
    call_count = db.query(SurveyCallCount).first()
    return {"count": call_count.count if call_count else 0}