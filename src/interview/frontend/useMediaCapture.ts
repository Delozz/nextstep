/**
 * Custom React hook for media capture with Voice Activity Detection.
 * Captures camera (1 FPS) and microphone (16kHz PCM) for interview.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import type { MediaCaptureState } from './types';

interface UseMediaCaptureOptions {
    videoFps?: number;
    audioSampleRate?: number;
    vadThreshold?: number;
    silenceTimeout?: number;
}

interface UseMediaCaptureReturn {
    state: MediaCaptureState;
    videoRef: React.RefObject<HTMLVideoElement>;
    startCapture: () => Promise<void>;
    stopCapture: () => void;
    getVideoFrame: () => string | null;
    getAudioBuffer: () => Float32Array | null;
    clearAudioBuffer: () => void;
    isSpeaking: boolean;
}

export function useMediaCapture(options: UseMediaCaptureOptions = {}): UseMediaCaptureReturn {
    const {
        videoFps = 1,
        audioSampleRate = 16000,
        vadThreshold = 0.01,
        silenceTimeout = 1500, // ms of silence to detect end of speech
    } = options;

    const [state, setState] = useState<MediaCaptureState>({
        isCapturing: false,
        hasPermission: false,
        audioLevel: 0,
        isSpeaking: false,
        error: null,
    });

    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const audioBufferRef = useRef<Float32Array[]>([]);
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const frameIntervalRef = useRef<number | null>(null);
    const silenceTimerRef = useRef<number | null>(null);
    const wasSpeakingRef = useRef(false);

    // Start capturing
    const startCapture = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: 'user' },
                audio: { sampleRate: audioSampleRate, channelCount: 1 },
            });

            streamRef.current = stream;

            // Set up video
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                await videoRef.current.play();
            }

            // Set up audio analysis
            audioContextRef.current = new AudioContext({ sampleRate: audioSampleRate });
            const source = audioContextRef.current.createMediaStreamSource(stream);

            analyserRef.current = audioContextRef.current.createAnalyser();
            analyserRef.current.fftSize = 2048;
            source.connect(analyserRef.current);

            // Create hidden canvas for frame capture
            canvasRef.current = document.createElement('canvas');
            canvasRef.current.width = 640;
            canvasRef.current.height = 480;

            // Start audio level monitoring
            const checkAudioLevel = () => {
                if (!analyserRef.current) return;

                const dataArray = new Float32Array(analyserRef.current.fftSize);
                analyserRef.current.getFloatTimeDomainData(dataArray);

                // Calculate RMS
                let sum = 0;
                for (let i = 0; i < dataArray.length; i++) {
                    sum += dataArray[i] * dataArray[i];
                }
                const rms = Math.sqrt(sum / dataArray.length);

                const isSpeaking = rms > vadThreshold;

                // Track audio for buffer
                if (isSpeaking) {
                    audioBufferRef.current.push(new Float32Array(dataArray));
                }

                // Detect end of speech (silence after speaking)
                if (wasSpeakingRef.current && !isSpeaking) {
                    if (!silenceTimerRef.current) {
                        silenceTimerRef.current = window.setTimeout(() => {
                            setState(prev => ({ ...prev, isSpeaking: false }));
                            silenceTimerRef.current = null;
                        }, silenceTimeout);
                    }
                } else if (isSpeaking) {
                    if (silenceTimerRef.current) {
                        clearTimeout(silenceTimerRef.current);
                        silenceTimerRef.current = null;
                    }
                    setState(prev => ({ ...prev, isSpeaking: true }));
                }

                wasSpeakingRef.current = isSpeaking;
                setState(prev => ({ ...prev, audioLevel: rms }));

                if (state.isCapturing) {
                    requestAnimationFrame(checkAudioLevel);
                }
            };

            requestAnimationFrame(checkAudioLevel);

            setState({
                isCapturing: true,
                hasPermission: true,
                audioLevel: 0,
                isSpeaking: false,
                error: null,
            });

        } catch (error) {
            setState(prev => ({
                ...prev,
                error: error instanceof Error ? error.message : 'Failed to access media devices',
                hasPermission: false,
            }));
        }
    }, [audioSampleRate, vadThreshold, silenceTimeout, state.isCapturing]);

    // Stop capturing
    const stopCapture = useCallback(() => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }

        if (audioContextRef.current) {
            audioContextRef.current.close();
            audioContextRef.current = null;
        }

        if (frameIntervalRef.current) {
            clearInterval(frameIntervalRef.current);
            frameIntervalRef.current = null;
        }

        if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
        }

        setState(prev => ({
            ...prev,
            isCapturing: false,
            isSpeaking: false,
            audioLevel: 0,
        }));
    }, []);

    // Get current video frame as base64
    const getVideoFrame = useCallback((): string | null => {
        if (!videoRef.current || !canvasRef.current) return null;

        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return null;

        ctx.drawImage(videoRef.current, 0, 0, 640, 480);
        const dataUrl = canvasRef.current.toDataURL('image/jpeg', 0.7);

        // Return just the base64 part, not the data URL prefix
        return dataUrl.split(',')[1];
    }, []);

    // Get accumulated audio buffer
    const getAudioBuffer = useCallback((): Float32Array | null => {
        if (audioBufferRef.current.length === 0) return null;

        const totalLength = audioBufferRef.current.reduce((sum, arr) => sum + arr.length, 0);
        const combined = new Float32Array(totalLength);

        let offset = 0;
        for (const arr of audioBufferRef.current) {
            combined.set(arr, offset);
            offset += arr.length;
        }

        return combined;
    }, []);

    // Clear audio buffer
    const clearAudioBuffer = useCallback(() => {
        audioBufferRef.current = [];
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopCapture();
        };
    }, [stopCapture]);

    return {
        state,
        videoRef,
        startCapture,
        stopCapture,
        getVideoFrame,
        getAudioBuffer,
        clearAudioBuffer,
        isSpeaking: state.isSpeaking,
    };
}

export default useMediaCapture;
