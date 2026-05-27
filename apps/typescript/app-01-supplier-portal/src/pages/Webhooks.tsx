import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useWebhooks } from '../hooks/useWebhooks';
import { useTranslation } from '../i18n/I18nContext';

// DECOY: Client-side URL validation — looks like the only safeguard
// but server-side validation should also exist
function validateUrlInput(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

export function WebhooksPage() {
  const { user } = useAuth();
  const { t } = useTranslation();
  const { subscriptions, loading, error, registerWebhook, deleteWebhook } = useWebhooks(user?.supplier_id || '');
  const [callbackUrl, setCallbackUrl] = useState('');
  const [regError, setRegError] = useState('');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegError('');

    // DECOY: Client-side URL validation — defense in depth
    if (!validateUrlInput(callbackUrl)) {
      setRegError('Invalid URL. Must start with http:// or https://');
      return;
    }

    try {
      await registerWebhook(callbackUrl);
      setCallbackUrl('');
    } catch (err: any) {
      setRegError(err.response?.data?.error || err.message || 'Registration failed');
    }
  };

  if (loading) return <div className="page-loading">{t('loading')}</div>;
  if (error) return <div className="page-error">{error}</div>;

  return (
    <div className="page webhooks-page">
      <h2>Webhooks</h2>

      <form className="webhook-form" onSubmit={handleRegister}>
        <h3>Register Webhook</h3>
        <div className="webhook-field">
          <label>Callback URL</label>
          <input
            type="text"
            value={callbackUrl}
            onChange={(e) => setCallbackUrl(e.target.value)}
            placeholder="https://example.com/webhook"
            required
          />
        </div>
        {regError && <p className="webhook-error">{regError}</p>}
        <button type="submit" className="btn-generate">Register</button>
      </form>

      <h3>Registered Webhooks</h3>
      {subscriptions.length === 0 ? (
        <p className="empty-state">No webhooks registered.</p>
      ) : (
        <table className="reports-table">
          <thead>
            <tr>
              <th>URL</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {subscriptions.map((sub) => (
              <tr key={sub.subscription_id}>
                <td>{sub.callback_url}</td>
                <td>{sub.is_active ? 'Active' : 'Inactive'}</td>
                <td>
                  <button
                    className="btn-delete"
                    onClick={() => deleteWebhook(sub.subscription_id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
