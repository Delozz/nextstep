"""
FastAPI WebSocket server for real-time mock interviews.
Uses Gemini 2.5 Flash Native Audio with Live API for unlimited requests.
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
    description="Real-time mock interview with Gemini AI Live API",
    version="2.0.0",
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


class LiveInterviewSession:
    """Manages a single interview session using Gemini Live API."""
    
    def __init__(self, session_id: str, config: InterviewConfig):
        self.session_id = session_id
        self.config = config
        self.log = SessionLog(session_id, config.target_role, config.user_name)
        self.model_name = 'gemini-2.5-flash-native-audio-preview-12-2025'
        self.system_prompt = get_interviewer_prompt(self.config.target_role)
        self.is_active = True
        self.live_session = None
        self.turn_count = 0
        
        # Live API configuration
        self.config_dict = {
            "response_modalities": ["AUDIO"],  # Native audio output (TTS)
            "system_instruction": f"{self.system_prompt}\n\nThe candidate's name is {self.config.user_name}. Conduct a professional interview with 5-6 questions.",
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": "Kore"  # Professional, clear voice
                    }
                }
            }
        }
    
    async def connect(self):
        """Establish Live API connection."""
        if not client:
            raise ValueError("Gemini client not initialized")
        
        self.live_session = await client.aio.live.connect(
            model=self.model_name,
            config=self.config_dict
        )
        
        # Send initial greeting to start interview
        await self.live_session.send(
            "Please begin the interview with a warm introduction and your first question.",
            end_of_turn=True
        )
        
        return self.live_session
    
    async def send_audio(self, audio_data: bytes, mime_type: str = "audio/pcm"):
        """Send audio chunk to Live API."""
        if not self.live_session:
            raise ValueError("Live session not connected")
        
        await self.live_session.send_realtime_input(
            audio={"data": audio_data, "mime_type": mime_type}
        )
    
    async def send_video_frame(self, frame_data: bytes, mime_type: str = "image/jpeg"):
        """Send video frame for behavioral analysis."""
        if not self.live_session:
            raise ValueError("Live session not connected")
        
        # Live API accepts video frames for multimodal analysis
        await self.live_session.send_realtime_input(
            video={"data": frame_data, "mime_type": mime_type}
        )
    
    async def receive_responses(self):
        """Generator that yields audio responses from Gemini."""
        if not self.live_session:
            raise ValueError("Live session not connected")
        
        turn = self.live_session.receive()
        async for response in turn:
            if response.server_content and response.server_content.model_turn:
                for part in response.server_content.model_turn.parts:
                    # Audio response (PCM data)
                    if part.inline_data and isinstance(part.inline_data.data, bytes):
                        yield {
                            "type": "audio",
                            "data": base64.b64encode(part.inline_data.data).decode('utf-8'),
                            "mime_type": "audio/pcm"
                        }
                    
                    # Text transcript (for logging)
                    if part.text:
                        self.log.append_transcript(f"Interviewer: {part.text}")
                        yield {
                            "type": "transcript",
                            "text": part.text
                        }
                
                # Track turns
                self.turn_count += 1
                
                # Check if interview should end
                if self.turn_count >= 6:
                    self.is_active = False
                    yield {
                        "type": "interview_complete",
                        "message": "Interview complete"
                    }
    
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
        
        # Close Live API session
        if self.live_session:
            await self.live_session.close()
        
        return report


# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok", "service": "NextStep Interview API (Live API)", "version": "2.0"}


@app.get("/roles")
async def get_roles():
    """Get available interview roles."""
    return {"roles": get_available_roles()}


@app.post("/session/create")
async def create_session(config: InterviewConfig):
    """Create a new interview session."""
    session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if not API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    session = LiveInterviewSession(session_id, config)
    sessions[session_id] = {
        "session": session,
        "created_at": datetime.now().isoformat()
    }
    
    return {"session_id": session_id, "target_role": config.target_role}


@app.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time interview with Live API.
    Handles binary audio/video streaming.
    """
    await websocket.accept()
    
    if session_id not in sessions:
        await websocket.send_json({"type": "error", "message": "Session not found"})
        await websocket.close()
        return
    
    session: LiveInterviewSession = sessions[session_id]["session"]
    
    try:
        # Connect to Live API
        await session.connect()
        
        # Start receiving responses in background
        async def receive_and_forward():
            """Receive audio from Gemini and forward to client."""
            try:
                async for response in session.receive_responses():
                    await websocket.send_json(response)
            except Exception as e:
                print(f"[Interview] Error receiving responses: {e}")
        
        # Start background task
        receive_task = asyncio.create_task(receive_and_forward())
        
        # Main loop: receive audio/video from client
        while session.is_active:
            try:
                message = await websocket.receive()
                
                # Handle different message types
                if "bytes" in message:
                    # Binary audio data
                    audio_data = message["bytes"]
                    await session.send_audio(audio_data)
                
                elif "text" in message:
                    # JSON messages (control commands, video frames)
                    data = json.loads(message["text"])
                    msg_type = data.get("type")
                    
                    if msg_type == "video_frame":
                        # Base64 encoded video frame
                        frame_b64 = data.get("frame")
                        frame_data = base64.b64decode(frame_b64)
                        await session.send_video_frame(frame_data)
                    
                    elif msg_type == "end":
                        # User requested to end interview
                        report = await session.end_interview()
                        await websocket.send_json({
                            "type": "report",
                            "data": report
                        })
                        break
                    
                    elif msg_type == "transcript":
                        # Log user's transcript (from browser speech recognition fallback)
                        transcript = data.get("text", "")
                        session.log.append_transcript(f"Candidate: {transcript}")
            
            except WebSocketDisconnect:
                print(f"[Interview] Client disconnected from session {session_id}")
                break
            except Exception as e:
                print(f"[Interview] Error in main loop: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
        
        # Cancel background task
        receive_task.cancel()
        
    except Exception as e:
        print(f"[Interview] Session error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except Exception:
            pass
    finally:
        # Cleanup session
        if session_id in sessions:
            del sessions[session_id]


# For direct execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
