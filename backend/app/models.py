"""Database models for SaferCall AI Backend"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class AudioScanRequest(BaseModel):
    """Request model for audio scanning"""
    store_in_s3: bool = Field(default=False, description="Store audio file in S3")


class TextScanRequest(BaseModel):
    """Request model for text scanning"""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v


class ScamDetectionResult(BaseModel):
    """Scam detection result model"""
    is_scam: bool
    scam_type: str
    confidence_score: int = Field(ge=0, le=100)
    severity: str
    keywords_found: list


class TranscriptionResult(BaseModel):
    """Transcription result model"""
    text: str
    length: int
    language: Optional[str] = "en"


class AudioMetadata(BaseModel):
    """Audio file metadata"""
    filename: str
    file_size_bytes: int
    file_size_mb: float
    format: str
    duration_seconds: Optional[float] = None


class AnalysisResult(BaseModel):
    """Analysis result model"""
    explanation: str
    recommendations: Optional[dict] = None


class StorageInfo(BaseModel):
    """Storage information"""
    stored_in_s3: bool
    s3_url: Optional[str] = None
    s3_key: Optional[str] = None


class AudioScanResponse(BaseModel):
    """Response model for audio scanning"""
    success: bool
    timestamp: str
    audio_metadata: AudioMetadata
    transcription: TranscriptionResult
    scam_detection: ScamDetectionResult
    analysis: AnalysisResult
    storage: StorageInfo


class TextScanResponse(BaseModel):
    """Response model for text scanning"""
    success: bool
    timestamp: str
    text: str
    scam_detection: ScamDetectionResult
    analysis: AnalysisResult


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    message: str
    details: Optional[dict] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    service: str
    version: Optional[str] = "1.0.0"


class ScamStatistics(BaseModel):
    """Statistics model"""
    total_scans: int = 0
    scams_detected: int = 0
    scam_types: dict = {}
    avg_confidence_score: float = 0.0
    uptime: str = "N/A"


# Database models (if using database)
class ScanRecord(BaseModel):
    """Database record for scan history"""
    id: Optional[int] = None
    scan_type: str  # 'audio' or 'text'
    content_hash: str
    is_scam: bool
    confidence_score: int
    scam_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None
    ip_address: Optional[str] = None


class UserModel(BaseModel):
    """User model"""
    id: Optional[int] = None
    username: str
    email: str
    api_key: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    scan_count: int = 0


class APIKeyModel(BaseModel):
    """API Key model"""
    key: str
    name: str
    user_id: int
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
