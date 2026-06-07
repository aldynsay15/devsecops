from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# SECURITY_FLAW: Использование стандартного postgres пользователя в production
# Ожидается, что сканер безопасности найдет это как нарушение security best practice
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/app_db"  # <-- УЯЗВИМОСТЬ: дефолтный пароль
)

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
