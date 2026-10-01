import React from 'react';
import { CheckCircle, AlertTriangle, Clock, Zap } from 'lucide-react';
import PredictionBars from '../PredictionBars/PredictionBars';
import GuidanceCard from '../GuidanceCard/GuidanceCard';
import './ResultCard.css';

export function ResultCard({ result, imageUrl }) {
  if (!result) return null;

  const {
    id,
    predicted_category,
    confidence,
    confidence_level,
    predictions,
    guidance,
    model_name,
    model_version,
    created_at
  } = result;

  const percentage = Math.round(confidence * 1000) / 10;
  const level = confidence_level || (confidence >= 0.8 ? 'high' : confidence >= 0.6 ? 'medium' : 'low');

  const formattedTime = created_at
    ? new Date(created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : 'Just now';

  return (
    <div className={`result-card glass-panel level-${level}`}>
      <div className="result-card-top">
        {imageUrl && (
          <div className="result-thumbnail-container">
            <img src={imageUrl} alt={`Classified as ${predicted_category?.name}`} className="result-thumbnail" />
            <div className={`confidence-tag-overlay tag-${level}`}>
              {level.toUpperCase()} CONFIDENCE
            </div>
          </div>
        )}

        <div className="result-primary-info">
          <div className="result-meta-row">
            <span className="result-id">Scan #{id || 'ID'}</span>
            <div className="result-stats-pills">
              {model_version && (
                <span className="stat-pill" title="Model Version">
                  <Zap size={13} /> {model_name} v{model_version}
                </span>
              )}
              <span className="stat-pill">
                <Clock size={13} /> {formattedTime}
              </span>
            </div>
          </div>

          <h2 className="result-category-title">{predicted_category?.name}</h2>

          <div className="result-confidence-highlight">
            <div className="confidence-numeric-box">
              <span className="confidence-number">{percentage}%</span>
              <span className="confidence-label">Confidence Score</span>
            </div>
            <div className="confidence-status-desc">
              {level === 'high' && (
                <p className="status-text text-high">
                  <CheckCircle size={16} /> Verified high-confidence AI prediction. Safe to follow disposal protocols.
                </p>
              )}
              {level === 'medium' && (
                <p className="status-text text-medium">
                  <AlertTriangle size={16} /> Medium confidence. Double check item materials if unsure.
                </p>
              )}
              {level === 'low' && (
                <p className="status-text text-low">
                  <AlertTriangle size={16} /> Low confidence detection. Please verify manually or rescan with better lighting.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {predictions && predictions.length > 0 && (
        <div className="result-section-divider">
          <PredictionBars predictions={predictions} />
        </div>
      )}

      {guidance && guidance.length > 0 && (
        <div className="result-section-divider">
          <GuidanceCard disposal={guidance[0]} confidenceLevel={level} />
        </div>
      )}
    </div>
  );
}

export default ResultCard;
