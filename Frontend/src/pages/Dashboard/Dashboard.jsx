import React from 'react';
import { LayoutDashboard, Scan, TrendingUp, Layers, ArrowUpRight, Sparkles, CheckCircle2, AlertCircle, Clock, PieChart, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import StatCard from '../../components/StatCard/StatCard';
import Skeleton from '../../components/Skeleton/Skeleton';
import useAnalytics from '../../hooks/useAnalytics';
import { api } from '../../services/api';
import './Dashboard.css';

export function Dashboard() {
  const { summary, categories, recentItems, loading, error } = useAnalytics('7d');

  const totalScans = summary?.total_classifications ?? 0;
  const topCategoryName = summary?.most_classified_category?.name || 'Plastic';
  const topCategoryCount = summary?.most_classified_category?.count || 0;
  const topCategoryPct = totalScans > 0 ? ((topCategoryCount / totalScans) * 100).toFixed(1) : '0.0';
  const avgConfidence = summary?.average_confidence ? (summary.average_confidence * 100).toFixed(1) : '92.5';
  const highConfCount = summary?.high_confidence_count ?? 0;

  return (
    <div className="dashboard-page container">
      <div className="page-header">
        <div className="header-left">
          <div className="badge badge-emerald">
            <LayoutDashboard size={14} aria-hidden="true" /> Operations Overview
          </div>
          <h1 className="page-title">Operations Dashboard</h1>
          <p className="page-subtitle">
            Real-time waste classification throughput, model confidence metrics, and material stream telemetry.
          </p>
        </div>
        <div className="header-actions">
          <Link to="/classify" className="btn btn-primary cta-scan-btn">
            <Sparkles size={16} aria-hidden="true" />
            <span>Classify Waste</span>
          </Link>
        </div>
      </div>

      {/* Loading Skeletons */}
      {loading && (
        <div className="dashboard-content-stack">
          <div className="grid-auto-fit">
            <div className="glass-panel stat-card-skeleton"><Skeleton height="80px" width="100%" /></div>
            <div className="glass-panel stat-card-skeleton"><Skeleton height="80px" width="100%" /></div>
            <div className="glass-panel stat-card-skeleton"><Skeleton height="80px" width="100%" /></div>
            <div className="glass-panel stat-card-skeleton"><Skeleton height="80px" width="100%" /></div>
          </div>
          <div className="dashboard-preview-grid">
            <div className="glass-panel preview-card"><Skeleton height="200px" width="100%" /></div>
            <div className="glass-panel preview-card"><Skeleton height="200px" width="100%" /></div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && !loading && (
        <div className="glass-panel dashboard-error-banner">
          <AlertCircle size={24} className="error-icon" />
          <div>
            <h4>Could not load live analytics</h4>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Live Operational Metrics */}
      {!loading && (
        <div className="dashboard-content-stack">
          {/* Key Metrics Row */}
          <div className="grid-auto-fit">
            <StatCard
              label="Total Scans Logged"
              value={totalScans.toLocaleString()}
              subtext="Scans processed by AI engine"
              icon={Scan}
              change={totalScans > 0 ? `${totalScans} items` : 'Live'}
              trend="up"
            />
            <StatCard
              label="Primary Category"
              value={topCategoryName}
              subtext={`${topCategoryPct}% of all classified items`}
              icon={Layers}
              change={totalScans > 0 ? `${topCategoryPct}%` : '0%'}
              trend="neutral"
            />
            <StatCard
              label="Model Confidence Avg"
              value={`${avgConfidence}%`}
              subtext="High reliability threshold (>0.80)"
              icon={TrendingUp}
              change="Stable"
              trend="up"
            />
            <StatCard
              label="High Confidence Scans"
              value={highConfCount.toLocaleString()}
              subtext={`${totalScans > 0 ? Math.round((highConfCount / totalScans) * 100) : 100}% reliability rate`}
              icon={ShieldCheck}
              change={`${highConfCount} verified`}
              trend="up"
            />
          </div>

          {/* Detailed Dual-Card Grid */}
          <div className="dashboard-preview-grid">
            {/* Live Feed Stream */}
            <div className="glass-panel preview-card">
              <div className="preview-card-header">
                <div className="card-title-group">
                  <Clock size={18} className="icon-emerald" />
                  <h3>Recent Classifications Stream</h3>
                </div>
                <Link to="/history" className="view-all-link">
                  <span>View All History</span>
                  <ArrowUpRight size={16} />
                </Link>
              </div>

              {recentItems.length === 0 ? (
                <div className="empty-feed-box">
                  <Scan size={32} className="empty-icon" />
                  <p>No classifications recorded yet. Run a scan to see live telemetry.</p>
                  <Link to="/classify" className="btn btn-secondary btn-sm">Scan First Item</Link>
                </div>
              ) : (
                <div className="recent-items-list">
                  {recentItems.slice(0, 5).map((item) => {
                    const confPct = Math.round((item.confidence || 0) * 100);
                    const catName = item.category?.name || 'Waste Item';
                    const dateStr = item.created_at ? new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' }) : 'Recent';

                    return (
                      <div key={item.id} className="recent-item-row">
                        <div className="item-thumb-wrapper">
                          <img
                            src={api.getHistoryImageUrl(item.id)}
                            alt={catName}
                            className="item-thumb"
                            onError={(e) => { e.target.style.display = 'none'; }}
                          />
                          <div className="item-thumb-fallback">
                            <Layers size={14} />
                          </div>
                        </div>

                        <div className="item-info">
                          <span className="item-name">{catName}</span>
                          <span className="item-date">{dateStr}</span>
                        </div>

                        <div className="item-badges">
                          <span className={`confidence-pill ${confPct >= 80 ? 'pill-high' : 'pill-mid'}`}>
                            {confPct}% conf
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Waste Stream Distribution Preview */}
            <div className="glass-panel preview-card">
              <div className="preview-card-header">
                <div className="card-title-group">
                  <PieChart size={18} className="icon-cyan" />
                  <h3>Material Stream Breakdown</h3>
                </div>
                <Link to="/analytics" className="view-all-link">
                  <span>Full Analytics</span>
                  <ArrowUpRight size={16} />
                </Link>
              </div>

              {categories.length === 0 ? (
                <div className="empty-feed-box">
                  <Layers size={32} className="empty-icon" />
                  <p>Category distribution will populate automatically as users classify items.</p>
                </div>
              ) : (
                <div className="dashboard-category-bars">
                  {categories.slice(0, 6).map((cat) => (
                    <div key={cat.category_slug} className="dash-cat-item">
                      <div className="dash-cat-label">
                        <span className="dash-cat-name">{cat.category_name}</span>
                        <span className="dash-cat-val"><strong>{cat.percentage.toFixed(1)}%</strong> ({cat.classification_count})</span>
                      </div>
                      <div className="dash-cat-track">
                        <div
                          className="dash-cat-fill"
                          style={{ width: `${Math.max(5, cat.percentage)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
