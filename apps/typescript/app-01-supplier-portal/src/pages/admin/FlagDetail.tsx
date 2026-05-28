import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { LoadingSpinner } from '../../components/LoadingSpinner';

export function AdminFlagDetailPage() {
  const { key } = useParams<{ key: string }>();
  const navigate = useNavigate();
  const [flag, setFlag] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get(`/admin/flags/${key}`);
        setFlag(res.data);
      } catch (err: any) {
        setError(err.message || 'Flag not found');
      } finally {
        setLoading(false);
      }
    })();
  }, [key]);

  if (loading) return <LoadingSpinner text="Loading flag detail..." />;
  if (error) return <div className="page-error">{error}</div>;
  if (!flag) return <div className="page-error">Flag not found</div>;

  return (
    <div className="page admin-page">
      <button className="btn-back" onClick={() => navigate('/admin/flags')}>Back to Flags</button>
      <h2>Flag Detail: {flag.key}</h2>
      <div className="detail-card">
        <div className="detail-row">
          <span className="detail-label">Key</span>
          <span>{flag.key}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Enabled</span>
          <span className={`status-badge`} style={{ backgroundColor: flag.enabled ? '#4caf50' : '#f44336' }}>
            {flag.enabled ? 'ON' : 'OFF'}
          </span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Description</span>
          {/* CHAIN LINK 2 (chain-03): Description rendered via dangerouslySetInnerHTML
              — unsanitized metadata enables stored XSS in admin console */}
          <span dangerouslySetInnerHTML={{ __html: flag.description }} />
        </div>
        <div className="detail-row">
          <span className="detail-label">Owner</span>
          <span>{flag.owner}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Created</span>
          <span>{flag.created_at ? new Date(flag.created_at * 1000).toLocaleString() : '—'}</span>
        </div>
      </div>
    </div>
  );
}
