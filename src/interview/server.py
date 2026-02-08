"""
FastAPI WebSocket server for real-time mock interviews.
Uses Gemini 2.0 Flash Native Live API for low-latency multimodal interviews.
"""

import os
import json
import asyncio
import base64
from typing import Dict, Optional, Any
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
client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1alpha'}) if API_KEY else None


# Active interview sessions
sessions: Dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("[Interview] Native Live Server starting...")
    yield
    print("[Interview] Server shutting down...")
    sessions.clear()


app = FastAPI(
    title="NextStep Mock Interview API (Native Live)",
    description="Real-time native multimodal mock interview with Gemini AI",
    version="2.0.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InterviewConfig(BaseModel):
    """Interview session configuration."""
    target_role: str
    user_name: str = "Candidate"
    mode: str = "native"  # "native" for Live API, "classic" for turn-based


class NativeInterviewSession:
    """Manages a Gemini 2.0 Native Live API session."""
    
    def __init__(self, session_id: str, config: InterviewConfig):
        self.session_id = session_id
        self.config = config
        self.log = SessionLog(session_id, config.target_role, config.user_name)
        # Using the latest experimental flash model for Live API
        self.model_name = 'gemini-2.0-flash-exp' 
        self.system_prompt = get_interviewer_prompt(self.config.target_role)
        self.is_active = True
        self.gemini_session = None
        
    async def get_live_config(self):
        """Build the configuration for the Live API."""
        return types.LiveConnectConfig(
            model=self.model_name,
            system_instruction=types.Content(
                parts=[types.Part.from_text(self.system_prompt)]
            ),
            generation_config=types.GenerationConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Puck"  # Professional interviewer voice
                        )
                    )
                )
            )
        )

    async def end_interview(self) -> Dict:
        """End interview and generate final report."""
        self.is_active = False
        try:
            scorer = InterviewScorer()
            report = await scorer.generate_report(self.log.to_dict())
        except Exception as e:
            print(f"[Interview] Report generation error: {e}")
            report = {"error": str(e)}
        return report


# --- API Endpoints ---

@app.get("/")
async def root():
    return {"status": "ok", "service": "NextStep Native Interview API"}


@app.get("/roles")
async def get_roles():
    return {"roles": get_available_roles()}


@app.post("/session/create")
async def create_session(config: InterviewConfig):
    session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if not API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    # We use NativeInterviewSession for everyone now since the user requested "Native"
    session = NativeInterviewSession(session_id, config)
    sessions[session_id] = {
        "session": session,
        "created_at": datetime.now().isoformat()
    }
    return {"session_id": session_id, "target_role": config.target_role}


@app.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time native interview interaction.
    Proxies between the client and Gemini Multimodal Live API.
    """
    await websocket.accept()
    
    if session_id not in sessions:
        await websocket.send_json({"type": "error", "message": "Session not found"})
        await websocket.close()
        return
    
    session_obj: NativeInterviewSession = sessions[session_id]["session"]
    
    # Connect to Gemini Live API
    try:
        config = await session_obj.get_live_config()
        
        async with client.aio.models.live.connect(model=session_obj.model_name, config=config) as gemini_session:
            session_obj.gemini_session = gemini_session
            
            # --- Handler for Gemini -> Client ---
            async def receive_from_gemini():
                try:
                    async for message in gemini_session:
                        # message is a types.LiveServerEvent
                        
                        # 1. Handle Audio Output
                        if message.server_content and message.server_content.model_turn:
                            for part in message.server_content.model_turn.parts:
                                if part.inline_data:
                                    # Send raw audio bytes to client
                                    audio_b64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                                    await websocket.send_json({
                                        "type": "audio",
                                        "data": audio_b64
                                    })
                        
                        # 2. Handle Text Transcription (of what Gemini is saying)
                        # The Live API can also return text parts if configured or as a fallback
                        if message.server_content and message.server_content.model_turn:
                            for part in message.server_content.model_turn.parts:
                                if part.text:
                                    await websocket.send_json({
                                        "type": "text",
                                        "text": part.text
                                    })
                                    session_obj.log.append_transcript(f"Interviewer: {part.text}")
                        
                        # 3. Handle User Transcription (from Gemini's internal STT)
                        if message.server_content and message.server_content.turn_complete:
                            # Signal to frontend that a turn is done
                            await websocket.send_json({"type": "turn_complete"})

                except Exception as e:
                    print(f"[Interview] Gemini receive error: {e}")
                    await websocket.send_json({"type": "error", "message": f"Gemini connection lost: {e}"})

            # --- Handler for Client -> Gemini ---
            async def send_to_gemini():
                try:
                    while True:
                        data = await websocket.receive_json()
                        msg_type = data.get("type")
                        
                        if msg_type == "audio":
                            # Client sending raw mic audio
                            audio_data = base64.b64decode(data.get("data", ""))
                            await gemini_session.send(
                                input=types.LiveClientRealtimeInput(
                                    media_chunks=[types.Blob(data=audio_data, mime_type="audio/pcm")]
                                )
                            )
                        
                        elif msg_type == "text":
                            # Client sending text input
                            text_input = data.get("text", "")
                            await gemini_session.send(input=text_input, end_of_turn=True)
                            session_obj.log.append_transcript(f"User: {text_input}")

                        elif msg_type == "end":
                            report = await session_obj.end_interview()
                            await websocket.send_json({"type": "report", "data": report})
                            break
                            
                except WebSocketDisconnect:
                    print(f"[Interview] Client disconnected")
                except Exception as e:
                    print(f"[Interview] Client send error: {e}")

            # Run both handlers concurrently
            await asyncio.gather(receive_from_gemini(), send_to_gemini())
            
    except Exception as e:
        print(f"[Interview] Session error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        if session_id in sessions:
            del sessions[session_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
