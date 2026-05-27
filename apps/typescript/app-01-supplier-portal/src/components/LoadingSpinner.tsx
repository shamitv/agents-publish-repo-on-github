import React from 'react';

export function LoadingSpinner({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="loading-spinner">
      <div className="spinner" />
      <p>{text}</p>
    </div>
  );
}
