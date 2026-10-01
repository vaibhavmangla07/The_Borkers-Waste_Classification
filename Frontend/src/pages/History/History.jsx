import React, { useState, useMemo } from 'react';
import { History as HistoryIcon, Search, Calendar, ChevronRight, AlertCircle, Sparkles, Inbox, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import Skeleton from '../../components/Skeleton/Skeleton';
import useHistory from '../../hooks/useHistory';
import './History.css';

export function History() {
  const { items, loading, error, refetch } = useHistory();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const matchesSearch = 
        item.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        String(item.id).includes(searchTerm);
      const matchesCat = selectedCategory === 'ALL' || item.category.toUpperCase() === selectedCategory;
      return matchesSearch && matchesCat;
    });
  }, [items, searchTerm, selectedCategory]);

  const categories = ['ALL', 'PLASTIC', 'ORGANIC', 'GLASS', 'METAL', 'PAPER'];

  return (
    <div className="history-page container">
      <div className="page-header">
        <div className="badge badge-emerald">
          <HistoryIcon size={14} aria-hidden="true" /> Scan Audit Trail
        </div>
        <h1 className="page-title">Classification History</h1>
        <p className="page-subtitle">
          Browse historical image scans, predicted categories, confidence distributions, and timestamps.
        </p>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="history-toolbar glass-panel">
        <div className="search-box">
          <Search size={16} className="search-icon" aria-hidden="true" />
          <input
            type="text"
            placeholder="Search scans by category or ID..."
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            aria-label="Filter scans by category or ID"
          />
        </div>

        <div className="category-filter-chips" role="radiogroup" aria-label="Filter by waste category">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              className={`filter-chip ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat === 'ALL' ? 'All Classes' : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="history-loading-list">
          <Skeleton height="72px" borderRadius="var(--radius-md)" />
          <Skeleton height="72px" borderRadius="var(--radius-md)" />
          <Skeleton height="72px" borderRadius="var(--radius-md)" />
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="glass-panel history-state-box error-box">
          <AlertCircle size={36} className="state-icon error-icon" aria-hidden="true" />
          <h3>Unable to Load Scan Records</h3>
          <p>{error}</p>
          <button type="button" className="btn btn-secondary" onClick={refetch}>
            <RefreshCw size={14} aria-hidden="true" /> Retry Fetch
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && filteredItems.length === 0 && (
        <div className="glass-panel history-state-box empty-box">
          <Inbox size={42} className="state-icon empty-icon" aria-hidden="true" />
          <h3>No Classifications Yet</h3>
          <p>
            {searchTerm || selectedCategory !== 'ALL'
              ? 'No historical scans match your current filter criteria.'
              : 'Scan your first waste item to start building your environmental audit trail.'}
          </p>
          <Link to="/classify" className="btn btn-primary">
            <Sparkles size={16} aria-hidden="true" />
            <span>Analyze Waste Item</span>
          </Link>
        </div>
      )}

      {/* Desktop Table View */}
      {!loading && !error && filteredItems.length > 0 && (
        <>
          <div className="history-table-container glass-panel">
            <table className="history-table">
              <thead>
                <tr>
                  <th scope="col">Scan ID</th>
                  <th scope="col">Category</th>
                  <th scope="col">Confidence</th>
                  <th scope="col">Recorded At</th>
                  <th scope="col" className="text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map((item) => {
                  const percentage = Math.round(item.confidence * 1000) / 10;
                  return (
                    <tr key={item.id}>
                      <td className="table-id-cell">#{item.id}</td>
                      <td className="table-cat-cell">
                        <strong>{item.category}</strong>
                      </td>
                      <td>
                        <div className="table-confidence-wrap">
                          <span className={`badge badge-${item.confidence_level === 'high' ? 'emerald' : item.confidence_level === 'moderate' ? 'amber' : 'rose'}`}>
                            {item.confidence_level.toUpperCase()}
                          </span>
                          <span className="confidence-num">{percentage}%</span>
                        </div>
                      </td>
                      <td className="table-date-cell">
                        <Calendar size={13} aria-hidden="true" />
                        <span>{new Date(item.created_at).toLocaleString()}</span>
                      </td>
                      <td className="text-right">
                        <Link to={`/result/${item.id}`} className="table-link">
                          <span>View Protocol</span>
                          <ChevronRight size={15} aria-hidden="true" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Mobile Card List (displayed on screens < 768px) */}
          <div className="history-mobile-cards">
            {filteredItems.map((item) => {
              const percentage = Math.round(item.confidence * 1000) / 10;
              return (
                <Link
                  key={item.id}
                  to={`/result/${item.id}`}
                  className="glass-panel history-mobile-card"
                >
                  <div className="card-top-row">
                    <span className="mobile-item-id">Scan #{item.id}</span>
                    <span className={`badge badge-${item.confidence_level === 'high' ? 'emerald' : item.confidence_level === 'moderate' ? 'amber' : 'rose'}`}>
                      {item.confidence_level.toUpperCase()} ({percentage}%)
                    </span>
                  </div>

                  <h3 className="mobile-item-category">{item.category}</h3>

                  <div className="card-bottom-row">
                    <span className="mobile-item-date">
                      <Calendar size={12} aria-hidden="true" />
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                    <span className="mobile-view-link">
                      View <ChevronRight size={14} aria-hidden="true" />
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>

          <div className="pagination-bar">
            <span className="page-indicator">
              Showing {filteredItems.length} of {items.length} records
            </span>
          </div>
        </>
      )}
    </div>
  );
}

export default History;
