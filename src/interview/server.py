"""
FastAPI WebSocket server for real-time mock interviews.
Uses Gemini 2.5 Flash Native Audio with Live API for bidirectional audio + video streaming.

Based on official Google AI documentation:
- https://ai.google.dev/gemini-api/docs/live
- https://ai.google.dev/gemini-api/docs/live-guide
- https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI.py

Supports:
- Native audio input/output (16kHz input, 24kHz output PCM)
- Video frame input (JPEG @ 1 FPS) for behavioral analysis
- Voice Activity Detection (VAD) for natural interruptions
- Affective dialog (emotion-aware responses)
- Context window compression for longer sessions
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

# Configure Gemini client with v1beta API version for Live API
API_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client(
    api_key=API_KEY,
    http_options={"api_version": "v1beta"}
) if API_KEY else None


# Active interview sessions
sessions: Dict[str, dict] = {}


# Audio format constants (from official docs)
SEND_SAMPLE_RATE = 16000    # Input: 16-bit PCM, 16kHz, mono
RECEIVE_SAMPLE_RATE = 24000  # Output: 24kHz

# Video processing rate
VIDEO_FPS = 1  # 1 frame per second (Live API processes at 1 FPS)

# Model name
MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("[Interview] Gemini 2.5 Flash Native Audio + Video Server starting...")
    print(f"[Interview] API Key configured: {'Yes' if API_KEY else 'No'}")
    yield
    print("[Interview] Server shutting down...")
    sessions.clear()


app = FastAPI(
    title="NextStep Mock Interview API",
    description="Real-time multimodal mock interview with Gemini 2.5 Flash Native Audio + Video",
    version="2.5.1",
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
    enable_video: bool = True  # Enable webcam for behavioral analysis


def build_system_instruction(target_role: str, user_name: str, video_enabled: bool) -> str:
    """Build the complete system instruction for the interview."""
    system_prompt = get_interviewer_prompt(target_role)
    
    video_context = ""
    if video_enabled:
        video_context = """
VIDEO ANALYSIS:
- You can see the candidate via their webcam
- Observe their body language, facial expressions, and engagement
- Note if they maintain eye contact, appear nervous, or seem confident
- Use visual cues to provide better conversational flow
- Include behavioral observations in your assessment"""
    
    return f"""{system_prompt}

INTERVIEW CONTEXT:
- Candidate Name: {user_name}
- Target Role: {target_role}
- Interview Format: Voice-based mock interview with 5-6 questions
{video_context}

INSTRUCTIONS:
1. Begin with a warm, professional greeting and introduce yourself as the interviewer
2. Ask one question at a time and wait for the candidate's response
3. Provide brief, encouraging feedback before moving to the next question
4. Cover a mix of behavioral, technical, and situational questions
5. Conclude with an opportunity for the candidate to ask questions
6. End with a professional closing statement

Maintain a natural, conversational tone throughout the interview.
Adapt your pacing and tone based on the candidate's responses and demeanor."""


def get_live_config(target_role: str, user_name: str, video_enabled: bool) -> types.LiveConnectConfig:
    """
    Build the Live API configuration using types.LiveConnectConfig.
    Based on official Google Cookbook example.
    """
    return types.LiveConnectConfig(
        response_modalities=["AUDIO"],  # Native audio output
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Puck"  # Professional interviewer voice
                )
            )
        ),
        # Context window compression for longer sessions
        context_window_compression=types.ContextWindowCompressionConfig(
            trigger_tokens=25600,
            sliding_window=types.SlidingWindow(target_tokens=12800),
        ),
        # System instruction
        system_instruction=types.Content(
            parts=[types.Part(text=build_system_instruction(target_role, user_name, video_enabled))]
        ),
    )


# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "NextStep Interview API",
        "version": "2.5.1",
        "model": MODEL,
        "features": [
            "Native Audio Live API",
            "Video Frame Analysis",
            "Bidirectional streaming",
            "Voice Activity Detection (VAD)",
            "Affective Dialog",
            "Context Window Compression"
        ],
        "audio": {
            "input_sample_rate": SEND_SAMPLE_RATE,
            "output_sample_rate": RECEIVE_SAMPLE_RATE,
            "format": "16-bit PCM mono"
        },
        "video": {
            "format": "JPEG",
            "recommended_fps": VIDEO_FPS
        }
    }


