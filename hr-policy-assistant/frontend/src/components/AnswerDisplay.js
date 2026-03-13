import React from 'react';

function AnswerDisplay({ answer }) {
    if (!answer) return null;

    return (
        <div className="card">
            <div className="answer-container">
                <div className={`cache-badge ${answer.cached ? 'cached' : 'fresh'}`}>
                    {answer.cached 
                        ? `✅ Cached (used ${answer.hit_count || 1} times)`
                        : '🆕 Fresh answer'
                    }
                </div>
                
                <div className="answer-content">
                    <h3>📝 Answer:</h3>
                    <div className="answer-text">{answer.answer}</div>
                </div>
                
                {answer.agent_trace && answer.agent_trace.length > 0 && (
                    <div className="trace-section">
                        <h4>🔍 Reasoning Trace:</h4>
                        <ul className="trace-steps">
                            {answer.agent_trace.map((step, index) => (
                                <li key={index} className="trace-step">
                                    <span className="trace-agent">{step.agent}:</span>
                                    <span className="trace-output"> {step.output}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}

export default AnswerDisplay;