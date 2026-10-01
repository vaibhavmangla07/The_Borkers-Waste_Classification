import React from 'react';
import { CheckCircle2, AlertTriangle, Trash2, Info } from 'lucide-react';
import './GuidanceCard.css';

export function GuidanceCard({ disposal, confidenceLevel = 'high' }) {
  if (!disposal) return null;

  const isLowConfidence = confidenceLevel === 'low';

  return (
    <div className={`glass-panel guidance-card ${isLowConfidence ? 'guidance-low-confidence' : ''}`}>
      <div className="guidance-header">
        <div className="bin-icon-wrapper">
          <Trash2 size={24} />
        </div>
        <div>
          <span className="guidance-bin-type">Recommended Bin: {disposal.bin_type}</span>
          <h3 className="guidance-title">{disposal.title}</h3>
        </div>
      </div>

      {isLowConfidence && (
        <div className="guidance-warning-box">
          <AlertTriangle size={18} className="warning-icon" />
          <p>
            <strong>Low Confidence Detection:</strong> The AI model is uncertain about this item. 
            Disposal guidance below is tentative. Please visually verify or upload a clearer, well-lit photo before disposing.
          </p>
        </div>
      )}

      <div className="guidance-sections">
        {disposal.instructions && disposal.instructions.length > 0 && (
          <div className="guidance-section do-section">
            <h4 className="section-label do-label">
              <CheckCircle2 size={16} /> What to Do
            </h4>
            <ul className="guidance-list">
              {disposal.instructions.map((item, idx) => (
                <li key={idx} className="guidance-list-item">
                  <span className="bullet-do">✓</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {disposal.avoid && disposal.avoid.length > 0 && (
          <div className="guidance-section avoid-section">
            <h4 className="section-label avoid-label">
              <Info size={16} /> Things to Avoid
            </h4>
            <ul className="guidance-list">
              {disposal.avoid.map((item, idx) => (
                <li key={idx} className="guidance-list-item">
                  <span className="bullet-avoid">✕</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default GuidanceCard;
