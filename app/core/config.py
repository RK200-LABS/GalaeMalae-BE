from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "GalaeMalae"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT 설정
    SECRET_KEY: str = "your-secret-key-here"  # 실제 운영 환경에서는 환경 변수로 관리
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    class Config:
        case_sensitive = True

settings = Settings() 