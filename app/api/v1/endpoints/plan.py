from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.plan import PlanRequest
from app.core.plan import create_travel_plan
import json

router = APIRouter()

@router.post("/plan")
def recommend_plan(request: PlanRequest, db: Session = Depends(get_db)):
    """
    여행지 이름과 여행 일정을 받아 여행 계획을 생성합니다.
    (비즈니스 로직은 core/plan.py에 위임)
    """
    try:
        plan_data = create_travel_plan(
            destination=request.destination,
            schedule=request.schedule
        )
        return plan_data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="API로부터 유효한 JSON 응답을 받지 못했습니다.")
    except Exception as e:
        # 서비스 계층에서 발생한 예외를 여기서 처리합니다.
        raise HTTPException(status_code=500, detail=f"여행 계획 생성 중 오류 발생: {str(e)}")