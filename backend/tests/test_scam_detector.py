"""
Test scam detector module
"""
import pytest
from app.scam_detector import detect_scam, analyze_scam_details, get_scam_type


class TestScamDetector:
    """Test scam detection functions"""
    
    def test_detect_otp_scam(self):
        """Test OTP scam detection"""
        text = "Please share your OTP to verify your account"
        assert detect_scam(text) is True
    
    def test_detect_bank_scam(self):
        """Test bank account scam detection"""
        text = "Your bank account will be suspended. Update your details."
        assert detect_scam(text) is True
    
    def test_detect_legitimate_message(self):
        """Test legitimate message"""
        text = "Hi, let's meet for coffee tomorrow"
        assert detect_scam(text) is False
    
    def test_analyze_scam_details(self):
        """Test detailed scam analysis"""
        text = "Send OTP and credit card details for prize claim"
        result = analyze_scam_details(text)
        assert result["is_scam"] is True
        assert result["confidence_score"] > 0
        assert "otp" in result["keyword_matches"]
    
    def test_get_scam_type_financial(self):
        """Test scam type classification - financial"""
        text = "Update your bank account information"
        scam_type = get_scam_type(text)
        assert scam_type == "financial_fraud"
    
    def test_get_scam_type_otp(self):
        """Test scam type classification - OTP"""
        text = "Verify your OTP code now"
        scam_type = get_scam_type(text)
        assert scam_type == "otp_scam"
    
    def test_empty_text(self):
        """Test with empty text"""
        assert detect_scam("") is False
        assert detect_scam(None) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
