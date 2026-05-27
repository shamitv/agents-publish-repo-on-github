import React, { useRef, useEffect } from 'react';

// DECOY: Safe notes renderer using textContent to prevent XSS
interface Props {
  notes: string;
}

export function ReportNotes({ notes }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.textContent = notes;
    }
  }, [notes]);

  return <div ref={ref} className="report-notes" />;
}
