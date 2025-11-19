"""API routes for SaferCall AI Backend"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Optional
from app.stt_module import transcribe_audio, get_transcription_metadata
from app.scam_detector import detect_scam, analyze_scam_details, get_scam_type
from app.llm_explainer import explain_scam, get_safety_recommendations
from app.s3_storage import s3_manager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/scan_audio/")
async def scan_audio(
    file: UploadFile = File(...),
    store_in_s3: bool = False
):
    """
    Scan audio file for scam indicators
    
    Args:
        file: Audio file to analyze
        store_in_s3: Whether to store the audio file in S3
    
    Returns:
        JSON response with scam analysis results
    """
    try:
        logger.info(f"Processing audio scan request: {file.filename}")
        
        # Get file metadata
        metadata = get_transcription_metadata(file)
        
        # Transcribe audio to text
        text = transcribe_audio(file)
        logger.info(f"Transcription completed: {len(text)} characters")
        
        # Perform scam detection
        is_scam = detect_scam(text)
        scam_details = analyze_scam_details(text)
        scam_type = get_scam_type(text) if is_scam else "none"
        
        # Get AI explanation
        explanation = explain_scam(text, is_scam)
        
        # Get safety recommendations if scam detected
        recommendations = None
        if is_scam:
            recommendations = get_safety_recommendations(text)
        
        # Store in S3 if requested
        s3_url = None
        if store_in_s3 and is_scam:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            object_key = f"scam_audio/{timestamp}_{file.filename}"
            
            # Upload to S3 (placeholder - would need actual file path)
            # success = s3_manager.upload_audio(file_path, object_key)
            # if success:
            #     s3_url = s3_manager.generate_presigned_url(object_key)
            logger.info(f"Would store in S3 with key: {object_key}")
        
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "audio_metadata": metadata,
            "transcription": {
                "text": text,
                "length": len(text)
            },
            "scam_detection": {
                "is_scam": is_scam,
                "scam_type": scam_type,
                "confidence_score": scam_details["confidence_score"],
                "severity": scam_details["severity"],
                "keywords_found": scam_details["keyword_matches"]
            },
            "analysis": {
                "explanation": explanation,
                "recommendations": recommendations
            },
            "storage": {
                "stored_in_s3": bool(s3_url),
                "s3_url": s3_url
            }
        }
        
        logger.info(f"Scan completed - Scam: {is_scam}, Type: {scam_type}")
        return JSONResponse(content=response, status_code=200)
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing audio scan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/scan_text/")
async def scan_text(text: str = Form(...)):
    """
    Scan text message for scam indicators
    
    Args:
        text: Text content to analyze
    
    Returns:
        JSON response with scam analysis results
    """
    try:
        logger.info(f"Processing text scan request: {len(text)} characters")
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        # Perform scam detection
        is_scam = detect_scam(text)
        scam_details = analyze_scam_details(text)
        scam_type = get_scam_type(text) if is_scam else "none"
        
        # Get AI explanation
        explanation = explain_scam(text, is_scam)
        
        # Get safety recommendations if scam detected
        recommendations = None
        if is_scam:
            recommendations = get_safety_recommendations(text)
        
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "scam_detection": {
                "is_scam": is_scam,
                "scam_type": scam_type,
                "confidence_score": scam_details["confidence_score"],
                "severity": scam_details["severity"],
                "keywords_found": scam_details["keyword_matches"]
            },
            "analysis": {
                "explanation": explanation,
                "recommendations": recommendations
            }
        }
        
        logger.info(f"Text scan completed - Scam: {is_scam}, Type: {scam_type}")
        return JSONResponse(content=response, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing text scan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SaferCall AI Backend"
    }

@router.get("/stats")
async def get_stats():
    """Get system statistics (placeholder for future implementation)"""
    return {
        "total_scans": 0,
        "scams_detected": 0,
        "uptime": "N/A",
        "message": "Statistics tracking not yet implemented"
    }