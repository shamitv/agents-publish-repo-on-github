import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export interface WebhookSubscription {
  subscription_id: string;
  supplier_id: string;
  callback_url: string;
  is_active: boolean;
}

export function useWebhooks(supplierId: string) {
  const [subscriptions, setSubscriptions] = useState<WebhookSubscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscriptions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/v1/reports/webhooks?supplier_id=${supplierId}`);
      setSubscriptions(response.data.subscriptions || []);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Failed to fetch webhooks');
    } finally {
      setLoading(false);
    }
  }, [supplierId]);

  useEffect(() => {
    if (supplierId) fetchSubscriptions();
  }, [fetchSubscriptions, supplierId]);

  const registerWebhook = useCallback(async (callbackUrl: string) => {
    const response = await api.post('/v1/reports/webhooks', {
      supplier_id: supplierId,
      callback_url: callbackUrl,
    });
    await fetchSubscriptions();
    return response.data;
  }, [supplierId, fetchSubscriptions]);

  const deleteWebhook = useCallback(async (subscriptionId: string) => {
    await api.delete(`/v1/reports/webhooks/${subscriptionId}`);
    await fetchSubscriptions();
  }, [fetchSubscriptions]);

  return { subscriptions, loading, error, registerWebhook, deleteWebhook, refresh: fetchSubscriptions };
}
