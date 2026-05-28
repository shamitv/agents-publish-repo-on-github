import React from 'react';

interface Props {
  href: string;
  disabled: boolean;
  label: string;
}

export function DownloadButton({ href, disabled, label }: Props) {
  if (disabled) {
    return <span className="btn-disabled">{label}</span>;
  }
  return (
    <a href={href} className="btn-download" download>
      {label}
    </a>
  );
}
