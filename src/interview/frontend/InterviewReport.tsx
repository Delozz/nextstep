/**
 * InterviewReport Component
 * Displays the final 70/30 score breakdown and feedback after interview.
 */

import React from 'react';
import type { InterviewReport as ReportData } from './types';

interface InterviewReportProps {
    report: ReportData;
    onRetry?: () => void;
    onClose?: () => void;
}

export const InterviewReport: React.FC<InterviewReportProps> = ({
    report,
    onRetry,
    onClose
}) => {
    if (report.error) {
        return (
            <div className="interview-report error">
                <h2>⚠️ Report Generation Failed</h2>
                <p>{report.error}</p>
                {onRetry && <button onClick={onRetry}>Try Again</button>}
            </div>
        );
    }

    const getScoreColor = (score: number): string => {
        if (score >= 80) return '#00FF94';
        if (score >= 60) return '#FFD700';
        if (score >= 40) return '#FFA500';
        return '#FF4B4B';
    };

    const getScoreLabel = (score: number): string => {
        if (score >= 90) return 'Exceptional';
        if (score >= 80) return 'Excellent';
        if (score >= 70) return 'Very Good';
        if (score >= 60) return 'Good';
        if (score >= 50) return 'Fair';
        return 'Needs Work';
    };

    return (
        <div className="interview-report">
            <style>{`
        .interview-report {
          background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
          border-radius: 16px;
          padding: 32px;
          color: white;
          font-family: 'Inter', -apple-system, sans-serif;
          max-width: 800px;
          margin: 0 auto;
        }

        .interview-report.error {
          border: 2px solid #FF4B4B;
        }

        .report-header {
          text-align: center;
          margin-bottom: 32px;
        }

        .final-score {
          font-size: 72px;
          font-weight: 800;
          margin: 16px 0;
        }

        .score-label {
          font-size: 24px;
          opacity: 0.9;
        }

        .score-breakdown {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 24px;
          margin: 32px 0;
        }

        .score-card {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          padding: 20px;
          text-align: center;
        }

        .score-card h3 {
          margin: 0 0 8px 0;
          font-size: 14px;
          text-transform: uppercase;
          opacity: 0.7;
        }

        .score-card .value {
          font-size: 36px;
          font-weight: 700;
        }

        .score-card .weight {
          font-size: 12px;
          opacity: 0.5;
        }

        .section {
          margin: 24px 0;
        }

        .section h3 {
          color: #00FF94;
          margin-bottom: 12px;
          font-size: 18px;
        }

        .section ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .section li {
          padding: 8px 0;
          border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .section li:last-child {
          border-bottom: none;
        }

        .strengths li::before {
          content: '✅ ';
        }

        .improvements li::before {
          content: '📈 ';
        }

        .next-steps li::before {
          content: '➡️ ';
        }

        .impression {
          background: rgba(0, 255, 148, 0.1);
          border-left: 4px solid #00FF94;
          padding: 16px;
          border-radius: 0 8px 8px 0;
          font-style: italic;
        }

        .question-feedback {
          margin-top: 24px;
        }

        .question-item {
          background: rgba(255,255,255,0.03);
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 12px;
        }

        .question-item .q-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .question-item .q-score {
          font-weight: 700;
          padding: 4px 12px;
          border-radius: 16px;
          font-size: 14px;
        }

        .actions {
          display: flex;
          gap: 16px;
          justify-content: center;
          margin-top: 32px;
        }

        .actions button {
          padding: 12px 32px;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #00FF94;
          color: #0a0e27;
          border: none;
        }

        .btn-primary:hover {
          background: #00cc77;
        }

        .btn-secondary {
          background: transparent;
          color: white;
          border: 2px solid rgba(255,255,255,0.3);
        }

        .btn-secondary:hover {
          border-color: white;
        }
      `}</style>

            <div className="report-header">
                <h1>🎯 Interview Complete</h1>
                <div
                    className="final-score"
                    style={{ color: getScoreColor(report.finalScore) }}
                >
                    {Math.round(report.finalScore)}
                </div>
                <div className="score-label">{getScoreLabel(report.finalScore)}</div>
            </div>

            <div className="score-breakdown">
                <div className="score-card">
                    <h3>Content Quality</h3>
                    <div className="value" style={{ color: getScoreColor(report.contentScore) }}>
                        {report.contentScore}
                    </div>
                    <div className="weight">{report.weightBreakdown?.content.weight} weight</div>
                </div>
                <div className="score-card">
                    <h3>Behavioral Delivery</h3>
                    <div className="value" style={{ color: getScoreColor(report.behavioralScore) }}>
                        {report.behavioralScore}
                    </div>
                    <div className="weight">{report.weightBreakdown?.behavioral.weight} weight</div>
                </div>
            </div>

            <div className="impression">
                {report.overallImpression}
            </div>

            <div className="section">
                <h3>💪 Strengths</h3>
                <ul className="strengths">
                    {report.strengths.map((s, i) => (
                        <li key={i}>{s}</li>
                    ))}
                </ul>
            </div>

            <div className="section">
                <h3>📈 Areas for Improvement</h3>
                <ul className="improvements">
                    {report.areasForImprovement.map((a, i) => (
                        <li key={i}>{a}</li>
                    ))}
                </ul>
            </div>

            {report.questionFeedback && report.questionFeedback.length > 0 && (
                <div className="section question-feedback">
                    <h3>📝 Question-by-Question Feedback</h3>
                    {report.questionFeedback.map((qf, i) => (
                        <div className="question-item" key={i}>
                            <div className="q-header">
                                <span>Q{i + 1}: {qf.question.substring(0, 50)}...</span>
                                <span
                                    className="q-score"
                                    style={{
                                        background: getScoreColor(qf.score),
                                        color: '#0a0e27'
                                    }}
                                >
                                    {qf.score}/100
                                </span>
                            </div>
                            <p style={{ opacity: 0.8, margin: 0 }}>{qf.feedback}</p>
                        </div>
                    ))}
                </div>
            )}

            <div className="section">
                <h3>🚀 Recommended Next Steps</h3>
                <ul className="next-steps">
                    {report.recommendedNextSteps.map((step, i) => (
                        <li key={i}>{step}</li>
                    ))}
                </ul>
            </div>

            <div className="actions">
                {onRetry && (
                    <button className="btn-primary" onClick={onRetry}>
                        Practice Again
                    </button>
                )}
                {onClose && (
                    <button className="btn-secondary" onClick={onClose}>
                        Back to Dashboard
                    </button>
                )}
            </div>
        </div>
    );
};

export default InterviewReport;
