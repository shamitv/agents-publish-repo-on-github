# Security Report: app-37 — Agricultural Crop Planner

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-37-crop-planner`

---

## Application Information
- **App ID:** app-37
- **Name:** Agricultural Crop Planner
- **Language:** Javascript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A05 | Security Misconfiguration | Medium | src/index.js | CWE-209 |
| V2 | A06 | Vulnerable and Outdated Components | High | src/index.js | CWE-22 |
| V3 | A10 | Server-Side Request Forgery (SSRF) | High | src/index.js | CWE-918 |

---

## Standalone Vulnerabilities

### VULN-01: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/index.js`:208-228 (method: `GET /api/system/config`)
- **CWE:** [CWE-209](https://cwe.mitre.org/data/definitions/209.html)

#### Description
An open diagnostics route leaks system node settings and an administrative weather integration API token key when active debug query options are provided.

### VULN-02: A06 — Vulnerable and Outdated Components

- **Severity:** High
- **Location:** `src/index.js`:157-190 (method: `POST /api/crop-plan/import-layout`)
- **CWE:** [CWE-22](https://cwe.mitre.org/data/definitions/22.html)

#### Description
An layout zip importer extracts files using relative archive paths without checking target folder bounds, allowing Zip Slip path traversal file overwrite.

### VULN-03: A10 — Server-Side Request Forgery (SSRF)

- **Severity:** High
- **Location:** `src/index.js`:193-205 (method: `GET /api/weather/proxy`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
The weather forecast query proxy makes HTTP calls using axios on user-supplied URL inputs with no address block restriction, enabling SSRF.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Diagnostics Configuration Exposure → SSRF Crop Analytics Pivoting

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker queries `/api/system/config?debug=true` to obtain the weather service token key `CROP-DEV-WEATHER-API-TOKEN-2026`. Utilizing the weather lookup proxy `/api/weather/proxy`, they submit `weatherUrl: 'http://localhost:8037/api/internal/telemetry?token=CROP-DEV-WEATHER-API-TOKEN-2026'`, leveraging the SSRF vulnerability to bypass authentication and retrieve all farm crop records from the internal analytics database.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | System diagnostics endpoint leaks weather integration API secret token key. | Medium | A05 | CWE-209 | src/index.js | `GET /api/system/config` |
| 2 | Weather query proxy makes external requests with no IP filtering rules. | Medium | A10 | CWE-918 | src/index.js | `GET /api/weather/proxy` |

### CHAIN-02: Subtle Ssrf Pivot To Injection

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
| 1 | The weather forecast query proxy makes HTTP calls using axios on user-supplied URL inputs with no address block restriction, enabling SSRF. | High | A10 | CWE-918 | src/index.js | `GET /api/weather/proxy` |
| 2 | An layout zip importer extracts files using relative archive paths without checking target folder bounds, allowing Zip Slip path traversal file overwrite. | High | A06 | CWE-22 | src/index.js | `POST /api/crop-plan/import-layout` |
| 3 | An open diagnostics route leaks system node settings and an administrative weather integration API token key when active debug query options are provided. | Medium | A05 | CWE-209 | src/index.js | `GET /api/system/config` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Proper user scoping constraints in GET /api/crops limiting output database entries to active customer only. |
| src/index.js | Proper parameterized query logic in GET /api/crops/:id to fetch crop profile details safely. |
