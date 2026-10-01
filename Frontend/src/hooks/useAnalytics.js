import { useState, useEffect } from 'react';
import { api } from '../services/api';

/**
 * Custom hook to fetch analytics metrics, distributions, and activity trends
 */
export function useAnalytics(range = '7d') {
  const [summary, setSummary] = useState(null);
  const [categories, setCategories] = useState([]);
  const [activity, setActivity] = useState([]);
  const [recentItems, setRecentItems] = useState([]);
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
          api.getAnalyticsActivity(30)
        ]);
        if (isMounted) {
          setSummary(sumData);
          setCategories(catData?.items || []);
          setRecentItems(actData || []);
          
          const days = range === '30d' ? 30 : 7;
          const grouped = {};
          
          // Seed the last N days with 0 so chart always renders complete dates
          for (let i = days - 1; i >= 0; i--) {
            const d = new Date();
            d.setDate(d.getDate() - i);
            const key = d.toISOString().split('T')[0];
            grouped[key] = 0;
          }

          (actData || []).forEach((curr) => {
            if (curr.created_at) {
              const dateStr = new Date(curr.created_at).toISOString().split('T')[0];
              if (grouped[dateStr] !== undefined) {
                grouped[dateStr]++;
              }
            }
          });
          
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
    recentItems,
    loading,
    error
  };
}

export default useAnalytics;
