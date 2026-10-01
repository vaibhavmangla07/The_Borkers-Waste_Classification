import React from 'react';
import { LayoutDashboard, Scan, TrendingUp, Layers, ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import StatCard from '../../components/StatCard/StatCard';
import './Dashboard.css';

export function Dashboard() {
  return (
    <div className="dashboard-page container">
      <div className="page-header">
        <div className="badge badge-emerald">
          <LayoutDashboard size={14} /> System Overview
        </div>
        <h1 className="page-title">Operations Dashboard</h1>
        <p className="page-subtitle">
          Real-time waste classification throughput, category distribution, and sorting efficiency metrics.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid-auto-fit">
        <StatCard
          label="Total Scans Logged"
          value="14,820"
          subtext="+12% from last week"
          icon={Scan}
          change="+12.4%"
          trend="up"
        />
        <StatCard
          label="Primary Category"
          value="Plastic"
          subtext="35.3% of total sorted streams"
          icon={Layers}
          change="35.3%"
          trend="neutral"
        />
        <StatCard
          label="Model Confidence Avg"
          value="94.6%"
          subtext="High reliability threshold (>0.80)"
          icon={TrendingUp}
          change="+1.2%"
          trend="up"
        />
      </div>

      {/* Placeholder Grid */}
      <div className="dashboard-preview-grid">
        <div className="glass-panel preview-card">
          <div className="preview-card-header">
            <h3>Recent Classifications Stream</h3>
            <Link to="/history" className="view-all-link">
              <span>View History</span>
              <ArrowUpRight size={16} />
            </Link>
          </div>
          <div className="placeholder-content">
            <div className="placeholder-badge">Live API Feed Placeholder</div>
            <p>Will stream classifications from <code>GET /api/history</code> upon backend phase activation.</p>
          </div>
        </div>

        <div className="glass-panel preview-card">
          <div className="preview-card-header">
            <h3>Waste Group Distribution</h3>
            <Link to="/analytics" className="view-all-link">
              <span>Detailed Analytics</span>
              <ArrowUpRight size={16} />
            </Link>
          </div>
          <div className="placeholder-content">
            <div className="placeholder-badge">Chart Placeholder</div>
            <p>Interactive group breakdowns consuming <code>GET /api/analytics/categories</code>.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
