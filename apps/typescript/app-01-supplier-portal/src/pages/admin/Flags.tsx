import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { LoadingSpinner } from '../../components/LoadingSpinner';

interface FeatureFlag {
  key: string;
  enabled: boolean;
  description: string;
  owner: string;
}

export function AdminFlagsPage() {
  const navigate = useNavigate();
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchFlags = async () => {
    try {
      setLoading(true);
      const res = await api.get('/admin/flags');
      const data = res.data;
      setFlags(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(err.message || 'Failed to load flags');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchFlags(); }, []);

  const handleToggle = async (key: string) => {
    try {
      await api.post(`/admin/flags/${key}/toggle`);
      await fetchFlags();
    } catch (err: any) {
      setError(err.message || 'Toggle failed');
    }
  };

  if (loading) return <LoadingSpinner text="Loading feature flags..." />;
  if (error) return <div className="page-error">{error}</div>;

  return (
    <div className="page admin-page">
      <h2>Feature Flags</h2>
      <table className="reports-table">
        <thead>
          <tr>
            <th>Key</th>
            <th>Description</th>
            <th>Owner</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {flags.map((flag) => (
            <tr key={flag.key}>
              <td><strong>{flag.key}</strong></td>
              <td>{flag.description}</td>
              <td>{flag.owner}</td>
              <td>
                <span className={`status-badge`} style={{ backgroundColor: flag.enabled ? '#4caf50' : '#f44336' }}>
                  {flag.enabled ? 'ON' : 'OFF'}
                </span>
              </td>
              <td>
                <button className="btn-download" onClick={() => navigate(`/admin/flags/${flag.key}`)}>Detail</button>
                <button className="btn-generate" style={{ marginLeft: '0.5rem' }} onClick={() => handleToggle(flag.key)}>
                  Toggle
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
