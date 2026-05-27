import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export interface Report {
  id: string;
  type: string;
  period: string;
  generated_at: string;
  status: string;
}

export function useReports() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // CHAIN LINK 1 (chain-01): SSRF injection via reportType parameter
      const response = await api.get('/api/reports');
      setReports(response.data);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to fetch reports');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const generateReport = useCallback(async (type: string) => {
    try {
      const response = await api.post('/api/reports/generate', { type });
      await fetchReports();
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.message || err.message || 'Failed to generate report');
    }
  }, [fetchReports]);

  return { reports, loading, error, generateReport, refresh: fetchReports };
}