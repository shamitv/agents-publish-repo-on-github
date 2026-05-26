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
| V1 | A10 | Server-Side Request Forgery | High | src/index.ts | CWE-918 |
| V2 | A03 | Injection | High | public/js/app.js | CWE-79 |
| V3 | A05 | Security Misconfiguration | Medium | public/js/app.js | CWE-312 |

---

## Standalone Vulnerabilities

### VULN-01: A10 — Server-Side Request Forgery

- **Severity:** High
- **Location:** `src/index.ts`:100-115 (method: `generatePreview`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
Server-Side Request Forgery (SSRF) in URL preview generation. The /api/preview endpoint fetches remote URLs using axios.get without verifying the target domain or restricting internal IP spaces.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `public/js/app.js`:80-100 (method: `renderWidgets`)
- **CWE:** [CWE-79](https://cwe.mitre.org/data/definitions/79.html)

#### Description
Cross-Site Scripting (XSS). The frontend renders dashboard widget titles directly into the DOM using innerHTML without HTML entity encoding, allowing execution of arbitrary Javascript.

### VULN-03: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `public/js/app.js`:1-10 (method: `global`)
- **CWE:** [CWE-312](https://cwe.mitre.org/data/definitions/312.html)

#### Description
Security Misconfiguration. Sensitive internal reporting API keys are hardcoded directly into the client-side JavaScript bundle, exposing them to any end-user.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: SSRF to Cloud Metadata → Full Credential Response → IAM Key Exfiltration

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker posts the AWS IMDS URL to the SSRF preview endpoint; the now-untruncated response returns full IAM credential JSON including AccessKeyId, SecretAccessKey, and Token, enabling lateral movement across the cloud environment.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | POST /api/preview fetches any URL server-side via axios without IP or hostname validation, allowing access to cloud metadata services at 169.254.169.254 | Medium | A10 | CWE-918 | src/index.ts | `POST /api/preview` |
| 2 | SSRF response body previously truncated to 500 chars; truncation removed, returning the full metadata credential payload (600+ bytes for AWS IMDSv1) | Low | A05 | CWE-200 | src/index.ts | `POST /api/preview` |
| 3 | GET /api/debug/headers returns all request headers verbatim including internal proxy headers injected by cloud load balancers | Low | A05 | CWE-200 | src/index.ts | `GET /api/debug/headers` |

### CHAIN-02: Subtle State Confusion Pivot To Ssrf

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy` `secondary_chain`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Security Misconfiguration. Sensitive internal reporting API keys are hardcoded directly into the client-side JavaScript bundle, exposing them to any end-user. | Medium | A05 | CWE-312 | public/js/app.js | `global` |
| 2 | Cross-Site Scripting (XSS). The frontend renders dashboard widget titles directly into the DOM using innerHTML without HTML entity encoding, allowing execution of arbitrary Javascript. | High | A03 | CWE-79 | public/js/app.js | `renderWidgets` |
| 3 | Server-Side Request Forgery (SSRF) in URL preview generation. The /api/preview endpoint fetches remote URLs using axios.get without verifying the target domain or restricting internal IP spaces. | High | A10 | CWE-918 | src/index.ts | `generatePreview` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.ts | Standard parameterized database mock queries. |
