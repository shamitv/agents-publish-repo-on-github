import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../i18n/I18nContext';
import { useReports } from '../hooks/useReports';
import { JobStatusBadge } from '../components/JobStatusBadge';
import { ReportNotes } from '../components/ReportNotes';

function ReportNotesCell({ notes }: { notes?: string }) {
  if (!notes) return <span className="no-notes">—</span>;

  // VULNERABILITY A06: Report notes rendered via dangerouslySetInnerHTML
  // without sanitization — XSS payload executes in supplier's browser session
  return <td dangerouslySetInnerHTML={{ __html: notes }} />;
}

export function ReportsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { reports, loading, error, generateReport, refresh } = useReports();

  const handleGenerate = () => {
    generateReport('sales').catch(() => {});
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
        <>
          {/* Decoy safe pattern: notes rendered via textContent */}
          <h3>Safe Notes Preview</h3>
          {reports.slice(0, 1).map((r) => (
            <ReportNotes key={r.id} notes={r.notes || 'No notes'} />
          ))}

          <table className="reports-table">
            <thead>
              <tr>
                <th>{t('report_detail_type')}</th>
                <th>{t('report_detail_period')}</th>
                <th>{t('report_detail_generated')}</th>
                <th>Status</th>
                <th>Notes</th>
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
                    <JobStatusBadge status={report.status} />
                  </td>
                  {/* VULNERABILITY A06: XSS via report notes */}
                  <ReportNotesCell notes={report.notes} />
                  <td>
                    <button
                      className={report.status === 'completed' || report.status === 'ready' ? 'btn-download' : 'btn-disabled'}
                      onClick={() => report.status === 'completed' || report.status === 'ready' ? navigate(`/reports/${report.id}`) : undefined}
                    >
                      {t('reports_download')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
