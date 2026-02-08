/**
 * Type definitions for the interview module.
 */

export interface InterviewConfig {
    targetRole: string;
    userName: string;
}

export interface Turn {
    question: string;
    answer: string;
    turnNumber: number;
    durationSec: number;
}

export interface BehavioralSummary {
    avgEyeContact: number;
    totalObservations: number;
    confidenceIndicators: string[];
    notes: string[];
}

export interface QuestionFeedback {
    question: string;
    score: number;
    feedback: string;
}

export interface WeightBreakdown {
    content: {
        score: number;
        weight: string;
        contribution: number;
    };
    behavioral: {
        score: number;
        weight: string;
        contribution: number;
    };
}

export interface InterviewReport {
    finalScore: number;
    contentScore: number;
    behavioralScore: number;
    overallImpression: string;
    strengths: string[];
    areasForImprovement: string[];
    questionFeedback: QuestionFeedback[];
    recommendedNextSteps: string[];
    weightBreakdown: WeightBreakdown;
    error?: string;
}

export interface WebSocketMessage {
    type: 'start' | 'turn' | 'end' | 'question' | 'report' | 'error';
    text?: string;
    transcript?: string;
    videoFrames?: string[];
    turnNumber?: number;
    isFinal?: boolean;
    data?: InterviewReport;
    message?: string;
}

export type InterviewStatus =
    | 'idle'
    | 'connecting'
    | 'ready'
    | 'listening'
    | 'processing'
    | 'speaking'
    | 'complete'
    | 'error';

export interface MediaCaptureState {
    isCapturing: boolean;
    hasPermission: boolean;
    audioLevel: number;
    isSpeaking: boolean;
    error: string | null;
}
