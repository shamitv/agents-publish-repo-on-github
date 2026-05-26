# Security Report: app-43-music-streaming

## Application Information

- **App ID**: app-43
- **App Name**: Music Streaming Playlist Service
- **Language**: JavaScript
- **Framework**: Express
- **Source**: `apps/javascript/app-43-music-streaming/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.js` → `GET /api/playlists/:id` (lines 146-162) | CWE-639 |
| V2 | A05 | Security Misconfiguration | Medium | `src/index.js` → `GET /api/system/status` (lines 208-228) | CWE-209 |
| V3 | A10 | Server-Side Request Forgery (SSRF) | High | `src/index.js` → `GET /api/cover` (lines 193-205) | CWE-918 |

### V1: IDOR on Playlist Details

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing private playlists by ID lacks checking user ownership, allowing any authenticated user to retrieve details of another listener's playlists.

**Endpoint**: `GET /api/playlists/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated user can view another user's private playlists by enumerating playlist IDs.

**Detection**: Look for absence of ownership checks in the playlist detail handler where the `:id` parameter is used without verifying the requesting user's identity against the playlist owner.

---

### V2: Diagnostics Endpoint Leaks Internal Token

**OWASP Category**: A05 — Security Misconfiguration

**Description**: An open diagnostics route leaks system node settings and an administrative metrics integration API token key when active debug query options are provided.

**Endpoint**: `GET /api/system/status`

**CWE**: CWE-209 (Information Exposure Through an Error Message)

**Impact**: Medium — An attacker can retrieve the metrics service API token `INTERNAL-METRICS-API-SECRET-2026`, which can be used to authenticate against internal analytics services.

**Detection**: Look for a diagnostics/debug endpoint that conditionally returns configuration objects including environment variables or hardcoded secrets based on a query parameter like `?debug=true`.

---

### V3: SSRF via Cover Art Proxy

**OWASP Category**: A10 — Server-Side Request Forgery (SSRF)

**Description**: The cover art query proxy makes HTTP calls using axios on user-supplied URL inputs with no address block restriction, enabling SSRF.

**Endpoint**: `GET /api/cover`

**CWE**: CWE-918 (Server-Side Request Forgery)

**Impact**: High — An attacker can make the server send crafted HTTP requests to internal network services, bypassing firewalls and accessing internal APIs or cloud metadata endpoints.

**Detection**: Look for an endpoint that accepts a user-controlled URL parameter and passes it directly to `axios.get()` or `fetch()` without any allowlist, denylist, or hostname validation.

---

## Chained Attack Scenario

### Chain: "Diagnostics Configuration Exposure → SSRF Playlist Analytics Pivoting"

**Impact**: `lateral_movement`

**Overview**: An attacker queries the diagnostics endpoint to obtain an internal metrics API token, then uses the SSRF-vulnerable cover art proxy to pivot to internal analytics services.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | System status endpoint leaks metrics integration API secret token key | Medium | A05 | CWE-209 | `GET /api/system/status` |
| 2 | Cover art proxy makes external requests with no IP filtering rules | Medium | A10 | CWE-918 | `GET /api/cover` |

**Attack Narrative**:
1. The attacker queries `GET /api/system/status?debug=true` to obtain the metrics service token key `INTERNAL-METRICS-API-SECRET-2026`.
2. Utilizing the cover lookup proxy at `GET /api/cover`, the attacker submits `url: 'http://localhost:8043/api/internal/analytics?token=INTERNAL-METRICS-API-SECRET-2026'`.
3. The server-side request (SSRF) bypasses authentication and retrieves all private playlists from the internal analytics database.

**Combined Impact**: Lateral movement — An attacker pivots from a public-facing diagnostics endpoint to access internal analytics databases by chaining secret leakage with SSRF.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.js` | Proper user scoping constraints in `GET /api/playlists` limiting output database entries to active listener only |
| `src/index.js` | Proper parameterized query logic in `POST /api/tracks` to add tracks to playlists safely |

---

## Detection Commands

```bash
# Find IDOR on playlist details
grep -n "playlists.*:id\|findOne\|findById" apps/javascript/app-43-music-streaming/src/index.js

# Find diagnostics endpoint leaking secrets
grep -n "status\|debug\|token\|secret\|metrics" apps/javascript/app-43-music-streaming/src/index.js

# Find SSRF vulnerable cover proxy
grep -n "axios\.get\|axios\.post\|fetch\|coverUrl" apps/javascript/app-43-music-streaming/src/index.js
```

---

*Report generated from `.vulns` manifest for app-43-music-streaming*