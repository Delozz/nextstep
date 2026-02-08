"""
Session logging for mock interview feature.
Captures transcript, behavioral observations, and timing data.
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Turn:
    """Represents a single interview turn (question + answer)."""
    question: str
    answer_transcript: str
    answer_audio_duration_sec: float
    video_frames_count: int
    behavioral_notes: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    @property
    def response_time_sec(self) -> float:
        """Time from question end to answer start."""
        if self.end_time:
            return self.end_time - self.start_time
        return 0.0


@dataclass
class BehavioralObservation:
    """Behavioral observation from video analysis."""
    timestamp: float
    eye_contact_score: float  # 0-1
    body_language_notes: str
    confidence_indicators: List[str] = field(default_factory=list)


class SessionLog:
    """
    Manages interview session state and logging.
    Accumulates transcript, behavioral data, and timing for final scoring.
    """
    
    def __init__(self, session_id: str, target_role: str, user_name: str = "Candidate"):
        self.session_id = session_id
        self.target_role = target_role
        self.user_name = user_name
        self.created_at = datetime.now()
        self.turns: List[Turn] = []
        self.behavioral_observations: List[BehavioralObservation] = []
        self.current_turn: Optional[Turn] = None
        self._audio_buffer: bytes = b""
        self._video_frames: List[str] = []  # base64 frames
        
    def start_turn(self, question: str) -> None:
        """Start a new interview turn with the given question."""
        if self.current_turn:
            self.end_turn()
        self.current_turn = Turn(
            question=question,
            answer_transcript="",
            answer_audio_duration_sec=0.0,
            video_frames_count=0
        )
        
    def append_transcript(self, text: str) -> None:
        """Append transcribed text to the current turn."""
        if self.current_turn:
            self.current_turn.answer_transcript += text
            
    def append_audio_chunk(self, audio_bytes: bytes, duration_sec: float) -> None:
        """Append audio chunk to buffer."""
        self._audio_buffer += audio_bytes
        if self.current_turn:
            self.current_turn.answer_audio_duration_sec += duration_sec
            
    def append_video_frame(self, frame_base64: str) -> None:
        """Append video frame for behavioral analysis."""
        self._video_frames.append(frame_base64)
        if self.current_turn:
            self.current_turn.video_frames_count += 1
            
    def add_behavioral_observation(
        self, 
        eye_contact_score: float, 
        body_language_notes: str,
        confidence_indicators: List[str] = None
    ) -> None:
        """Add a behavioral observation from video analysis."""
        observation = BehavioralObservation(
            timestamp=time.time(),
            eye_contact_score=eye_contact_score,
            body_language_notes=body_language_notes,
            confidence_indicators=confidence_indicators or []
        )
        self.behavioral_observations.append(observation)
        if self.current_turn:
            self.current_turn.behavioral_notes.append(body_language_notes)
            
    def end_turn(self) -> None:
        """End the current turn and save it."""
        if self.current_turn:
            self.current_turn.end_time = time.time()
            self.turns.append(self.current_turn)
            self.current_turn = None
            self._audio_buffer = b""
            self._video_frames = []
            
    def get_full_transcript(self) -> str:
        """Get the complete interview transcript."""
        lines = []
        for i, turn in enumerate(self.turns, 1):
            lines.append(f"Q{i}: {turn.question}")
            lines.append(f"A{i}: {turn.answer_transcript}")
            lines.append("")
        return "\n".join(lines)
    
    def get_behavioral_summary(self) -> Dict:
        """Get aggregated behavioral metrics."""
        if not self.behavioral_observations:
            return {
                "avg_eye_contact": 0.5,
                "total_observations": 0,
                "confidence_indicators": []
            }
            
        avg_eye_contact = sum(o.eye_contact_score for o in self.behavioral_observations) / len(self.behavioral_observations)
        all_indicators = []
        for o in self.behavioral_observations:
            all_indicators.extend(o.confidence_indicators)
            
        return {
            "avg_eye_contact": avg_eye_contact,
            "total_observations": len(self.behavioral_observations),
            "confidence_indicators": list(set(all_indicators)),
            "notes": [o.body_language_notes for o in self.behavioral_observations[-5:]]  # Last 5
        }
    
    def to_dict(self) -> Dict:
        """Export session data for scoring."""
        return {
            "session_id": self.session_id,
            "target_role": self.target_role,
            "user_name": self.user_name,
            "created_at": self.created_at.isoformat(),
            "total_turns": len(self.turns),
            "total_duration_sec": sum(t.answer_audio_duration_sec for t in self.turns),
            "transcript": self.get_full_transcript(),
            "behavioral_summary": self.get_behavioral_summary(),
            "turns": [
                {
                    "question": t.question,
                    "answer": t.answer_transcript,
                    "duration_sec": t.answer_audio_duration_sec,
                    "behavioral_notes": t.behavioral_notes
                }
                for t in self.turns
            ]
        }
