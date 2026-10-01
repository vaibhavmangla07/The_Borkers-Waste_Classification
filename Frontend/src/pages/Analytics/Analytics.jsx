import React, { useState } from 'react';
import { BarChart3, PieChart, Activity, AlertCircle, Inbox, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import Skeleton from '../../components/Skeleton/Skeleton';
import useAnalytics from '../../hooks/useAnalytics';
import './Analytics.css';

export function Analytics() {
  const [range, setRange] = useState('7d');
  const { categories, activity, loading, error } = useAnalytics(range);

  return (
    <div className="analytics-page container">
      <div className="page-header">
        <div className="badge badge-cyan">
          <BarChart3 size={14} aria-hidden="true" /> Intelligence & Trends
        </div>
        <h1 className="page-title">Waste Analytics & Metrics</h1>
        <p className="page-subtitle">
          Aggregate volume breakdown across material categories, municipal recycling rates, and scan frequencies.
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="analytics-grid">
          <div className="glass-panel analytics-card">
            <Skeleton height="32px" width="50%" />
            <Skeleton height="24px" width="100%" />
            <Skeleton height="24px" width="100%" />
            <Skeleton height="24px" width="100%" />
          </div>
          <div className="glass-panel analytics-card">
            <Skeleton height="32px" width="50%" />
            <Skeleton height="160px" width="100%" />
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="glass-panel analytics-state-box error-box">
          <AlertCircle size={38} className="state-icon error-icon" aria-hidden="true" />
          <h3>Unable to Load Analytics</h3>
          <p>{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && categories.length === 0 && (
        <div className="glass-panel analytics-state-box empty-box">
          <Inbox size={42} className="state-icon empty-icon" aria-hidden="true" />
          <h3>No Analytics Data Available</h3>
          <p>Scans logged through the classification engine will automatically populate volume and activity metrics.</p>
          <Link to="/classify" className="btn btn-primary" style={{ marginTop: '0.75rem' }}>
            <Sparkles size={16} aria-hidden="true" />
            <span>Classify Waste Now</span>
          </Link>
        </div>
      )}

      {/* Analytics Content */}
      {!loading && !error && categories.length > 0 && (
        <div className="analytics-grid">
          {/* Distribution Bars */}
          <div className="glass-panel analytics-card">
            <div className="card-header-row">
              <div className="header-title-wrap">
                <PieChart size={20} className="header-icon" aria-hidden="true" />
                <h3>Category Distribution</h3>
              </div>
              <span className="badge badge-emerald">Model Telemetry</span>
            </div>

            <div className="category-bars-container">
              {categories.map((cat) => (
                <div key={cat.category} className="cat-bar-item">
                  <div className="cat-bar-header">
                    <span className="cat-name">{cat.category}</span>
                    <span className="cat-stats">
                      <strong>{cat.percentage}%</strong> ({cat.count.toLocaleString()} scans)
                    </span>
                  </div>
                  <div className="cat-track">
                    <div
                      className="cat-fill"
                      style={{ width: `${cat.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Temporal Activity Card */}
          <div className="glass-panel analytics-card">
            <div className="card-header-row">
              <div className="header-title-wrap">
                <Activity size={20} className="header-icon" aria-hidden="true" />
                <h3>Activity Trends</h3>
              </div>
              <div className="time-range-toggle" role="group" aria-label="Select time range">
                <button
                  type="button"
                  className={`toggle-btn ${range === '7d' ? 'active' : ''}`}
                  onClick={() => setRange('7d')}
                >
                  7D
                </button>
                <button
                  type="button"
                  className={`toggle-btn ${range === '30d' ? 'active' : ''}`}
                  onClick={() => setRange('30d')}
                >
                  30D
                </button>
              </div>
            </div>

            <div className="chart-placeholder-box">
              <div className="chart-preview-bars">
                {activity.map((item, idx) => {
                  const maxScans = Math.max(...activity.map(a => a.scans || 1));
                  const heightPercent = Math.min(100, Math.max(15, Math.round((item.scans / maxScans) * 100)));
                  const isLast = idx === activity.length - 1;
                  const dayName = new Date(item.date).toLocaleDateString([], { weekday: 'short' });

                  return (
                    <div
                      key={item.date || idx}
                      className={`mock-bar ${isLast ? 'active-bar' : ''}`}
                      style={{ height: `${heightPercent}%` }}
                      title={`${item.date}: ${item.scans} scans`}
                    >
                      <span className="bar-label">{dayName}</span>
                    </div>
                  );
                })}
              </div>
              <p className="chart-caption">
                Daily scan frequency consuming <code>GET /api/analytics/activity</code>.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Analytics;
