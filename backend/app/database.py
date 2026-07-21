"""数据库会话管理"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL

# SQLite compatible - remove +aiosqlite prefix for sync engine
sync_url = DATABASE_URL.replace("+aiosqlite", "")

engine = create_engine(sync_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models.database import Base
    Base.metadata.create_all(bind=engine)
