import { useState, useCallback } from 'react';
import { api } from '../services/api';

/**
 * Custom hook to handle waste image classification lifecycle
 */
export function useClassify() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const classify = useCallback(async (file) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.classifyImage(file);
      setResult(data);
      return data;
    } catch (err) {
      const formattedError = {
        code: err.code || 'UNKNOWN_ERROR',
        message: err.message || 'Classification failed. Please try again.'
      };
      setError(formattedError);
      throw formattedError;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setResult(null);
  }, []);

  return {
    classify,
    reset,
    loading,
    error,
    result
  };
}

export default useClassify;
