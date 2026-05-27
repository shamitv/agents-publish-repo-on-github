import React from 'react';
import { useTranslation } from '../i18n/I18nContext';
import { useDashboard } from '../hooks/useDashboard';

export function DashboardPage() {
  const { t } = useTranslation();
  const { stats, loading, error, refresh } = useDashboard();

  if (loading) {
    return <div className="page-loading">{t('loading')}</div>;
  }

  if (error) {
    return (
      <div className="page-error">
        <p>{t('error_generic')}: {error}</p>
        <button onClick={refresh}>{t('reports_generate')}</button>
      </div>
    );
  }

  return (
    <div className="page dashboard-page">
      <h2>{t('dashboard_title')}</h2>
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>{t('dashboard_total_sales')}</h3>
            <p className="stat-value">${stats.total_sales.toLocaleString()}</p>
          </div>
          <div className="stat-card">
            <h3>{t('dashboard_total_orders')}</h3>
            <p className="stat-value">{stats.total_orders.toLocaleString()}</p>
          </div>
          <div className="stat-card">
            <h3>{t('dashboard_low_stock')}</h3>
            <p className="stat-value">{stats.low_stock_items}</p>
          </div>
          <div className="stat-card">
            <h3>{t('dashboard_data_quality')}</h3>
            <p className="stat-value">{stats.data_quality_score}%</p>
          </div>
        </div>
      )}
    </div>
  );
}