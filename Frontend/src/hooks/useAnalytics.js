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
          setCategories(catData?.items || []);
          
          // Group recent classifications by date for the activity chart
          const grouped = (actData || []).reduce((acc, curr) => {
            const dateStr = new Date(curr.created_at).toISOString().split('T')[0];
            if (!acc[dateStr]) acc[dateStr] = 0;
            acc[dateStr]++;
            return acc;
          }, {});
          
          const chartData = Object.entries(grouped)
            .sort((a, b) => a[0].localeCompare(b[0]))
            .map(([date, scans]) => ({ date, scans }));
            
          setActivity(chartData);
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
