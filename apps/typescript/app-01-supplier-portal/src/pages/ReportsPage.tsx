import React from 'react';
import { useTranslation } from '../i18n/I18nContext';
import { useReports } from '../hooks/useReports';

export function ReportsPage() {
  const { t } = useTranslation();
  const { reports, loading, error, generateReport, refresh } = useReports();

  const handleGenerate = () => {
    generateReport('sales_summary').catch(() => {});
  };

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
    <div className="page reports-page">
      <h2>{t('reports_title')}</h2>
      <button className="btn-generate" onClick={handleGenerate}>
        {t('reports_generate')}
      </button>
      {reports.length === 0 ? (
        <p className="empty-state">{t('reports_no_reports')}</p>
      ) : (
        <table className="reports-table">
          <thead>
            <tr>
              <th>{t('report_detail_type')}</th>
              <th>{t('report_detail_period')}</th>
              <th>{t('report_detail_generated')}</th>
              <th>{t('reports_download')}</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((report) => (
              <tr key={report.id}>
                <td>{report.type}</td>
                <td>{report.period}</td>
                <td>{new Date(report.generated_at).toLocaleDateString()}</td>
                <td>
                  {/* CHAIN LINK 3 (chain-01): Unvalidated download URL from server response */}
                  <a
                    href={report.status === 'ready' ? `/api/reports/download/${report.id}` : '#'}
                    className={report.status === 'ready' ? 'btn-download' : 'btn-disabled'}
                  >
                    {t('reports_download')}
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}