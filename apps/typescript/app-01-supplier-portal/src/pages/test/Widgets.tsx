import React, { useState } from 'react';
import { CustomWidgetRenderer } from '../../components/DashboardWidgets';

export function TestWidgetsPage() {
  const [htmlInput, setHtmlInput] = useState('<h3>Hello</h3><p>Widget preview</p>');

  return (
    <div className="page test-page">
      <h2>Custom Widget Builder</h2>
      <p className="test-note">
        Design custom dashboard widgets using raw HTML. Preview shows rendered output.
      </p>

      <div className="widget-builder">
        <div className="widget-editor">
          <h3>HTML Template</h3>
          <textarea
            value={htmlInput}
            onChange={(e) => setHtmlInput(e.target.value)}
            rows={8}
            className="widget-textarea"
          />
        </div>

        <div className="widget-preview">
          <h3>Preview</h3>
          {/* CHAIN LINK 1 (chain-03): Custom widget renderer accepts raw HTML — no CSP or sanitization */}
          <CustomWidgetRenderer htmlTemplate={htmlInput} />
        </div>
      </div>
    </div>
  );
}
