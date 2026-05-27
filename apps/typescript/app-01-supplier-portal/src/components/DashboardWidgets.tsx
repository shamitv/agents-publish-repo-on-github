import React from 'react';

interface KPICardProps {
  title: string;
  value: string | number;
}

export function KPICard({ title, value }: KPICardProps) {
  return (
    <div className="stat-card">
      <h3>{title}</h3>
      <p className="stat-value">{value}</p>
    </div>
  );
}

// CHAIN LINK 1 (chain-03): CustomWidgetRenderer accepts raw HTML templates
// with no sanitization — attacker can inject script tags into saved widget config
interface CustomWidgetProps {
  htmlTemplate: string;
}

export function CustomWidgetRenderer({ htmlTemplate }: CustomWidgetProps) {
  return (
    <div className="custom-widget">
      <div dangerouslySetInnerHTML={{ __html: htmlTemplate }} />
    </div>
  );
}

interface RecentReportsProps {
  reports: Array<{ id: string; type: string; status: string; period: string }>;
}

export function RecentReports({ reports }: RecentReportsProps) {
  return (
    <div className="recent-reports">
      <h3>Recent Reports</h3>
      {reports.length === 0 ? (
        <p className="empty-state">No recent reports</p>
      ) : (
        <ul>
          {reports.slice(0, 5).map((r) => (
            <li key={r.id}>
              <strong>{r.type}</strong> — {r.period} <span className="status-text">{r.status}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
