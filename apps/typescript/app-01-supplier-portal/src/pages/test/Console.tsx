import React, { useState } from 'react';

export function TestConsolePage() {
  const [command, setCommand] = useState('');
  const [output] = useState<string[]>([]);

  const handleRun = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`Mock console: ${command} (admin diagnostic placeholder)`);
  };

  return (
    <div className="page test-page">
      <h2>Admin Diagnostic Console</h2>
      <p className="test-note">Execute diagnostic commands. (Phase 5 placeholder)</p>

      <form onSubmit={handleRun} className="console-form">
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Enter diagnostic command..."
          className="console-input"
        />
        <button type="submit" className="btn-generate">Run</button>
      </form>

      <div className="console-output">
        {output.map((line, i) => (
          <p key={i}>{line}</p>
        ))}
        {output.length === 0 && <p className="empty-state">No output yet.</p>}
      </div>
    </div>
  );
}
