import React from 'react';
import { useTranslation } from '../i18n/I18nContext';
import { useDashboard } from '../hooks/useDashboard';
import { KPICard, CustomWidgetRenderer, RecentReports } from '../components/DashboardWidgets';
import { useReports } from '../hooks/useReports';

export function DashboardPage() {
  const { t } = useTranslation();
  const { stats, loading, error, refresh } = useDashboard();
  const { reports } = useReports();

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
          <KPICard title={t('dashboard_total_sales')} value={`$${stats.total_sales?.toLocaleString() || '0'}`} />
          <KPICard title={t('dashboard_total_orders')} value={stats.total_orders?.toLocaleString() || '0'} />
          <KPICard title={t('dashboard_low_stock')} value={stats.low_stock_items || '0'} />
          <KPICard title={t('dashboard_data_quality')} value={`${stats.data_quality_score || '0'}%`} />
        </div>
      )}

      <RecentReports reports={reports.map((r) => ({ id: r.id, type: r.type, status: r.status, period: r.period }))} />

      <div className="custom-widgets-section">
        <h3>Custom Widget Preview</h3>
        {/* CHAIN LINK 1 (chain-03): Custom widget renders raw HTML — no sanitization */}
        <CustomWidgetRenderer htmlTemplate="<p style='color:#666'>Dashboard widget <strong>active</strong></p>" />
      </div>
    </div>
  );
}
