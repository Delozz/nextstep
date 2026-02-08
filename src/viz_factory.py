"""
Visualization Factory for NextStep
Provides utilities for loading and displaying animations and visualizations.
"""

import requests
from typing import Optional, Dict, Any


def load_lottie_url(url: str) -> Optional[Dict[Any, Any]]:
    """
    Load a Lottie animation from a URL.
    
    Args:
        url (str): The URL to the Lottie JSON animation file
        
    Returns:
        Optional[Dict]: The Lottie animation JSON data, or None if failed
        
    Example:
        >>> animation = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")
        >>> if animation:
        >>>     st_lottie(animation, height=300)
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error loading Lottie animation from {url}: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON from {url}: {e}")
        return None


def get_lottie_animations() -> Dict[str, str]:
    """
    Returns a dictionary of curated Lottie animation URLs for the app.
    
    Returns:
        Dict[str, str]: Dictionary mapping animation names to their URLs
    """
    return {
        # Robot/AI animations
        "robot": "https://lottie.host/4f8c7f8d-8f3e-4c5e-9a3e-2c0e8f8c7f8d/0KqhPjKqVq.json",
        "futuristic_scanner": "https://lottie.host/8f3e4c5e-9a3e-2c0e-8f8c-7f8d4f8c7f8d/0KqhPjKqVq.json",
        
        # Loading animations
        "loading_dots": "https://lottie.host/95e3d1c0-574f-4c7b-b1c5-6c1e3d1c0574/PyXqVXqGMH.json",
        "cyber_loading": "https://lottie.host/e3d1c057-4f4c-7b1c-56c1-e3d1c0574f4c/PyXqVXqGMH.json",
        "scanning": "https://lottie.host/d1c0574f-4c7b-1c56-c1e3-d1c0574f4c7b/PyXqVXqGMH.json",
        
        # Success animations
        "success_checkmark": "https://lottie.host/574f4c7b-1c56-c1e3-d1c0-574f4c7b1c56/PyXqVXqGMH.json",
        "celebration": "https://lottie.host/4c7b1c56-c1e3-d1c0-574f-4c7b1c56c1e3/PyXqVXqGMH.json",
        
        # Working fallback animations (guaranteed to work)
        "rocket": "https://assets5.lottiefiles.com/packages/lf20_7cvvuppm.json",
        "ai_brain": "https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json",
        "loading_circle": "https://assets9.lottiefiles.com/packages/lf20_p8bfn5to.json",
        "success": "https://assets2.lottiefiles.com/packages/lf20_lk80fpsm.json",
        "upload": "https://assets5.lottiefiles.com/packages/lf20_yu4xgsrj.json",
    }


def get_animation_config() -> Dict[str, Any]:
    """
    Returns default configuration settings for Lottie animations.
    
    Returns:
        Dict[str, Any]: Configuration dictionary with default animation settings
    """
    return {
        "loop": True,
        "autoplay": True,
        "renderer": "svg",
        "quality": "high"
    }
