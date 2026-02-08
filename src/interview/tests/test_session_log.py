"""
Unit tests for the SessionLog class.
"""

import pytest
import time
from src.interview.session_log import SessionLog, Turn, BehavioralObservation


class TestSessionLog:
    """Tests for SessionLog class."""
    
    def test_init(self):
        """Test SessionLog initialization."""
        log = SessionLog("test-123", "Software Engineer", "John Doe")
        
        assert log.session_id == "test-123"
        assert log.target_role == "Software Engineer"
        assert log.user_name == "John Doe"
        assert len(log.turns) == 0
        assert log.current_turn is None
    
    def test_start_turn(self):
        """Test starting a new turn."""
        log = SessionLog("test", "Data Scientist")
        log.start_turn("Tell me about yourself")
        
        assert log.current_turn is not None
        assert log.current_turn.question == "Tell me about yourself"
        assert log.current_turn.answer_transcript == ""
    
    def test_append_transcript(self):
        """Test appending transcript text."""
        log = SessionLog("test", "PM")
        log.start_turn("Question 1")
        log.append_transcript("My answer ")
        log.append_transcript("continues here.")
        
        assert log.current_turn.answer_transcript == "My answer continues here."
    
    def test_end_turn(self):
        """Test ending a turn and saving it."""
        log = SessionLog("test", "PM")
        log.start_turn("Question 1")
        log.append_transcript("Answer 1")
        log.end_turn()
        
        assert len(log.turns) == 1
        assert log.turns[0].question == "Question 1"
        assert log.turns[0].answer_transcript == "Answer 1"
        assert log.current_turn is None
    
    def test_multiple_turns(self):
        """Test multiple interview turns."""
        log = SessionLog("test", "Engineer")
        
        # Turn 1
        log.start_turn("Q1")
        log.append_transcript("A1")
        log.end_turn()
        
        # Turn 2
        log.start_turn("Q2")
        log.append_transcript("A2")
        log.end_turn()
        
        assert len(log.turns) == 2
        assert log.turns[0].question == "Q1"
        assert log.turns[1].question == "Q2"
    
    def test_behavioral_observation(self):
        """Test adding behavioral observations."""
        log = SessionLog("test", "PM")
        log.start_turn("Q1")
        
        log.add_behavioral_observation(
            eye_contact_score=0.8,
            body_language_notes="Good posture, engaged",
            confidence_indicators=["steady voice", "appropriate pauses"]
        )
        
        assert len(log.behavioral_observations) == 1
        assert log.behavioral_observations[0].eye_contact_score == 0.8
        assert "Good posture" in log.behavioral_observations[0].body_language_notes
    
    def test_get_full_transcript(self):
        """Test transcript generation."""
        log = SessionLog("test", "PM")
        
        log.start_turn("Tell me about yourself")
        log.append_transcript("I am a software engineer")
        log.end_turn()
        
        log.start_turn("What are your strengths?")
        log.append_transcript("Problem solving and teamwork")
        log.end_turn()
        
        transcript = log.get_full_transcript()
        
        assert "Q1: Tell me about yourself" in transcript
        assert "A1: I am a software engineer" in transcript
        assert "Q2: What are your strengths?" in transcript
    
    def test_behavioral_summary(self):
        """Test behavioral summary aggregation."""
        log = SessionLog("test", "PM")
        
        log.add_behavioral_observation(0.7, "Note 1")
        log.add_behavioral_observation(0.9, "Note 2")
        log.add_behavioral_observation(0.8, "Note 3")
        
        summary = log.get_behavioral_summary()
        
        assert summary["total_observations"] == 3
        assert 0.79 < summary["avg_eye_contact"] < 0.81  # Should be ~0.8
    
    def test_to_dict(self):
        """Test export to dictionary."""
        log = SessionLog("test-123", "Data Scientist", "Jane")
        log.start_turn("Q1")
        log.append_transcript("A1")
        log.end_turn()
        
        data = log.to_dict()
        
        assert data["session_id"] == "test-123"
        assert data["target_role"] == "Data Scientist"
        assert data["user_name"] == "Jane"
        assert data["total_turns"] == 1
        assert "transcript" in data


class TestTurn:
    """Tests for Turn dataclass."""
    
    def test_turn_creation(self):
        """Test Turn initialization."""
        turn = Turn(
            question="Test question",
            answer_transcript="Test answer",
            answer_audio_duration_sec=5.0,
            video_frames_count=5
        )
        
        assert turn.question == "Test question"
        assert turn.answer_transcript == "Test answer"
        assert turn.answer_audio_duration_sec == 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