@app.get("/roles")
async def get_roles():
    """Get available interview roles."""
    return {"roles": get_available_roles()}


@app.post("/session/create")
async def create_session(config: InterviewConfig):
    """Create a new interview session."""
    session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if not API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY not configured. Please set it in your .env file."
        )
    
    # Store session config (actual connection happens in WebSocket)
    sessions[session_id] = {
        "config": config.model_dump(),
        "created_at": datetime.now().isoformat(),
        "log": SessionLog(session_id, config.target_role, config.user_name)
    }
    
    mode = "audio + video" if config.enable_video else "audio only"
    print(f"[Interview] Created session {session_id} ({mode}) for role: {config.target_role}")
    
    return {
        "session_id": session_id,
        "target_role": config.target_role,
        "user_name": config.user_name,
        "model": MODEL,
        "video_enabled": config.enable_video
    }


@app.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time multimodal interview with Gemini Live API.
    
    Protocol:
    - Client sends: JSON messages with audio/video data
    - Server sends: JSON with audio data, transcripts, and control messages
    
    JSON message types from client:
    - {"type": "start"} - Begin the interview
    - {"type": "audio", "data": "base64..."} - Audio chunk (PCM 16kHz)
    - {"type": "video", "data": "base64..."} - Video frame (JPEG)
    - {"type": "text", "text": "..."} - Text input (fallback)
    - {"type": "end"} - End the interview
    
    JSON message types from server:
    - {"type": "connected", "model": "..."}
    - {"type": "audio", "data": "base64...", "sample_rate": 24000}
    - {"type": "transcript", "text": "..."}
    - {"type": "turn_complete"}
    - {"type": "report", "data": {...}}
    - {"type": "error", "message": "..."}
    """
    await websocket.accept()
    print(f"[Interview] WebSocket connected for session {session_id}")
    
    if session_id not in sessions:
        await websocket.send_json({"type": "error", "message": "Session not found"})
        await websocket.close()
        return
    
    session_data = sessions[session_id]
    config = session_data["config"]
    log: SessionLog = session_data["log"]
    
    target_role = config["target_role"]
    user_name = config["user_name"]
    video_enabled = config.get("enable_video", True)
    
    # Queues for bidirectional communication
    outgoing_queue = asyncio.Queue(maxsize=10)  # Audio/video to Gemini
    is_active = True
    turn_count = 0
    
    try:
        # Get Live API configuration
        live_config = get_live_config(target_role, user_name, video_enabled)
        
        # Connect to Gemini Live API using async context manager
        async with client.aio.live.connect(model=MODEL, config=live_config) as gemini_session:
            print(f"[Interview] Gemini Live session established for {session_id}")
            
            await websocket.send_json({
                "type": "connected",
                "model": MODEL,
                "video_enabled": video_enabled
            })
            
            # Task: Receive from Gemini and forward to client
            async def receive_from_gemini():
                nonlocal is_active, turn_count
                try:
                    while is_active:
                        turn = gemini_session.receive()
                        async for response in turn:
                            if not is_active:
                                break
                            
                            # Handle audio data
                            if data := response.data:
                                await websocket.send_json({
                                    "type": "audio",
                                    "data": base64.b64encode(data).decode('utf-8'),
                                    "sample_rate": RECEIVE_SAMPLE_RATE
                                })
                            
                            # Handle text transcript
                            if text := response.text:
                                log.append_transcript(f"Interviewer: {text}")
                                await websocket.send_json({
                                    "type": "transcript",
                                    "text": text
                                })
                        
                        # Turn complete
                        turn_count += 1
                        await websocket.send_json({
                            "type": "turn_complete",
                            "turn_count": turn_count
                        })
                        
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print(f"[Interview] Gemini receive error: {e}")
                    try:
                        await websocket.send_json({"type": "error", "message": str(e)})
                    except Exception:
                        pass
            
            # Task: Send queued audio/video to Gemini
            async def send_to_gemini():
                nonlocal is_active
                try:
                    while is_active:
                        msg = await outgoing_queue.get()
                        
                        if msg["type"] == "audio":
                            await gemini_session.send_realtime_input(
                                audio={"data": msg["data"], "mime_type": "audio/pcm"}
                            )
                        elif msg["type"] == "video":
                            await gemini_session.send_realtime_input(
                                media={"data": msg["data"], "mime_type": "image/jpeg"}
                            )
                        elif msg["type"] == "text":
                            log.append_transcript(f"Candidate: {msg['text']}")
                            await gemini_session.send_client_content(
                                turns=types.Content(parts=[types.Part(text=msg["text"])]),
                                turn_complete=True
                            )
                        elif msg["type"] == "start":
                            await gemini_session.send_client_content(
                                turns=types.Content(
                                    parts=[types.Part(text="Please begin the interview now. Start with a warm greeting and your first question.")]
                                ),
                                turn_complete=True
                            )
                            
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print(f"[Interview] Gemini send error: {e}")
            
            # Task: Receive from WebSocket client
            async def receive_from_client():
                nonlocal is_active
                try:
                    while is_active:
                        message = await websocket.receive()
                        
                        if "text" in message:
                            data = json.loads(message["text"])
                            msg_type = data.get("type")
                            
                            if msg_type == "start":
                                await outgoing_queue.put({"type": "start"})
                            
                            elif msg_type == "audio":
                                audio_b64 = data.get("data", "")
                                audio_data = base64.b64decode(audio_b64)
                                # Drop if queue is full (keep real-time)
                                try:
                                    outgoing_queue.put_nowait({"type": "audio", "data": audio_data})
                                except asyncio.QueueFull:
                                    outgoing_queue.get_nowait()
                                    outgoing_queue.put_nowait({"type": "audio", "data": audio_data})
                            
                            elif msg_type == "video":
                                frame_b64 = data.get("data", "")
                                await outgoing_queue.put({"type": "video", "data": frame_b64})
                            
                            elif msg_type == "text":
                                text = data.get("text", "")
                                await outgoing_queue.put({"type": "text", "text": text})
                            
                            elif msg_type == "end":
                                is_active = False
                                break
                        
                        elif "bytes" in message:
                            # Binary audio data
                            audio_data = message["bytes"]
                            try:
                                outgoing_queue.put_nowait({"type": "audio", "data": audio_data})
                            except asyncio.QueueFull:
                                outgoing_queue.get_nowait()
                                outgoing_queue.put_nowait({"type": "audio", "data": audio_data})
                                
                except WebSocketDisconnect:
                    print(f"[Interview] Client disconnected from {session_id}")
                    is_active = False
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print(f"[Interview] Client receive error: {e}")
                    is_active = False
            
            # Run all tasks concurrently
            receive_gemini_task = asyncio.create_task(receive_from_gemini())
            send_gemini_task = asyncio.create_task(send_to_gemini())
            receive_client_task = asyncio.create_task(receive_from_client())
            
            # Wait for client task to complete (user ends interview or disconnects)
            await receive_client_task
            
            # Cancel other tasks
            is_active = False
            receive_gemini_task.cancel()
            send_gemini_task.cancel()
            
            try:
                await receive_gemini_task
            except asyncio.CancelledError:
                pass
            try:
                await send_gemini_task
            except asyncio.CancelledError:
                pass
            
            # Generate report
            print(f"[Interview] Generating report for {session_id}")
            if log.current_turn:
                log.end_turn()
            
            try:
                scorer = InterviewScorer()
                report = await scorer.generate_report(log.to_dict())
            except Exception as e:
                print(f"[Interview] Report generation error: {e}")
                report = {
                    "final_score": 0,
                    "error": str(e),
                    "message": "Report generation failed"
                }
            
            await websocket.send_json({
                "type": "report",
                "data": report
            })
            
    except Exception as e:
        print(f"[Interview] Session error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        # Cleanup
        if session_id in sessions:
            del sessions[session_id]
        print(f"[Interview] Session {session_id} cleaned up")


# For direct execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
