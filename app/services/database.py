from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()

DB_USER = os.getenv("DB_USERNAME")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3401")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:"
    f"{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
    f"{DB_NAME}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True,pool_size=5,max_overflow=10,pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("Database connected successfully!")
    except Exception as e:
        print("Database connection failed:", e)