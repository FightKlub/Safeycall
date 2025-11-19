"""LLM-based scam explanation module using Google Gemini API"""
import google.generativeai as genai
import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Gemini API with credentials from environment
genai.configure(api_key=settings.gemini_api_key)

# Initialize Gemini model
model = genai.GenerativeModel("models/gemini-1.5-pro")

def explain_scam(text: str, is_scam: bool = True) -> str:
    """
    Generate a detailed explanation of why a text might be a scam
    
    Args:
        text: The text content to analyze
        is_scam: Whether the text was detected as a potential scam
    
    Returns:
        str: Human-readable explanation of the scam indicators
    """
    try:
        if is_scam:
            prompt = f"""Analyze this phone call or message and explain why it could be a scam.
            Provide a clear, simple explanation that a non-technical user can understand.
            
            Text: '{text}'
            
            Include:
            1. Specific red flags or warning signs
            2. Common scam tactics being used
            3. What a legitimate organization would do instead
            4. Recommended actions to stay safe
            """
        else:
            prompt = f"""This message appears legitimate. Explain briefly why this is likely safe:
            
            Text: '{text}'
            """
        
        logger.info(f"Generating explanation for text (scam={is_scam})")
        response = model.generate_content(prompt)
        
        if response and response.text:
            logger.info("Successfully generated explanation")
            return response.text
        else:
            logger.warning("Empty response from Gemini API")
            return "Unable to generate explanation at this time."
            
    except Exception as e:
        logger.error(f"Error generating scam explanation: {str(e)}")
        return f"Analysis unavailable: {str(e)}"

def get_safety_recommendations(text: str) -> dict:
    """
    Get specific safety recommendations based on the scam type
    
    Returns:
        dict: Safety recommendations and action items
    """
    try:
        prompt = f"""For this potential scam message, provide specific safety recommendations:
        
        Text: '{text}'
        
        Return a JSON response with:
        - immediate_actions: List of actions to take right now
        - do_not: List of things to avoid
        - report_to: Where to report this scam
        """
        
        response = model.generate_content(prompt)
        return {"recommendations": response.text}
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return {"recommendations": "Contact your bank or local authorities if you suspect fraud."}
