# Security Report: app-43 — Music Streaming Playlist Service

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-43-music-streaming`

---

## Application Information
- **App ID:** app-43
- **Name:** Music Streaming Playlist Service
- **Language:** Javascript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/index.js | CWE-639 |
| V2 | A05 | Security Misconfiguration | Medium | src/index.js | CWE-209 |
| V3 | A10 | Server-Side Request Forgery (SSRF) | High | src/index.js | CWE-918 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/index.js`:146-162 (method: `GET /api/playlists/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Viewing private playlists by ID lacks checking user ownership, allowing any authenticated user to retrieve details of another listener's playlists.

### VULN-02: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/index.js`:208-228 (method: `GET /api/system/status`)
- **CWE:** [CWE-209](https://cwe.mitre.org/data/definitions/209.html)

#### Description
An open diagnostics route leaks system node settings and an administrative metrics integration API token key when active debug query options are provided.

### VULN-03: A10 — Server-Side Request Forgery (SSRF)

- **Severity:** High
- **Location:** `src/index.js`:193-205 (method: `GET /api/cover`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
The cover art query proxy makes HTTP calls using axios on user-supplied URL inputs with no address block restriction, enabling SSRF.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Diagnostics Configuration Exposure → SSRF Playlist Analytics Pivoting

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
An attacker queries `/api/system/status?debug=true` to obtain the metrics service token key `INTERNAL-METRICS-API-SECRET-2026`. Utilizing the cover lookup proxy `/api/cover`, they submit `url: 'http://localhost:8043/api/internal/analytics?token=INTERNAL-METRICS-API-SECRET-2026'`, leveraging the SSRF vulnerability to bypass authentication and retrieve all private playlists from the internal analytics database.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | System status endpoint leaks metrics integration API secret token key. | Medium | A05 | CWE-209 | src/index.js | `GET /api/system/status` |
| 2 | Cover art proxy makes external requests with no IP filtering rules. | Medium | A10 | CWE-918 | src/index.js | `GET /api/cover` |

### CHAIN-02: Subtle Ssrf Pivot To Idor

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy` `secondary_chain`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | The cover art query proxy makes HTTP calls using axios on user-supplied URL inputs with no address block restriction, enabling SSRF. | High | A10 | CWE-918 | src/index.js | `GET /api/cover` |
| 2 | An open diagnostics route leaks system node settings and an administrative metrics integration API token key when active debug query options are provided. | Medium | A05 | CWE-209 | src/index.js | `GET /api/system/status` |
| 3 | Viewing private playlists by ID lacks checking user ownership, allowing any authenticated user to retrieve details of another listener's playlists. | Medium | A01 | CWE-639 | src/index.js | `GET /api/playlists/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Proper user scoping constraints in GET /api/playlists limiting output database entries to active listener only. |
| src/index.js | Proper parameterized query logic in POST /api/tracks to add tracks to playlists safely. |
