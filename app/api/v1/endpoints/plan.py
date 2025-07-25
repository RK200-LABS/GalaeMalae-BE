from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.plan import PlanRequest
from app.core.plan import create_travel_plan
from app.models.plan_call_count import PlanCallCount


import json

router = APIRouter()

@router.post("/plan")
def recommend_plan(request: PlanRequest, db: Session = Depends(get_db)):


    call_count = db.query(PlanCallCount).first()
    if not call_count:
        call_count = PlanCallCount(count=1)
        db.add(call_count)
    else:
        call_count.count += 1
    db.commit()

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

@router.get("/create/count")
def get_plan_create_count(db: Session = Depends(get_db)):
    call_count = db.query(PlanCallCount).first()
    return {"count": call_count.count if call_count else 0}