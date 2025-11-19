"""Advanced scam detection module with keyword matching and pattern analysis"""
import re
import logging
from typing import Dict, List, Tuple
from app.config import SCAM_KEYWORDS

logger = logging.getLogger(__name__)

# Suspicious patterns
SUSPICIOUS_PATTERNS = [
    r"\b\d{6}\b",  # 6-digit OTP
    r"\b\d{16}\b",  # Credit card numbers
    r"verify.*account",
    r"suspend.*account",
    r"urgent.*action",
    r"click.*link",
    r"expire.*\d+.*hours",
    r"won.*prize",
    r"refund.*\$\d+",
    r"tax.*refund",
    r"update.*payment",
]

def detect_scam(text: str) -> bool:
    """
    Detect if text contains scam indicators
    
    Args:
        text: The text to analyze
    
    Returns:
        bool: True if scam indicators are found
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Check for scam keywords
    keyword_matches = [word for word in SCAM_KEYWORDS if word in text_lower]
    
    # Check for suspicious patterns
    pattern_matches = []
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text_lower):
            pattern_matches.append(pattern)
    
    is_scam = len(keyword_matches) > 0 or len(pattern_matches) > 0
    
    if is_scam:
        logger.warning(f"Scam detected - Keywords: {keyword_matches}, Patterns: {len(pattern_matches)}")
    else:
        logger.info("No scam indicators detected")
    
    return is_scam

def analyze_scam_details(text: str) -> Dict:
    """
    Provide detailed analysis of scam indicators
    
    Returns:
        dict: Detailed analysis including confidence score and matched indicators
    """
    text_lower = text.lower()
    
    # Find all matching keywords
    keyword_matches = [word for word in SCAM_KEYWORDS if word in text_lower]
    
    # Find all matching patterns
    pattern_matches = []
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text_lower):
            pattern_matches.append(pattern)
    
    # Calculate confidence score (0-100)
    confidence = min(100, (len(keyword_matches) * 20) + (len(pattern_matches) * 15))
    
    return {
        "is_scam": len(keyword_matches) > 0 or len(pattern_matches) > 0,
        "confidence_score": confidence,
        "keyword_matches": keyword_matches,
        "pattern_count": len(pattern_matches),
        "severity": "high" if confidence > 70 else "medium" if confidence > 40 else "low"
    }

def get_scam_type(text: str) -> str:
    """
    Classify the type of scam based on content
    
    Returns:
        str: Scam type classification
    """
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["bank", "account", "card", "pin"]):
        return "financial_fraud"
    elif any(word in text_lower for word in ["otp", "verify", "code"]):
        return "otp_scam"
    elif any(word in text_lower for word in ["anydesk", "remote", "teamviewer"]):
        return "tech_support_scam"
    elif any(word in text_lower for word in ["prize", "won", "lottery"]):
        return "prize_scam"
    elif any(word in text_lower for word in ["tax", "irs", "refund"]):
        return "government_impersonation"
    else:
        return "generic_scam"
