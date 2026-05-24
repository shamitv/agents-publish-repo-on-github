# Security Report: app-40-pet-adoption

## Application Information

- **App ID**: app-40
- **App Name**: Pet Adoption Portal
- **Language**: JavaScript
- **Framework**: Express
- **Source**: `apps/javascript/app-40-pet-adoption/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | High | `src/index.js` → `GET /api/pets/search` (lines 151-163) | CWE-89 |
| V2 | A05 | Security Misconfiguration | Medium | `src/index.js` → `GET /api/system/diagnostics` (lines 184-198) | CWE-209 |
| V3 | A08 | Software and Data Integrity Failures | High | `src/index.js` → `POST /api/pets/layout` (lines 166-181) | CWE-502 |

### V1: SQL Injection on Pet Search

**OWASP Category**: A03 — Injection

**Description**: User search query input is directly concatenated into a raw SQL statement, leading to SQL injection.

**Endpoint**: `GET /api/pets/search`

**CWE**: CWE-89 (SQL Injection)

**Impact**: High — An attacker can extract arbitrary data from the database including user credentials, pet records, and adoption applications.

**Detection**: Search for raw string concatenation with user-supplied `q` or `query` parameters inside `db.all()` or `db.query()` calls in the search handler.

---

### V2: Diagnostics Endpoint Leaks Server Secrets

**OWASP Category**: A05 — Security Misconfiguration

**Description**: An open diagnostics route leaks server settings and a hardcoded administrative recovery API token when query parameters activate debug mode.

**Endpoint**: `GET /api/system/diagnostics`

**CWE**: CWE-209 (Information Exposure Through an Error Message)

**Impact**: Medium — An attacker can retrieve the layout configuration token `PET-PORTAL-DEV-LAYOUT-KEY-2026` from the diagnostics output, which is used as an authentication bypass for the layout endpoint.

**Detection**: Look for a diagnostics or debug endpoint that returns environment variables, file paths, or hardcoded strings containing tokens/secrets when a `?debug=true` flag is present.

---

### V3: Insecure Deserialization via eval() in Layout

**OWASP Category**: A08 — Software and Data Integrity Failures

**Description**: Layout configurations submitted by users are parsed using the insecure `eval()` constructor, enabling remote code execution on the server host.

**Endpoint**: `POST /api/pets/layout`

**CWE**: CWE-502 (Deserialization of Untrusted Data)

**Impact**: High — An attacker can inject arbitrary JavaScript code through the layout payload, achieving full remote code execution on the server.

**Detection**: Look for `eval()` calls or `new Function()` constructors that process user-supplied JSON or string data. Also look for authentication gates that check a header value against the leaked token.

---

## Chained Attack Scenario

### Chain: "Diagnostics Configuration Disclosure → Remote Code Execution via Insecure Deserialization"

**Impact**: `account_takeover`

**Overview**: An attacker retrieves the layout API token from the diagnostics endpoint, then uses it to submit a malicious layout containing eval()-based code execution.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | System diagnostics endpoint leaks layout customization token key | Medium | A05 | CWE-209 | `GET /api/system/diagnostics` |
| 2 | Layout update route executes custom strings using eval() without checks | Medium | A08 | CWE-502 | `POST /api/pets/layout` |

**Attack Narrative**:
1. The attacker sends `GET /api/system/diagnostics?debug=true` to obtain the layout configuration token `PET-PORTAL-DEV-LAYOUT-KEY-2026`.
2. Using this token in the `x-layout-token` header to bypass authentication, the attacker POSTs to `/api/pets/layout` with a layout configuration payload containing a system command execution string evaluated via `eval()` (e.g., `require('child_process').execSync('whoami')`).
3. The server executes the injected JavaScript, giving the attacker RCE and full account takeover capabilities.

**Combined Impact**: Account takeover — An attacker can achieve full remote code execution on the server by chaining token leakage with insecure deserialization.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.js` | Proper parameterized query logic in `POST /api/applications/apply` to record application entries safely |
| `src/index.js` | Proper Bcrypt hashing for password storage and validation |

---

## Detection Commands

```bash
# Find SQL injection vulnerable search
grep -n "SELECT.*\+.*req\.query\|db\.all.*req" apps/javascript/app-40-pet-adoption/src/index.js

# Find diagnostics endpoint leaking secrets
grep -n "diagnostics\|debug\|token\|secret" apps/javascript/app-40-pet-adoption/src/index.js

# Find eval() used for layout parsing
grep -n "eval\|new Function\|layout" apps/javascript/app-40-pet-adoption/src/index.js
```

---

*Report generated from `.vulns` manifest for app-40-pet-adoption*