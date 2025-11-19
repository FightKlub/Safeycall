"""
SaferCall AI Backend Application Package
"""
__version__ = "1.0.0"
__author__ = "SaferCall AI Team"
__email__ = "support@safercall.ai"

from app.config import get_settings

# Initialize settings on import
settings = get_settings()
