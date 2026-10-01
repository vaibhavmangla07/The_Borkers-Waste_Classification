import React from 'react';
import './StatCard.css';

export function StatCard({ label, value, subtext, icon: Icon, change, trend = 'neutral', className = '', style = {} }) {
  return (
    <div className={`glass-panel glass-panel-hover stat-card ${className}`} style={style}>
      <div className="stat-card-header">
        <span className="stat-card-label">{label}</span>
        {Icon && (
          <div className="stat-card-icon">
            <Icon size={20} />
          </div>
        )}
      </div>
      <div className="stat-card-value-row">
        <span className="stat-card-value">{value}</span>
        {change && (
          <span className={`stat-trend-badge trend-${trend}`}>
            {change}
          </span>
        )}
      </div>
      {subtext && <div className="stat-card-subtext">{subtext}</div>}
    </div>
  );
}

export default StatCard;
