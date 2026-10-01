import { useState, useEffect } from 'react';
import { api } from '../services/api';

/**
 * Custom hook to fetch analytics metrics, distributions, and activity trends
 */
export function useAnalytics(range = '7d') {
  const [summary, setSummary] = useState(null);
  const [categories, setCategories] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadAnalytics() {
      setLoading(true);
      setError(null);
      try {
        const [sumData, catData, actData] = await Promise.all([
          api.getAnalyticsSummary(),
          api.getAnalyticsCategories(),
          api.getAnalyticsActivity(range)
        ]);
        if (isMounted) {
          setSummary(sumData);
          setCategories(catData || []);
          setActivity(actData || []);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Failed to load analytics');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadAnalytics();
    return () => {
      isMounted = false;
    };
  }, [range]);

  return {
    summary,
    categories,
    activity,
    loading,
    error
  };
}

export default useAnalytics;
