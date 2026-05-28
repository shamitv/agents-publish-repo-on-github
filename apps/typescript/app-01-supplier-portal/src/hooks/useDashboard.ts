import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export interface DashboardStats {
  total_sales: number;
  total_orders: number;
  low_stock_items: number;
  data_quality_score: number;
}

export function useDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // CHAIN LINK 2 (chain-01): IDOR — fetches stats by supplier_id from URL query
      const params = new URLSearchParams(window.location.search);
      const supplierId = params.get('supplier_id') || 'supplier-001';
      const response = await api.get(`/portal/dashboard?supplier_id=${supplierId}`);
      setStats(response.data.kpi || response.data);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to fetch dashboard');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const refresh = useCallback(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, loading, error, refresh };
}
