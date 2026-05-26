# Security Report: app-37-crop-planner

## Application Information

- **App ID**: app-37
- **App Name**: Agricultural Crop Planner
- **Language**: JavaScript
- **Framework**: Express
- **Source**: `apps/javascript/app-37-crop-planner/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A05 | Security Misconfiguration | Medium | `src/index.js` → `GET /api/system/config` (lines 208-228) | CWE-209 |
| V2 | A06 | Vulnerable and Outdated Components | High | `src/index.js` → `POST /api/crop-plan/import-layout` (lines 157-190) | CWE-22 |
| V3 | A10 | Server-Side Request Forgery (SSRF) | High | `src/index.js` → `GET /api/weather/proxy` (lines 193-205) | CWE-918 |

### V1: Diagnostics Endpoint Leaks Configuration Secrets

**OWASP Category**: A05 — Security Misconfiguration

**Description**: An open diagnostics route leaks system node settings and an administrative weather integration API token key when active debug query options are provided.

**Endpoint**: `GET /api/system/config`

**CWE**: CWE-209 (Information Exposure Through an Error Message)

**Impact**: Medium — An attacker can retrieve the weather service API token `CROP-DEV-WEATHER-API-TOKEN-2026`, which can be used to authenticate against internal services.

**Detection**: Look for a debug endpoint that conditionally returns configuration objects including environment variables or hardcoded secrets based on a query parameter like `?debug=true`.

---

### V2: Zip Slip Path Traversal in Layout Importer

**OWASP Category**: A06 — Vulnerable and Outdated Components

**Description**: A layout zip importer extracts files using relative archive paths without checking target folder bounds, allowing Zip Slip path traversal file overwrite.

**Endpoint**: `POST /api/crop-plan/import-layout`

**CWE**: CWE-22 (Path Traversal)

**Impact**: High — An attacker can craft a malicious ZIP archive containing entries with `../` path components to overwrite arbitrary files on the server filesystem, potentially achieving code execution.

**Detection**: Search for ZIP extraction logic that does not validate or sanitize individual entry paths against an expected extraction directory.

---

### V3: SSRF via Weather Query Proxy

**OWASP Category**: A10 — Server-Side Request Forgery (SSRF)

**Description**: The weather forecast query proxy makes HTTP calls using axios on user-supplied URL inputs with no address block restriction, enabling SSRF.

**Endpoint**: `GET /api/weather/proxy`

**CWE**: CWE-918 (Server-Side Request Forgery)

**Impact**: High — An attacker can make the server send crafted HTTP requests to internal network services, bypassing firewalls and accessing internal APIs, cloud metadata endpoints, or other restricted resources.

**Detection**: Look for an endpoint that accepts a user-controlled URL parameter and passes it directly to `axios.get()` or `fetch()` without any allowlist, denylist, or hostname validation.

---

## Chained Attack Scenario

### Chain: "Diagnostics Configuration Exposure → SSRF Crop Analytics Pivoting"

**Impact**: `lateral_movement`

**Overview**: An attacker first retrieves the internal API token from a misconfigured diagnostics endpoint, then uses the SSRF-vulnerable weather proxy to pivot to internal services.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | System diagnostics endpoint leaks weather integration API secret token key | Medium | A05 | CWE-209 | `GET /api/system/config` |
| 2 | Weather query proxy makes external requests with no IP filtering rules | Medium | A10 | CWE-918 | `GET /api/weather/proxy` |

**Attack Narrative**:
1. The attacker queries `GET /api/system/config?debug=true` to obtain the weather service token key `CROP-DEV-WEATHER-API-TOKEN-2026`.
2. Utilizing the weather lookup proxy at `GET /api/weather/proxy`, the attacker submits `weatherUrl: 'http://localhost:8037/api/internal/telemetry?token=CROP-DEV-WEATHER-API-TOKEN-2026'`.
3. The server-side request (SSRF) bypasses authentication and retrieves all farm crop records from the internal analytics database.

**Combined Impact**: Lateral movement — An attacker pivots from a public-facing diagnostics endpoint to access internal telemetry databases by chaining secret leakage with SSRF.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.js` | Proper user scoping constraints in `GET /api/crops` limiting output database entries to active customer only |
| `src/index.js` | Proper parameterized query logic in `GET /api/crops/:id` to fetch crop profile details safely |

---

## Detection Commands

```bash
# Find diagnostic endpoint leaking secrets
grep -n "debug\|config\|token\|secret" apps/javascript/app-37-crop-planner/src/index.js

# Find Zip Slip vulnerable extraction
grep -n "extract\|unzip\|zip\|\.path\|\.fileName" apps/javascript/app-37-crop-planner/src/index.js

# Find SSRF vulnerable proxy endpoint
grep -n "axios\.get\|axios\.post\|fetch" apps/javascript/app-37-crop-planner/src/index.js
```

---

*Report generated from `.vulns` manifest for app-37-crop-planner*