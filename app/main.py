from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import users, survey, auth, plan
from app.db.init_db import init_db
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

app = FastAPI(
    title="GalaeMalae API",
    description="GalaeMalae Backend API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 도메인만 허용하도록 수정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(survey.router, prefix="/api/v1/survey", tags=["survey"])
app.include_router(plan.router, prefix="/api/v1/plan", tags=["plan"])

@app.get("/")
async def root():
    return {"message": "Welcome to GalaeMalae API"}

# 앱 시작 시 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    init_db() 