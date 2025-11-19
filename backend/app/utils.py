"""Utility functions for SaferCall AI Backend"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token
    
    Args:
        length: Length of the token
    
    Returns:
        str: Secure random token
    """
    return secrets.token_urlsafe(length)


def hash_text(text: str) -> str:
    """
    Generate SHA256 hash of text
    
    Args:
        text: Text to hash
    
    Returns:
        str: Hex digest of hash
    """
    return hashlib.sha256(text.encode()).hexdigest()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks
    
    Args:
        filename: Original filename
    
    Returns:
        str: Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    dangerous_chars = ['..', '/', '\\', '\x00']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def calculate_expiry_time(hours: int = 24) -> datetime:
    """
    Calculate expiry datetime
    
    Args:
        hours: Number of hours from now
    
    Returns:
        datetime: Expiry datetime
    """
    return datetime.now() + timedelta(hours=hours)


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging
    
    Args:
        data: Sensitive data to mask
        visible_chars: Number of characters to keep visible
    
    Returns:
        str: Masked data
    """
    if len(data) <= visible_chars:
        return "*" * len(data)
    
    return data[:visible_chars] + "*" * (len(data) - visible_chars)


def validate_email(email: str) -> bool:
    """
    Basic email validation
    
    Args:
        email: Email address to validate
    
    Returns:
        bool: True if valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone_number(phone: str) -> bool:
    """
    Basic phone number validation
    
    Args:
        phone: Phone number to validate
    
    Returns:
        bool: True if valid
    """
    import re
    # Remove common formatting characters
    phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    # Check if it's 10-15 digits
    return bool(re.match(r'^\d{10,15}$', phone))


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed
        
        Args:
            identifier: Unique identifier (e.g., IP address)
        
        Returns:
            bool: True if request is allowed
        """
        now = datetime.now()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside the window
        cutoff_time = now - timedelta(seconds=self.window_seconds)
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True


def log_api_call(endpoint: str, method: str, status_code: int, duration_ms: float):
    """
    Log API call metrics
    
    Args:
        endpoint: API endpoint called
        method: HTTP method
        status_code: Response status code
        duration_ms: Request duration in milliseconds
    """
    logger.info(
        f"API Call - {method} {endpoint} - "
        f"Status: {status_code} - Duration: {duration_ms:.2f}ms"
    )
