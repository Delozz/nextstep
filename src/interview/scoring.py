"""
70/30 Scoring Algorithm for Mock Interviews.
- 70% Content Quality (logic, relevance, depth)
- 30% Behavioral Delivery (eye contact, tone, confidence)
"""

import os
import json
from typing import Dict, List, Optional
from google import genai


class InterviewScorer:
    """
    Generates final interview scores and feedback using Gemini.
    Implements the 70/30 weighting algorithm.
    """
    
    CONTENT_WEIGHT = 0.70
    BEHAVIORAL_WEIGHT = 0.30
    
    def __init__(self, api_key: str = None):
        """Initialize scorer with Gemini API."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY required for scoring")
        
        # Use new google.genai client
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-2.5-flash'
        
    async def generate_report(self, session_data: Dict) -> Dict:
        """
        Generate comprehensive interview report with 70/30 scoring.
        
        Args:
            session_data: Output from SessionLog.to_dict()
            
        Returns:
            Complete scoring report with feedback
        """
        # Build the analysis prompt
        prompt = self._build_scoring_prompt(session_data)
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            result = self._parse_response(response.text)
            
            # Apply 70/30 weighting
            content_score = result.get("content_score", 50)
            behavioral_score = result.get("behavioral_score", 50)
            
            final_score = (
                content_score * self.CONTENT_WEIGHT +
                behavioral_score * self.BEHAVIORAL_WEIGHT
            )
            
            result["final_score"] = round(final_score, 1)
            result["weight_breakdown"] = {
                "content": {"score": content_score, "weight": "70%", "contribution": round(content_score * self.CONTENT_WEIGHT, 1)},
                "behavioral": {"score": behavioral_score, "weight": "30%", "contribution": round(behavioral_score * self.BEHAVIORAL_WEIGHT, 1)}
            }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "final_score": 0,
                "content_score": 0,
                "behavioral_score": 0
            }
    
    def _build_scoring_prompt(self, session_data: Dict) -> str:
        """Build the Gemini prompt for interview scoring."""
        return f"""You are an expert interview coach evaluating a mock interview for the role of {session_data['target_role']}.

## INTERVIEW TRANSCRIPT
{session_data['transcript']}

## BEHAVIORAL OBSERVATIONS
- Average Eye Contact Score: {session_data['behavioral_summary'].get('avg_eye_contact', 0.5):.2f}/1.0
- Confidence Indicators: {', '.join(session_data['behavioral_summary'].get('confidence_indicators', ['none observed']))}
- Notes: {'; '.join(session_data['behavioral_summary'].get('notes', [])[:3])}

## YOUR TASK
Evaluate this interview and return a JSON object with:

{{
    "content_score": <0-100 score for answer quality, logic, relevance, depth>,
    "behavioral_score": <0-100 score for delivery, eye contact, confidence, tone>,
    "overall_impression": "<2-3 sentence summary>",
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "areas_for_improvement": ["<area 1>", "<area 2>", "<area 3>"],
    "question_feedback": [
        {{"question": "<Q1>", "score": <0-100>, "feedback": "<specific feedback>"}},
        ...
    ],
    "recommended_next_steps": ["<action 1>", "<action 2>"]
}}

SCORING GUIDELINES:
- Content (70% weight): Evaluate clarity, structure, relevance to the role, use of examples, technical accuracy
- Behavioral (30% weight): Eye contact consistency, vocal confidence, body language, engagement level

Return ONLY valid JSON, no markdown or explanations."""

    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini response into structured data."""
        # Clean up response
        text = response_text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Return default structure if parsing fails
            return {
                "content_score": 50,
                "behavioral_score": 50,
                "overall_impression": "Unable to parse detailed feedback.",
                "strengths": [],
                "areas_for_improvement": [],
                "question_feedback": [],
                "recommended_next_steps": []
            }
    
    def generate_quick_feedback(self, transcript: str, target_role: str) -> str:
        """Generate quick text-only feedback (synchronous, for testing)."""
        prompt = f"""Briefly evaluate this interview answer for a {target_role} position:

{transcript[:1000]}

Provide 2-3 sentences of constructive feedback."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Feedback generation failed: {e}"
