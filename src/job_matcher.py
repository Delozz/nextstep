import os
import google.generativeai as genai


def get_lifestyle_reality_check(api_key=None, city="", debt=0, lifestyle="Balanced"):
    """
    Agent 1: The Financial Realist.
    Generates a 'Vibe Check' based on the user's debt and lifestyle choice.
    
    Args:
        api_key: Google Gemini API key (loaded from env if not provided)
        city: Target city name
        debt: Student loan debt amount
        lifestyle: Lifestyle preference (Frugal, Balanced, Boujee)
    
    Returns:
        str: AI-generated reality check message
    """
    # Load API key from parameter or environment
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY', '')
    
    if not api_key:
        return "⚠️ Please set GEMINI_API_KEY environment variable or provide api_key parameter."

    # CONFIGURE
    try:
        genai.configure(api_key=api_key)
        # Using Gemini 3 Flash Preview - Latest balanced model (Dec 2025)
        # https://ai.google.dev/gemini-api/docs/models#gemini-3-flash
        model = genai.GenerativeModel('gemini-3-flash-preview')
    except Exception as e:
        return f"Configuration Error: {str(e)}"

    prompt = f"""
    Act as a 'Financial Big Brother' for a new college grad.
    
    User Profile:
    - Target City: {city}
    - Student Loans: ${debt:,}
    - Lifestyle Preference: {lifestyle} (Options: Frugal, Balanced, Boujee)
    
    Task:
    Write a 3-sentence 'Reality Check'.
    1. Can they afford this lifestyle in this city with that debt?
    2. What is the harsh reality (e.g., "You will need 3 roommates")?
    3. End with one helpful tip for that specific city.
    
    Be direct but encouraging. Use a friendly, big-sibling tone.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"LIFESTYLE AGENT ERROR: {e}")
        return "⚠️ AI Error: Check your API Key or Quota."


def get_career_advice(api_key=None, resume_data=None, target_city=""):
    """
    Agent 2: The Career Coach.
    Suggests a specific 'Pivot' to help them succeed in the target city.
    
    Args:
        api_key: Google Gemini API key (loaded from env if not provided)
        resume_data: Dictionary with resume information (skills, major, etc.)
        target_city: Target city for job search
    
    Returns:
        str: AI-generated career advice
    """
    # Load API key from parameter or environment
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY', '')
    
    if not api_key:
        return "⚠️ Please set GEMINI_API_KEY environment variable."
    
    # Handle missing resume data
    if not resume_data:
        resume_data = {}

    try:
        genai.configure(api_key=api_key)
        # Using Gemini 3 Flash Preview - Latest balanced model (Dec 2025)
        # https://ai.google.dev/gemini-api/docs/models#gemini-3-flash
        model = genai.GenerativeModel('gemini-3-flash-preview')
    except Exception as e:
        return f"Configuration Error: {str(e)}"

    # SAFEGUARD: Handle cases where no skills are found
    raw_skills = resume_data.get('skills', [])
    skills = ", ".join(raw_skills) if raw_skills else "General student background"
    major = resume_data.get('major', 'General')

    prompt = f"""
    User is a {major} major looking for a job in {target_city}.
    Their Current Skills: {skills}.
    
    Task:
    1. Suggest 1 specific job title that fits them in {target_city}.
    2. Suggest 1 specific project or certification they should do to increase their salary.
    
    Keep it short and actionable (bullet points).
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"CAREER AGENT ERROR: {e}")
        return "Focus on building a portfolio relevant to local industries."
