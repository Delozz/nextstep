"""
FastAPI WebSocket server for real-time mock interviews.
Uses chunked turn-based streaming with Gemini 2.5 Flash for cost-effective interviews.
"""

import os
import json
import asyncio
import base64
from typing import Dict, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

from .session_log import SessionLog
from .scoring import InterviewScorer
from .prompts import get_interviewer_prompt, get_available_roles

# Load .env so the API key is available when running standalone
load_dotenv()

# Configure Gemini client
API_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=API_KEY) if API_KEY else None


# Active interview sessions
sessions: Dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("[Interview] Server starting...")
    yield
    print("[Interview] Server shutting down...")
    sessions.clear()


app = FastAPI(
    title="NextStep Mock Interview API",
    description="Real-time mock interview with Gemini AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InterviewConfig(BaseModel):
    """Interview session configuration."""
    target_role: str
    user_name: str = "Candidate"


class InterviewSession:
    """Manages a single interview session."""
    
    def __init__(self, session_id: str, config: InterviewConfig):
        self.session_id = session_id
        self.config = config
        self.log = SessionLog(session_id, config.target_role, config.user_name)
        self.model_name = 'gemini-2.5-flash-lite'
        self.system_prompt = get_interviewer_prompt(self.config.target_role)
        self.conversation_text = ""  # Plain text conversation history
        self.is_active = True
        self.current_question = ""
        
    async def initialize(self) -> str:
        """Initialize the interview and get the first question."""
        # Build initial prompt as a single string
        prompt = f"{self.system_prompt}\n\nThe candidate's name is {self.config.user_name}. Please begin the interview with an introduction and your first question."
        
        response = await client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        
        self.current_question = response.text
        self.conversation_text = f"Interviewer: {self.current_question}"
        self.log.start_turn(self.current_question)
        
        return self.current_question
    
    async def process_turn(self, transcript: str, video_frames: list = None) -> str:
        """
        Process a complete turn (user's answer) and get next question.
        """
        if not self.conversation_text:
            raise ValueError("Session not initialized")
            
        # Log the answer
        self.log.append_transcript(transcript)
        
        # Update conversation as plain text
        self.conversation_text += f"\n\nCandidate: {transcript}"
        
        # Analyze behavior from video if provided (non-blocking, won't crash if it fails)
        if video_frames and len(video_frames) > 0:
            await self._analyze_behavior(video_frames)
        
        # End current turn
        self.log.end_turn()
        
        # Check if interview should end (after ~5 questions)
        if len(self.log.turns) >= 5:
            self.is_active = False
            closing = "Thank you for your time today. That concludes our interview. You'll receive detailed feedback shortly."
            self.conversation_text += f"\n\nInterviewer: {closing}"
            return closing
        
        # Build a single string prompt with full context for the next question
        full_prompt = (
            f"{self.system_prompt}\n\n"
            f"## CONVERSATION SO FAR\n{self.conversation_text}\n\n"
            f"## INSTRUCTION\n"
            f"Based on the candidate's last answer, respond briefly (1-2 sentences of acknowledgment) "
            f"and then ask your next interview question. Keep it conversational and natural."
        )
        
        response = await client.aio.models.generate_content(
            model=self.model_name,
            contents=full_prompt
        )
        
        self.current_question = response.text
        self.conversation_text += f"\n\nInterviewer: {self.current_question}"
        self.log.start_turn(self.current_question)
        
        return self.current_question
    
    async def _analyze_behavior(self, video_frames: list) -> None:
        """Analyze video frames for behavioral observations."""
        if len(video_frames) < 3:
            return
            
        try:
            # Sample a few frames for analysis
            sample_frames = video_frames[::max(1, len(video_frames)//3)][:3]
            
            # Build parts list with text and images using the types API
            parts = [
                types.Part.from_text(
                    "Analyze these video frames from an interview. Rate eye contact (0-1 scale) and note body language. Return JSON: {\"eye_contact\": 0.X, \"notes\": \"brief observation\", \"confidence_indicators\": [\"indicator1\"]}"
                )
            ]
            
            for frame_b64 in sample_frames:
                parts.append(
                    types.Part.from_bytes(
                        data=base64.b64decode(frame_b64),
                        mime_type="image/jpeg"
                    )
                )
            
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=types.Content(role="user", parts=parts)
            )
            
            # Parse behavioral data
            text = response.text.strip()
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            
            data = json.loads(text)
            self.log.add_behavioral_observation(
                eye_contact_score=data.get("eye_contact", 0.5),
                body_language_notes=data.get("notes", ""),
                confidence_indicators=data.get("confidence_indicators", [])
            )
            
        except Exception as e:
            # Non-critical, log and continue
            print(f"[Interview] Behavioral analysis skipped: {e}")
    
    async def end_interview(self) -> Dict:
        """End interview and generate final report."""
        self.is_active = False
        
        if self.log.current_turn:
            self.log.end_turn()
            
        try:
            scorer = InterviewScorer()
            report = await scorer.generate_report(self.log.to_dict())
        except Exception as e:
            print(f"[Interview] Report generation error: {e}")
            report = {
                "final_score": 0,
                "content_score": 0,
                "behavioral_score": 0,
                "overall_impression": f"Report generation failed: {e}",
                "strengths": [],
                "areas_for_improvement": [],
                "question_feedback": [],
                "recommended_next_steps": []
            }
        
        return report


# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok", "service": "NextStep Interview API"}


@app.get("/roles")
async def get_roles():
    """Get available interview roles."""
    return {"roles": get_available_roles()}


@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to show current configuration."""
    # Create a test session to check what model it would use
    test_config = InterviewConfig(target_role="Software Engineer", user_name="Test")
    test_session = InterviewSession("test", test_config)
    return {
        "model_name": test_session.model_name,
        "api_key_configured": bool(API_KEY),
        "api_key_prefix": API_KEY[:10] + "..." if API_KEY else None
    }


@app.post("/session/create")
async def create_session(config: InterviewConfig):
    """Create a new interview session."""
    session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if not API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    session = InterviewSession(session_id, config)
    sessions[session_id] = {
        "session": session,
        "created_at": datetime.now().isoformat()
    }
    
    return {"session_id": session_id, "target_role": config.target_role}


@app.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time interview interaction.
    """
    await websocket.accept()
    
    if session_id not in sessions:
        await websocket.send_json({"type": "error", "message": "Session not found"})
        await websocket.close()
        return
    
    session: InterviewSession = sessions[session_id]["session"]
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            
            if msg_type == "start":
                # Initialize and send first question
                try:
                    question = await session.initialize()
                    await websocket.send_json({
                        "type": "question",
                        "text": question,
                        "turn_number": 1
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Failed to start interview: {e}"
                    })
                
            elif msg_type == "turn":
                # Process answer and get next question
                transcript = data.get("transcript", "")
                video_frames = data.get("video_frames", [])
                
                try:
                    response = await session.process_turn(transcript, video_frames)
                    
                    await websocket.send_json({
                        "type": "question",
                        "text": response,
                        "turn_number": len(session.log.turns) + 1,
                        "is_final": not session.is_active
                    })
                    
                    if not session.is_active:
                        # Auto-generate report when interview ends
                        report = await session.end_interview()
                        await websocket.send_json({
                            "type": "report",
                            "data": report
                        })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error processing answer: {e}"
                    })
                    
            elif msg_type == "end":
                # Force end interview
                try:
                    report = await session.end_interview()
                    await websocket.send_json({
                        "type": "report", 
                        "data": report
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error ending interview: {e}"
                    })
                break
                
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                })
                
    except WebSocketDisconnect:
        print(f"[Interview] Client disconnected from session {session_id}")
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except Exception:
            pass  # Connection already closed
    finally:
        # Cleanup session after disconnect
        if session_id in sessions:
            del sessions[session_id]


# For direct execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
