# Security Report: app-11 — Social Media Analytics Dashboard

**Language:** Typescript (Express)
**Directory:** `apps/typescript/app-11-social-analytics`

---

## Application Information
- **App ID:** app-11
- **Name:** Social Media Analytics Dashboard
- **Language:** Typescript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A10 | Server-Side Request Forgery | High | src/services/PreviewService.ts | CWE-918 |
| V2 | A05 | Security Misconfiguration | Medium | src/controllers/DebugController.ts | CWE-200 |
| V3 | A01 | Broken Access Control | Medium | src/services/InternalSearchService.ts | CWE-287 |
| V4 | A03 | Injection | High | public/js/app.js | CWE-79 |
| V5 | A05 | Security Misconfiguration | Medium | public/js/app.js | CWE-312 |

---

## Standalone Vulnerabilities

### VULN-01: A10 — Server-Side Request Forgery

- **Severity:** High
- **Location:** `src/services/PreviewService.ts`:4-17 (method: `fetchPreview`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
Preview service fetches arbitrary caller-supplied URLs with axios and no internal network restrictions.

### VULN-02: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/controllers/DebugController.ts`:7-10 (method: `getConfig`)
- **CWE:** [CWE-200](https://cwe.mitre.org/data/definitions/200.html)

#### Description
Debug configuration endpoint exposes internal service URLs, tokens, and infrastructure connection strings.

### VULN-03: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/services/InternalSearchService.ts`:6-20 (method: `adminSearch`)
- **CWE:** [CWE-287](https://cwe.mitre.org/data/definitions/287.html)

#### Description
Internal search admin service trusts a leaked bearer-style token and exposes service topology.

### VULN-04: A03 — Injection

- **Severity:** High
- **Location:** `public/js/app.js`:64-80 (method: `loadWidgets`)
- **CWE:** [CWE-79](https://cwe.mitre.org/data/definitions/79.html)

#### Description
Widget titles are rendered with innerHTML without encoding, allowing stored XSS.

### VULN-05: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `public/js/app.js`:1-2 (method: `global`)
- **CWE:** [CWE-312](https://cwe.mitre.org/data/definitions/312.html)

#### Description
Internal reporting API key is hardcoded in the browser bundle.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Debug Config Leak → HTTP SSRF → Internal Search Pivot → Lateral Movement

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Medium
- **Subtlety Tags:** 

#### Prerequisites
- None specified

#### Attack Narrative
An attacker reads the debug configuration to discover the internal search URL and token, then sends that internal URL to the preview SSRF endpoint to access service topology unreachable from the public network.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | GET /api/debug/config exposes internal search URL, service token, and infrastructure connection strings. | Medium | A05 | CWE-200 | src/controllers/DebugController.ts | `getConfig` |
| 2 | POST /api/preview fetches the attacker-supplied internal search URL server-side with no IP or hostname restrictions. | Medium | A10 | CWE-918 | src/services/PreviewService.ts | `fetchPreview` |
| 3 | Internal search admin endpoint trusts the leaked service token and exposes internal search topology. | Low | A01 | CWE-287 | src/services/InternalSearchService.ts | `adminSearch` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/referenceGuards.ts | allowedCallback validates scheme and host against an allowlist and should not be flagged as SSRF. |
| src/cache/SessionCache.ts | Session cache stores opaque random session IDs generated with crypto.randomBytes. |
