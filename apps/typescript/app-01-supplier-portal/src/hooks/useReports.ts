import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export interface Report {
  id: string;
  type: string;
  period: string;
  generated_at: string;
  status: string;
  notes?: string;
}

export function useReports() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams(window.location.search);
      const supplierId = params.get('supplier_id') || 'supplier-001';
      const response = await api.get(`/portal/reports?supplier_id=${supplierId}`);
      const data = response.data.reports || response.data;
      setReports(Array.isArray(data) ? data : []);
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
      const params = new URLSearchParams(window.location.search);
      const supplierId = params.get('supplier_id') || 'supplier-001';
      const response = await api.post('/portal/reports/request', {
        supplier_id: supplierId,
        report_type: type,
      });
      await fetchReports();
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.message || err.message || 'Failed to generate report');
    }
  }, [fetchReports]);

  return { reports, loading, error, generateReport, refresh: fetchReports };
}
