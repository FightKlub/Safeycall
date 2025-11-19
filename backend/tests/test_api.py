"""
Test cases for SaferCall AI Backend
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "SaferCall AI API is running"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestScamDetection:
    """Test scam detection functionality"""
    
    def test_detect_scam_text_positive(self):
        """Test scam detection with scam text"""
        response = client.post(
            "/api/v1/scan_text/",
            data={"text": "Send me your OTP and bank account details immediately"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["scam_detection"]["is_scam"] is True
    
    def test_detect_scam_text_negative(self):
        """Test scam detection with legitimate text"""
        response = client.post(
            "/api/v1/scan_text/",
            data={"text": "Hello, how are you today?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["scam_detection"]["is_scam"] is False
    
    def test_empty_text_validation(self):
        """Test validation for empty text"""
        response = client.post(
            "/api/v1/scan_text/",
            data={"text": ""}
        )
        assert response.status_code == 400


class TestAudioProcessing:
    """Test audio processing endpoints"""
    
    def test_audio_scan_missing_file(self):
        """Test audio scan without file"""
        response = client.post("/api/v1/scan_audio/")
        assert response.status_code == 422  # Unprocessable Entity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
