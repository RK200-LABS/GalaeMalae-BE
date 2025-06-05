from app.db.session import engine, Base
from app.models.user import User  # 모든 모델을 여기서 import

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 