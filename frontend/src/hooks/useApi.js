import { useState, useCallback, useRef } from 'react';

/**
 * A standardized hook for API calls with loading, error, and data states.
 * @template T
 * @returns {{ data: T | null, loading: boolean, error: string | null, execute: Function, reset: Function }}
 */
export function useApi() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  const execute = useCallback(async (apiFn, ...args) => {
    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setLoading(true);
    setError(null);

    try {
      const response = await apiFn(...args);
      setData(response.data);
      return { success: true, data: response.data };
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'An unexpected error occurred';
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setData(null);
    setLoading(false);
    setError(null);
  }, []);

  return { data, loading, error, execute, reset };
}

/**
 * A hook for paginated API calls.
 * @template T
 * @returns {{ data: T[], loading: boolean, error: string | null, fetch: Function, page: number, setPage: Function, hasMore: boolean, total: number }}
 */
export function usePaginatedApi() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);

  const fetch = useCallback(async (apiFn, currentPage = 1, append = false) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiFn({ page: currentPage, limit: 20 });
      const items = response.data?.items || response.data || [];
      const totalCount = response.data?.total || items.length;

      setData((prev) => (append ? [...prev, ...items] : items));
      setTotal(totalCount);
      setHasMore(items.length === 20 && (append ? prev.length + items.length : items.length) < totalCount);
      setPage(currentPage);
      return { success: true, data: items };
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Failed to fetch data';
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, fetch, page, setPage, hasMore, total };
}

