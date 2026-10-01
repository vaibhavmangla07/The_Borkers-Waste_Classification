import React from 'react';
import './PredictionBars.css';

export function PredictionBars({ predictions = [] }) {
  if (!predictions || predictions.length === 0) {
    return null;
  }

  const getConfidenceLevel = (score) => {
    if (score >= 0.8) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
  };

  return (
    <div className="prediction-bars-wrapper">
      <h4 className="prediction-bars-title">Top Model Predictions</h4>
      <div className="prediction-bars-list">
        {predictions.map((item, index) => {
          const percentage = Math.round(item.confidence * 1000) / 10;
          const level = getConfidenceLevel(item.confidence);

          return (
            <div key={item.category || index} className="prediction-item">
              <div className="prediction-item-header">
                <div className="prediction-label-wrap">
                  <span className="prediction-rank">#{index + 1}</span>
                  <span className="prediction-name">{item.category}</span>
                </div>
                <div className="prediction-value-wrap">
                  <span className={`prediction-level-tag tag-${level}`}>
                    {level.toUpperCase()}
                  </span>
                  <span className="prediction-percentage">{percentage}%</span>
                </div>
              </div>

              <div className="bar-track">
                <div
                  className={`bar-fill bar-fill-${level}`}
                  style={{ width: `${Math.min(100, Math.max(2, percentage))}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default PredictionBars;
