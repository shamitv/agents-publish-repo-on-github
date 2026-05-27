import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import { LoadingSpinner } from '../../components/LoadingSpinner';

export function AdminCachePage() {
  const [stats, setStats] = useState<any>(null);
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pattern, setPattern] = useState('');
  const [message, setMessage] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsRes, entriesRes] = await Promise.all([
        api.get('/admin/cache/stats'),
        api.get('/admin/cache/entries'),
      ]);
      setStats(statsRes.data);
      setEntries(Array.isArray(entriesRes.data) ? entriesRes.data : []);
    } catch (err: any) {
      setError(err.message || 'Failed to load cache data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleInvalidate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/admin/cache/invalidate', { pattern });
      setMessage(`Invalidated ${res.data.removed} entries matching "${pattern}"`);
      setPattern('');
      await fetchData();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  };

  if (loading) return <LoadingSpinner text="Loading cache stats..." />;
  if (error) return <div className="page-error">{error}</div>;

  return (
    <div className="page admin-page">
      <h2>Cache Management</h2>
      {message && <p style={{ padding: '0.5rem', background: '#e8f5e9', borderRadius: 4 }}>{message}</p>}

      {stats && (
        <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
          <div className="stat-card">
            <h3>Hit Rate</h3>
            <p className="stat-value">{stats.hit_rate?.toFixed(1) || '0'}%</p>
          </div>
          <div className="stat-card">
            <h3>Entries</h3>
            <p className="stat-value">{stats.size || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Hits</h3>
            <p className="stat-value">{stats.hits || 0}</p>
          </div>
          <div className="stat-card">
            <h3>Misses</h3>
            <p className="stat-value">{stats.misses || 0}</p>
          </div>
        </div>
      )}

      <form className="webhook-form" onSubmit={handleInvalidate}>
        <h3>Invalidate Cache</h3>
        <div className="webhook-field">
          <label>Key Pattern</label>
          <input type="text" value={pattern} onChange={(e) => setPattern(e.target.value)} placeholder="e.g. report:*" required />
        </div>
        <button type="submit" className="btn-generate">Invalidate</button>
      </form>

      <h3>Cache Entries</h3>
      <table className="reports-table">
        <thead>
          <tr>
            <th>Key</th>
            <th>TTL Remaining</th>
            <th>Access Count</th>
          </tr>
        </thead>
        <tbody>
          {entries.slice(0, 50).map((entry, i) => (
            <tr key={entry.key || i}>
              <td>{entry.key}</td>
              <td>{entry.ttl_remaining_seconds?.toFixed(1) || '—'}s</td>
              <td>{entry.access_count || 0}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {entries.length === 0 && <p className="empty-state">No cache entries.</p>}
    </div>
  );
}
