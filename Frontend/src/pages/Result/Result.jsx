import React, { useEffect, useState } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import { ArrowLeft, AlertCircle, Sparkles } from 'lucide-react';
import ResultCard from '../../components/ResultCard/ResultCard';
import Skeleton from '../../components/Skeleton/Skeleton';
import { api } from '../../services/api';
import './Result.css';

export function Result() {
  const { id } = useParams();
  const location = useLocation();
  const [result, setResult] = useState(location.state?.result || null);
  const [loading, setLoading] = useState(!location.state?.result);
  const [error, setError] = useState(null);

  useEffect(() => {
    // If not passed through route state, fetch from API
    if (!result && id) {
      let isMounted = true;
      api.getHistoryItem(id)
        .then(async (data) => {
          if (!data.guidance && data.predicted_category?.slug) {
            try {
              data.guidance = await api.getCategoryGuidance(data.predicted_category.slug);
            } catch (gErr) {
              console.error('Failed to load guidance:', gErr);
            }
          }
          if (isMounted) setResult(data);
        })
        .catch((err) => {
          if (isMounted) setError(err.message || 'Could not load classification record');
        })
        .finally(() => {
          if (isMounted) setLoading(false);
        });

      return () => {
        isMounted = false;
      };
    }
  }, [id, result]);

  return (
    <div className="result-page container">
      {/* Top navigation row */}
      <div className="result-nav-row">
        <Link to="/classify" className="btn btn-secondary back-btn">
          <ArrowLeft size={16} />
          <span>Scan Another Item</span>
        </Link>
        <Link to="/history" className="btn btn-ghost">
          <span>View Scan History</span>
        </Link>
      </div>

      {loading && (
        <div className="result-loading-state glass-panel">
          <Skeleton height="240px" borderRadius="var(--radius-md)" />
          <Skeleton height="40px" width="60%" />
          <Skeleton height="100px" />
          <Skeleton height="150px" />
        </div>
      )}

      {error && !loading && (
        <div className="result-error-state glass-panel">
          <AlertCircle size={40} className="error-icon" />
          <h3>Unable to Load Scan</h3>
          <p>{error}</p>
          <Link to="/classify" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            <Sparkles size={16} />
            <span>Perform New Scan</span>
          </Link>
        </div>
      )}

      {result && !loading && (
        <div className="result-display-wrapper">
          <ResultCard
            result={result}
            imageUrl={result.thumbnail || null}
          />
        </div>
      )}
    </div>
  );
}

export default Result;
