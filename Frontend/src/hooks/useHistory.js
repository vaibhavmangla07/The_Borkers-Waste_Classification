import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

/**
 * Custom hook to manage classification history list and filters
 */
export function useHistory(initialParams = {}) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [params, setParams] = useState(initialParams);

  useEffect(() => {
    let isMounted = true;
    api.getHistory(params)
      .then((data) => {
        if (isMounted) {
          setItems(data?.items || []);
          setTotal(data?.total || 0);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to load history');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [params]);

  const updateFilters = (newParams) => {
    setParams((prev) => ({ ...prev, ...newParams }));
  };

  const refetch = useCallback(() => {
    setLoading(true);
    api.getHistory(params)
      .then((data) => {
        setItems(data?.items || []);
        setTotal(data?.total || 0);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load history');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [params]);

  return {
    items,
    total,
    loading,
    error,
    params,
    updateFilters,
    refetch
  };
}

export default useHistory;
