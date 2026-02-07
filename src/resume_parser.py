"""
AI-Powered Resume Parser Module using Google Gemini Flash
Person C - Feature Specialist
Uses Gemini AI to intelligently extract skills, experience, and insights from resumes
"""

import os
import json
from typing import Dict, List, Set
import PyPDF2
from io import BytesIO
import google.generativeai as genai


class AIResumeParser:
    """AI-powered resume analysis using Gemini Flash"""

    def __init__(self, api_key: str = None):
        """
        Initialize the AI Resume Parser

        Args:
            api_key: Google Gemini API key (loaded from environment if not provided)
        """
        # Load API key from parameter or environment variable
        if api_key:
            self.api_key = api_key
        else:
            # Try to load from environment
            self.api_key = os.getenv('GEMINI_API_KEY', '')
            if not self.api_key:
                raise ValueError(
                    "GEMINI_API_KEY not found. Please provide api_key parameter or set GEMINI_API_KEY environment variable."
                )

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        # Using Gemini 3 Flash Preview - Latest balanced model (Dec 2025)
        # https://ai.google.dev/gemini-api/docs/models#gemini-3-flash
        self.model = genai.GenerativeModel('gemini-3-flash-preview')

        self.raw_text = ""
        self.ai_analysis = {}

    def extract_text_from_pdf(self, uploaded_file) -> str:
        """
        Extract text from uploaded PDF file

        Args:
            uploaded_file: Streamlit UploadedFile object or file path

        Returns:
            str: Extracted text from PDF
        """
        try:
            # Handle different input types
            if isinstance(uploaded_file, str):
                # File path
                with open(uploaded_file, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            else:
                # Streamlit UploadedFile
                pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

            self.raw_text = text
            return text

        except Exception as e:
            return f"Error parsing PDF: {str(e)}"

    def analyze_with_ai(self, text: str = None) -> Dict:
        """
        Use Gemini 3 Flash AI to analyze resume and extract structured information

        Args:
            text: Resume text (uses self.raw_text if not provided)

        Returns:
            Dictionary with AI-extracted information
        """
        if text is None:
            text = self.raw_text

        if not text or len(text.strip()) < 50:
            return {"error": "Resume text too short or empty"}

        # Craft the AI prompt
        prompt = f"""You are an expert resume analyzer and career counselor. Analyze the following resume and extract key information in JSON format.

RESUME TEXT:
{text}

INSTRUCTIONS:
Extract the following information and return ONLY a valid JSON object (no markdown, no explanations):

{{
    "personal_info": {{
        "name": "candidate's full name or 'Unknown'",
        "email": "email address or null",
        "phone": "phone number or null",
        "location": "city, state or null"
    }},
    "education": {{
        "highest_degree": "PhD, Master's, Bachelor's, Associate's, High School, or Unknown",
        "major": "field of study or null",
        "university": "school name or null",
        "graduation_year": "year or null"
    }},
    "experience": {{
        "total_years": estimated total years of professional experience (number),
        "current_title": "most recent job title or null",
        "previous_titles": ["list of previous job titles"],
        "companies": ["list of companies worked at"]
    }},
    "technical_skills": [
        "list of all technical/hard skills mentioned (programming languages, tools, technologies, certifications)"
    ],
    "soft_skills": [
        "list of soft skills mentioned (leadership, communication, teamwork, etc.)"
    ],
    "projects": [
        "notable projects mentioned (brief description)"
    ],
    "achievements": [
        "key achievements, awards, or metrics mentioned"
    ],
    "career_summary": "2-3 sentence summary of this person's career trajectory and strengths",
    "recommended_roles": [
        "3-5 job titles this person would be qualified for"
    ],
    "skill_level": "Entry, Mid, Senior, or Expert based on experience and skills",
    "industries": [
        "industries they have experience in or would fit well in"
    ]
}}

Be thorough but accurate. If information is not present, use null or empty arrays. For years of experience, analyze date ranges mentioned."""

        try:
            # Call Gemini 3 Flash API
            response = self.model.generate_content(prompt)

            # Parse the JSON response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text.replace(
                    '```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()

            # Parse JSON
            analysis = json.loads(response_text)
            self.ai_analysis = analysis

            return analysis

        except json.JSONDecodeError as e:
            # If JSON parsing fails, return raw response for debugging
            return {
                "error": "Failed to parse AI response as JSON",
                "raw_response": response.text,
                "parse_error": str(e)
            }
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}

    def get_skills_for_matching(self) -> Set[str]:
        """
        Extract all skills in a format suitable for job matching

        Returns:
            Set of all skills (technical + soft) in lowercase
        """
        if not self.ai_analysis:
            return set()

        skills = set()

        # Add technical skills
        tech_skills = self.ai_analysis.get('technical_skills', [])
        skills.update([skill.lower() for skill in tech_skills])

        # Add soft skills
        soft_skills = self.ai_analysis.get('soft_skills', [])
        skills.update([skill.lower() for skill in soft_skills])

        return skills

    def get_resume_summary(self, uploaded_file) -> Dict:
        """
        Complete AI-powered analysis of resume

        Args:
            uploaded_file: Streamlit UploadedFile object or file path

        Returns:
            Dictionary with comprehensive resume analysis
        """
        # Extract text
        text = self.extract_text_from_pdf(uploaded_file)

        if text.startswith("Error"):
            return {"error": text}

        # Analyze with AI
        analysis = self.analyze_with_ai(text)

        if "error" in analysis:
            return analysis

        # Format for compatibility with existing code
        return {
            "ai_analysis": analysis,
            "total_skills": len(analysis.get('technical_skills', [])) + len(analysis.get('soft_skills', [])),
            "tech_skills": analysis.get('technical_skills', []),
            "soft_skills": analysis.get('soft_skills', []),
            "experience_years": analysis.get('experience', {}).get('total_years', 0),
            "education_level": analysis.get('education', {}).get('highest_degree', 'Unknown'),
            "career_summary": analysis.get('career_summary', ''),
            "recommended_roles": analysis.get('recommended_roles', []),
            "skill_level": analysis.get('skill_level', 'Unknown'),
            "name": analysis.get('personal_info', {}).get('name', 'Unknown'),
            "current_title": analysis.get('experience', {}).get('current_title', 'Unknown'),
            "raw_text_preview": text[:300] + "..." if len(text) > 300 else text
        }

    def get_improvement_suggestions(self) -> List[str]:
        """
        Generate AI-powered resume improvement suggestions

        Returns:
            List of suggestions to improve the resume
        """
        if not self.raw_text:
            return []

        prompt = f"""You are a professional resume coach. Review this resume and provide 3-5 specific, actionable suggestions to improve it.

RESUME:
{self.raw_text}

Provide suggestions in JSON array format:
["suggestion 1", "suggestion 2", "suggestion 3"]

Focus on:
- Missing important sections
- Skills that should be highlighted more
- Quantifiable achievements
- Keywords for ATS optimization
- Formatting improvements"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean up markdown
            if '```' in response_text:
                response_text = response_text.replace(
                    '```json', '').replace('```', '').strip()

            suggestions = json.loads(response_text)
            return suggestions

        except:
            return ["Unable to generate suggestions at this time"]


def parse_resume_with_ai(uploaded_file, api_key: str = None) -> Dict:
    """
    Convenience function for AI-powered resume parsing

    Args:
        uploaded_file: Streamlit UploadedFile object or file path
        api_key: Google Gemini API key (uses hardcoded key if not provided)

    Returns:
        Dictionary with parsed resume data
    """
    parser = AIResumeParser(api_key=api_key)
    return parser.get_resume_summary(uploaded_file)
