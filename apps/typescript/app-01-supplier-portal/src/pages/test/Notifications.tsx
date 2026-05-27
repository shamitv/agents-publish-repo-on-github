import React, { useState } from 'react';

export function TestNotificationsPage() {
  const [prefs, setPrefs] = useState({
    emailReports: true,
    slackAlerts: false,
    weeklyDigest: true,
  });

  return (
    <div className="page test-page">
      <h2>Notification Preferences</h2>
      <p className="test-note">Configure how you receive report notifications.</p>

      <div className="prefs-card">
        {Object.entries(prefs).map(([key, value]) => (
          <label key={key} className="pref-row">
            <input
              type="checkbox"
              checked={value}
              onChange={() => setPrefs((p) => ({ ...p, [key]: !p[key as keyof typeof p] }))}
            />
            <span>{key.replace(/([A-Z])/g, ' $1').replace(/^./, (s) => s.toUpperCase())}</span>
          </label>
        ))}
      </div>
      <button className="btn-generate" onClick={() => alert('Preferences saved (mock)')}>
        Save Preferences
      </button>
    </div>
  );
}
