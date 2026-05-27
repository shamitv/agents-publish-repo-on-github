import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from '../i18n/I18nContext';
import { useReports } from '../hooks/useReports';
import { JobStatusBadge } from '../components/JobStatusBadge';
import { DownloadButton } from '../components/DownloadButton';

export function ReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { reports } = useReports();
  const report = reports.find((r) => r.id === id);

  if (!report) {
    return (
      <div className="page-error">
        <p>{t('error_generic')}: Report not found</p>
        <button onClick={() => navigate('/reports')}>{t('report_detail_back')}</button>
      </div>
    );
  }

  return (
    <div className="page report-detail-page">
      <button className="btn-back" onClick={() => navigate('/reports')}>
        {t('report_detail_back')}
      </button>
      <h2>{t('report_detail_title')}</h2>
      <div className="detail-card">
        <div className="detail-row">
          <span className="detail-label">{t('report_detail_type')}</span>
          <span>{report.type}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">{t('report_detail_period')}</span>
          <span>{report.period}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">{t('report_detail_generated')}</span>
          <span>{new Date(report.generated_at).toLocaleString()}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Status</span>
          <JobStatusBadge status={report.status} />
        </div>
        <div className="detail-row">
          <span className="detail-label">{t('reports_download')}</span>
          <DownloadButton
            href={`/api/reports/download/${report.id}`}
            disabled={report.status !== 'ready'}
            label={t('reports_download')}
          />
        </div>
      </div>
    </div>
  );
}
