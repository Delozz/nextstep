/**
 * InterviewRoom Component
 * Main interview interface with camera, microphone, and real-time AI interaction.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useMediaCapture } from './useMediaCapture';
import { InterviewReport } from './InterviewReport';
import type {
    InterviewConfig,
    InterviewStatus,
    WebSocketMessage,
    InterviewReport as ReportData
} from './types';

interface InterviewRoomProps {
    serverUrl?: string;
    availableRoles?: string[];
    userName?: string;
    onComplete?: (report: ReportData) => void;
    onExit?: () => void;
}

// Default roles if not provided
const DEFAULT_ROLES = [
    'Software Engineer',
    'Data Scientist',
    'Quant',
    'Product Manager',
    'Cybersecurity Analyst',
];

export const InterviewRoom: React.FC<InterviewRoomProps> = ({
    serverUrl = 'ws://localhost:8000',
    availableRoles = DEFAULT_ROLES,
    userName = 'Candidate',
    onComplete,
    onExit,
}) => {
    // State
    const [status, setStatus] = useState<InterviewStatus>('idle');
    const [selectedRole, setSelectedRole] = useState<string>(availableRoles[0]);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [currentQuestion, setCurrentQuestion] = useState<string>('');
    const [turnNumber, setTurnNumber] = useState<number>(0);
    const [transcript, setTranscript] = useState<string>('');
    const [report, setReport] = useState<ReportData | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [videoFrames, setVideoFrames] = useState<string[]>([]);

    // Refs
    const wsRef = useRef<WebSocket | null>(null);
    const recognitionRef = useRef<any>(null);
    const frameIntervalRef = useRef<number | null>(null);

    // Media capture hook
    const {
        state: mediaState,
        videoRef,
        startCapture,
        stopCapture,
        getVideoFrame,
        isSpeaking,
    } = useMediaCapture({
        videoFps: 1,
        vadThreshold: 0.01,
        silenceTimeout: 2000, // 2 seconds of silence = end of turn
    });

    // Initialize speech recognition
    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = true;
            recognitionRef.current.interimResults = true;
            recognitionRef.current.lang = 'en-US';

            recognitionRef.current.onresult = (event: any) => {
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript + ' ';
                    }
                }
                if (finalTranscript) {
                    setTranscript(prev => prev + finalTranscript);
                }
            };

            recognitionRef.current.onerror = (event: any) => {
                console.error('Speech recognition error:', event.error);
            };
        }
    }, []);

    // Capture video frames at 1 FPS
    useEffect(() => {
        if (status === 'listening' && mediaState.isCapturing) {
            frameIntervalRef.current = window.setInterval(() => {
                const frame = getVideoFrame();
                if (frame) {
                    setVideoFrames(prev => [...prev.slice(-30), frame]); // Keep last 30 frames
                }
            }, 1000);
        }

        return () => {
            if (frameIntervalRef.current) {
                clearInterval(frameIntervalRef.current);
            }
        };
    }, [status, mediaState.isCapturing, getVideoFrame]);

    // Handle end of speech (VAD detected silence)
    useEffect(() => {
        if (status === 'listening' && !isSpeaking && transcript.length > 10) {
            // User stopped speaking, send turn
            handleSendTurn();
        }
    }, [isSpeaking, status, transcript]);

    // Create session
    const createSession = async (): Promise<string> => {
        const response = await fetch(`${serverUrl.replace('ws', 'http')}/session/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_role: selectedRole,
                user_name: userName,
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to create session');
        }

        const data = await response.json();
        return data.session_id;
    };

    // Connect WebSocket
    const connectWebSocket = useCallback((sessionId: string) => {
        const ws = new WebSocket(`${serverUrl}/ws/interview/${sessionId}`);

        ws.onopen = () => {
            setStatus('ready');
            // Start the interview
            ws.send(JSON.stringify({ type: 'start' }));
        };

        ws.onmessage = (event) => {
            const message: WebSocketMessage = JSON.parse(event.data);

            switch (message.type) {
                case 'question':
                    setCurrentQuestion(message.text || '');
                    setTurnNumber(message.turnNumber || 0);
                    setStatus('listening');
                    setTranscript('');
                    setVideoFrames([]);

                    // Speak the question using TTS
                    if ('speechSynthesis' in window && message.text) {
                        const utterance = new SpeechSynthesisUtterance(message.text);
                        utterance.rate = 0.9;
                        window.speechSynthesis.speak(utterance);
                    }

                    // Start speech recognition
                    if (recognitionRef.current) {
                        try {
                            recognitionRef.current.start();
                        } catch (e) {
                            // Already started
                        }
                    }

                    if (message.isFinal) {
                        setStatus('complete');
                    }
                    break;

                case 'report':
                    setReport(message.data || null);
                    setStatus('complete');
                    if (message.data && onComplete) {
                        onComplete(message.data);
                    }
                    break;

                case 'error':
                    setError(message.message || 'Unknown error');
                    setStatus('error');
                    break;
            }
        };

        ws.onerror = () => {
            setError('WebSocket connection failed');
            setStatus('error');
        };

        ws.onclose = () => {
            if (status !== 'complete' && status !== 'error') {
                setError('Connection closed unexpectedly');
                setStatus('error');
            }
        };

        wsRef.current = ws;
    }, [serverUrl, status, onComplete]);

    // Start interview
    const handleStart = async () => {
        try {
            setStatus('connecting');
            setError(null);

            await startCapture();

            const newSessionId = await createSession();
            setSessionId(newSessionId);

            connectWebSocket(newSessionId);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to start interview');
            setStatus('error');
        }
    };

    // Send turn to server
    const handleSendTurn = () => {
        if (!wsRef.current || status !== 'listening') return;

        // Stop speech recognition
        if (recognitionRef.current) {
            recognitionRef.current.stop();
        }

        setStatus('processing');

        wsRef.current.send(JSON.stringify({
            type: 'turn',
            transcript: transcript,
            video_frames: videoFrames.slice(-10), // Send last 10 frames for analysis
        }));
    };

    // End interview
    const handleEndInterview = () => {
        if (wsRef.current) {
            wsRef.current.send(JSON.stringify({ type: 'end' }));
        }
        stopCapture();
        if (recognitionRef.current) {
            recognitionRef.current.stop();
        }
    };

    // Reset for new interview
    const handleRetry = () => {
        setStatus('idle');
        setReport(null);
        setCurrentQuestion('');
        setTranscript('');
        setVideoFrames([]);
        setTurnNumber(0);
        setError(null);
        stopCapture();
    };

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
            stopCapture();
        };
    }, [stopCapture]);

    // Render report if complete
    if (status === 'complete' && report) {
        return (
            <InterviewReport
                report={report}
                onRetry={handleRetry}
                onClose={onExit}
            />
        );
    }

    return (
        <div className="interview-room">
            <style>{`
        .interview-room {
          background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
          border-radius: 16px;
          padding: 32px;
          color: white;
          font-family: 'Inter', -apple-system, sans-serif;
          min-height: 600px;
          display: flex;
          flex-direction: column;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
        }

        .header h1 {
          margin: 0;
          color: #00FF94;
        }

        .status-badge {
          padding: 8px 16px;
          border-radius: 20px;
          font-size: 14px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .status-idle { background: rgba(255,255,255,0.1); }
        .status-connecting { background: #FFA500; color: #000; }
        .status-ready { background: #00FF94; color: #000; }
        .status-listening { background: #00D9FF; color: #000; animation: pulse 1s infinite; }
        .status-processing { background: #9D4EDD; animation: pulse 0.5s infinite; }
        .status-error { background: #FF4B4B; }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }

        .setup-panel {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 24px;
        }

        .role-selector {
          width: 100%;
          max-width: 400px;
        }

        .role-selector label {
          display: block;
          margin-bottom: 8px;
          font-size: 14px;
          opacity: 0.8;
        }

        .role-selector select {
          width: 100%;
          padding: 12px 16px;
          border-radius: 8px;
          background: rgba(255,255,255,0.1);
          border: 2px solid rgba(255,255,255,0.2);
          color: white;
          font-size: 16px;
          cursor: pointer;
        }

        .role-selector select:focus {
          outline: none;
          border-color: #00FF94;
        }

        .start-btn {
          padding: 16px 48px;
          font-size: 18px;
          font-weight: 700;
          background: linear-gradient(135deg, #00FF94 0%, #00D9FF 100%);
          color: #0a0e27;
          border: none;
          border-radius: 12px;
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .start-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0, 255, 148, 0.3);
        }

        .start-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
        }

        .interview-panel {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .video-container {
          position: relative;
          width: 100%;
          max-width: 640px;
          margin: 0 auto 24px;
          border-radius: 12px;
          overflow: hidden;
          background: #000;
        }

        .video-container video {
          width: 100%;
          transform: scaleX(-1);
        }

        .turn-indicator {
          position: absolute;
          top: 16px;
          left: 16px;
          background: rgba(0,0,0,0.7);
          padding: 8px 16px;
          border-radius: 20px;
          font-size: 14px;
        }

        .audio-indicator {
          position: absolute;
          bottom: 16px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          gap: 4px;
        }

        .audio-bar {
          width: 4px;
          background: #00FF94;
          border-radius: 2px;
          transition: height 0.1s;
        }

        .question-display {
          background: rgba(0, 255, 148, 0.1);
          border-left: 4px solid #00FF94;
          padding: 20px;
          border-radius: 0 12px 12px 0;
          margin-bottom: 24px;
        }

        .question-display h3 {
          margin: 0 0 8px 0;
          font-size: 14px;
          opacity: 0.7;
        }

        .question-display p {
          margin: 0;
          font-size: 18px;
          line-height: 1.5;
        }

        .transcript-area {
          background: rgba(255,255,255,0.05);
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 24px;
          min-height: 100px;
        }

        .transcript-area h4 {
          margin: 0 0 12px 0;
          font-size: 14px;
          opacity: 0.7;
        }

        .transcript-area p {
          margin: 0;
          font-size: 16px;
          line-height: 1.6;
          opacity: 0.9;
        }

        .controls {
          display: flex;
          gap: 16px;
          justify-content: center;
        }

        .end-btn {
          padding: 12px 32px;
          font-size: 16px;
          font-weight: 600;
          background: #FF4B4B;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
        }

        .end-btn:hover {
          background: #cc3333;
        }

        .error-message {
          background: rgba(255, 75, 75, 0.2);
          border: 1px solid #FF4B4B;
          padding: 16px;
          border-radius: 8px;
          margin-bottom: 16px;
        }
      `}</style>

            <div className="header">
                <h1>🎤 Mock Interview</h1>
                <span className={`status-badge status-${status}`}>
                    {status === 'idle' && '⏸️ Ready'}
                    {status === 'connecting' && '🔄 Connecting...'}
                    {status === 'ready' && '✅ Connected'}
                    {status === 'listening' && '🎙️ Listening...'}
                    {status === 'processing' && '🤖 Processing...'}
                    {status === 'error' && '❌ Error'}
                </span>
            </div>

            {error && (
                <div className="error-message">
                    ⚠️ {error}
                </div>
            )}

            {status === 'idle' && (
                <div className="setup-panel">
                    <h2>Prepare for Your Interview</h2>

                    <div className="role-selector">
                        <label>Select Interview Role</label>
                        <select
                            value={selectedRole}
                            onChange={(e) => setSelectedRole(e.target.value)}
                        >
                            {availableRoles.map(role => (
                                <option key={role} value={role}>{role}</option>
                            ))}
                        </select>
                    </div>

                    <p style={{ textAlign: 'center', opacity: 0.7, maxWidth: 400 }}>
                        The AI interviewer will ask 4-5 questions. Speak naturally and take your time.
                        You'll receive detailed feedback at the end.
                    </p>

                    <button
                        className="start-btn"
                        onClick={handleStart}
                        disabled={status !== 'idle'}
                    >
                        🚀 Start Interview
                    </button>
                </div>
            )}

            {(status === 'connecting' || status === 'ready' || status === 'listening' || status === 'processing') && (
                <div className="interview-panel">
                    <div className="video-container">
                        <video ref={videoRef} autoPlay muted playsInline />
                        <div className="turn-indicator">
                            Question {turnNumber}/5
                        </div>
                        {status === 'listening' && (
                            <div className="audio-indicator">
                                {[...Array(5)].map((_, i) => (
                                    <div
                                        key={i}
                                        className="audio-bar"
                                        style={{
                                            height: isSpeaking
                                                ? `${20 + Math.random() * 30}px`
                                                : '8px'
                                        }}
                                    />
                                ))}
                            </div>
                        )}
                    </div>

                    {currentQuestion && (
                        <div className="question-display">
                            <h3>🤖 Interviewer</h3>
                            <p>{currentQuestion}</p>
                        </div>
                    )}

                    <div className="transcript-area">
                        <h4>📝 Your Response</h4>
                        <p>{transcript || 'Start speaking when you\'re ready...'}</p>
                    </div>

                    <div className="controls">
                        <button className="end-btn" onClick={handleEndInterview}>
                            End Interview
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default InterviewRoom;
