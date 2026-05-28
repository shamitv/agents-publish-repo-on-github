import React from 'react';

interface Props {
  status: string;
}

const STATUS_COLORS: Record<string, string> = {
  queued: '#ff9800',
  pending: '#ff9800',
  running: '#2196f3',
  completed: '#4caf50',
  failed: '#f44336',
  ready: '#4caf50',
};

export function JobStatusBadge({ status }: Props) {
  const color = STATUS_COLORS[status.toLowerCase()] || '#9e9e9e';
  return (
    <span className="status-badge" style={{ backgroundColor: color }}>
      {status}
    </span>
  );
}
