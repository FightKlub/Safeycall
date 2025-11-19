"""
Database setup and connection management
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database_url if settings.database_url else "sqlite:///./safercall.db",
    connect_args={"check_same_thread": False} if "sqlite" in (settings.database_url or "") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ScanRecordDB(Base):
    """Database model for scan records"""
    __tablename__ = "scan_records"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(String(10), nullable=False)  # 'audio' or 'text'
    content_hash = Column(String(64), index=True)
    is_scam = Column(Boolean, default=False)
    confidence_score = Column(Integer)
    scam_type = Column(String(50), nullable=True)
    severity = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    s3_url = Column(Text, nullable=True)


class UserDB(Base):
    """Database model for users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    api_key = Column(String(100), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    scan_count = Column(Integer, default=0)


class APIKeyDB(Base):
    """Database model for API keys"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True)
    name = Column(String(100))
    user_id = Column(Integer, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
