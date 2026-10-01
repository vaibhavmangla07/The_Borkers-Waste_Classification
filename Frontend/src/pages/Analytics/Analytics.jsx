import React, { useState } from 'react';
import { BarChart3, PieChart, Activity, AlertCircle, Inbox, Sparkles, TrendingUp, Layers, Scan, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import Skeleton from '../../components/Skeleton/Skeleton';
import StatCard from '../../components/StatCard/StatCard';
import useAnalytics from '../../hooks/useAnalytics';
import './Analytics.css';

export function Analytics() {
  const [range, setRange] = useState('7d');
  const { summary, categories, activity, loading, error } = useAnalytics(range);

  const totalScans = summary?.total_classifications ?? 0;
  const topCategoryName = summary?.most_classified_category?.name || 'N/A';
  const topCategoryCount = summary?.most_classified_category?.count || 0;
  const topCategoryPct = totalScans > 0 ? ((topCategoryCount / totalScans) * 100).toFixed(1) : '0.0';
  const avgConfidence = summary?.average_confidence ? (summary.average_confidence * 100).toFixed(1) : '0.0';
  const highConfCount = summary?.high_confidence_count ?? 0;

  return (
    <div className="analytics-page container">
      <div className="page-header">
        <div className="header-left">
          <div className="badge badge-cyan">
            <BarChart3 size={14} aria-hidden="true" /> Intelligence & Trends
          </div>
          <h1 className="page-title">Waste Analytics & Metrics</h1>
          <p className="page-subtitle">
            Aggregate volume breakdown across material categories, model telemetry, and scan activity.
          </p>
        </div>
        <div className="header-actions">
          <Link to="/classify" className="btn btn-primary cta-scan-btn">
            <Sparkles size={16} aria-hidden="true" />
            <span>Classify Waste</span>
          </Link>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="analytics-content-stack">
          <div className="grid-auto-fit">
            <div className="glass-panel stat-card-skeleton"><Skeleton height="80px" width="100%" /></div>
            <div className="glass-panel stat-card-skeleton"><Skeleton height="80px" width="100%" /></div>
            <div className="glass-panel stat-card-skeleton"><Skeleton height="80px" width="100%" /></div>
            <div className="glass-panel stat-card-skeleton"><Skeleton height="80px" width="100%" /></div>
          </div>
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
      {!loading && !error && categories.length === 0 && totalScans === 0 && (
        <div className="glass-panel analytics-state-box empty-box">
          <Inbox size={42} className="state-icon empty-icon" aria-hidden="true" />
          <h3>No Analytics Data Available Yet</h3>
          <p>Scans logged through the classification engine will automatically populate volume, breakdown, and activity metrics.</p>
          <Link to="/classify" className="btn btn-primary" style={{ marginTop: '0.75rem' }}>
            <Sparkles size={16} aria-hidden="true" />
            <span>Classify Waste Now</span>
          </Link>
        </div>
      )}

      {/* Analytics Content */}
      {!loading && !error && (categories.length > 0 || totalScans > 0) && (
        <div className="analytics-content-stack">
          {/* Overview Stat Cards */}
          <div className="grid-auto-fit">
            <StatCard
              label="Total Volume Sorted"
              value={totalScans.toLocaleString()}
              subtext="Scans logged to database"
              icon={Scan}
              change={totalScans > 0 ? `${totalScans} items` : 'Live'}
              trend="up"
            />
            <StatCard
              label="Dominant Waste Stream"
              value={topCategoryName}
              subtext={`${topCategoryPct}% of all classified items`}
              icon={Layers}
              change={totalScans > 0 ? `${topCategoryPct}%` : '0%'}
              trend="neutral"
            />
            <StatCard
              label="Average Model Confidence"
              value={`${avgConfidence}%`}
              subtext="Softmax confidence score"
              icon={TrendingUp}
              change="Optimal"
              trend="up"
            />
            <StatCard
              label="High Confidence Scans"
              value={highConfCount.toLocaleString()}
              subtext="Confidence ≥ 80%"
              icon={ShieldCheck}
              change={`${highConfCount} verified`}
              trend="up"
            />
          </div>

          <div className="analytics-grid">
            {/* Distribution Bars */}
            <div className="glass-panel analytics-card">
              <div className="card-header-row">
                <div className="header-title-wrap">
                  <PieChart size={20} className="header-icon" aria-hidden="true" />
                  <h3>Material Category Distribution</h3>
                </div>
                <span className="badge badge-emerald">Model Telemetry</span>
              </div>

              <div className="category-bars-container">
                {categories.map((cat) => (
                  <div key={cat.category_slug} className="cat-bar-item">
                    <div className="cat-bar-header">
                      <span className="cat-name">{cat.category_name}</span>
                      <span className="cat-stats">
                        <strong>{cat.percentage.toFixed(1)}%</strong> ({cat.classification_count.toLocaleString()} scans)
                      </span>
                    </div>
                    <div className="cat-track">
                      <div
                        className="cat-fill"
                        style={{ width: `${Math.max(4, cat.percentage)}%` }}
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
                  <Activity size={20} className="header-icon icon-cyan" aria-hidden="true" />
                  <h3>Scan Activity Trends</h3>
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
                    const maxScans = Math.max(1, ...activity.map(a => a.scans || 0));
                    const heightPercent = item.scans > 0 ? Math.min(100, Math.max(20, Math.round((item.scans / maxScans) * 100))) : 8;
                    const isLast = idx === activity.length - 1;
                    const dayName = new Date(item.date).toLocaleDateString([], { weekday: 'short' });

                    return (
                      <div
                        key={item.date || idx}
                        className={`mock-bar ${isLast ? 'active-bar' : ''} ${item.scans > 0 ? 'has-data' : ''}`}
                        style={{ height: `${heightPercent}%` }}
                        title={`${item.date}: ${item.scans} scans`}
                      >
                        <span className="bar-label">{dayName}</span>
                      </div>
                    );
                  })}
                </div>
                <p className="chart-caption">
                  Daily scan throughput powered by real-time classification telemetry.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Analytics;
