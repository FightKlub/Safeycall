"""Speech-to-Text module using OpenAI Whisper"""
import whisper
import tempfile
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
from app.config import get_settings, ALLOWED_AUDIO_FORMATS, MAX_FILE_SIZE_BYTES

logger = logging.getLogger(__name__)
settings = get_settings()

# Load Whisper model
try:
    model = whisper.load_model(settings.whisper_model_size)
    logger.info(f"Loaded Whisper model: {settings.whisper_model_size}")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {str(e)}")
    model = None

def validate_audio_file(file) -> Tuple[bool, Optional[str]]:
    """
    Validate audio file format and size
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_AUDIO_FORMATS:
        return False, f"Unsupported audio format. Allowed: {', '.join(ALLOWED_AUDIO_FORMATS)}"
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE_BYTES / (1024*1024)}MB"
    
    if file_size == 0:
        return False, "File is empty"
    
    return True, None

def transcribe_audio(file) -> str:
    """
    Transcribe audio file to text using Whisper
    
    Args:
        file: UploadFile object containing audio data
    
    Returns:
        str: Transcribed text
    
    Raises:
        ValueError: If file validation fails
        RuntimeError: If transcription fails
    """
    if model is None:
        logger.error("Whisper model not loaded")
        raise RuntimeError("Speech recognition service unavailable")
    
    # Validate file
    is_valid, error_msg = validate_audio_file(file)
    if not is_valid:
        logger.warning(f"Audio validation failed: {error_msg}")
        raise ValueError(error_msg)
    
    temp_path = None
    try:
        # Create temporary file with appropriate extension
        file_ext = Path(file.filename).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            content = file.file.read()
            tmp.write(content)
            temp_path = tmp.name
        
        logger.info(f"Transcribing audio file: {file.filename} ({len(content)} bytes)")
        
        # Transcribe audio
        result = model.transcribe(temp_path, language="en", fp16=False)
        
        transcribed_text = result.get("text", "").strip()
        
        if not transcribed_text:
            logger.warning("Transcription resulted in empty text")
            return "[No speech detected]"
        
        logger.info(f"Successfully transcribed {len(transcribed_text)} characters")
        return transcribed_text
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise RuntimeError(f"Failed to transcribe audio: {str(e)}")
        
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.debug(f"Cleaned up temporary file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {str(e)}")

def get_transcription_metadata(file) -> Dict:
    """
    Get metadata about the audio file and transcription
    
    Returns:
        dict: Metadata including duration, file size, etc.
    """
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    return {
        "filename": file.filename,
        "file_size_bytes": file_size,
        "file_size_mb": round(file_size / (1024 * 1024), 2),
        "format": Path(file.filename).suffix.lower()
    }
