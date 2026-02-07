# src/config.py
"""
Configuration module for API keys and environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

def get_gemini_api_key():
    """
    Get Gemini API key from environment variables
    
    Returns:
        str: API key or empty string if not found
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please create a .env file with GEMINI_API_KEY=your_key_here"
        )
    return GEMINI_API_KEY
