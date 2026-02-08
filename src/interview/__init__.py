# Interview module initialization
"""
Real-time mock interview feature using Gemini 2.5 Flash with chunked turn-based streaming.
Cost-optimized approach: ~$2/interview with 1-2 sec latency.
"""

from .session_log import SessionLog
from .scoring import InterviewScorer

__all__ = ['SessionLog', 'InterviewScorer']
