# Chained Vulnerability Scenarios — Digital Assets

## Chain: "SSRF File Fetch → Predictable Path RCE"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SSRF in asset import fetches arbitrary network URLs | Medium | A10 | `src/index.ts` → `POST /api/assets/import` |
| 2 | Unrestricted upload stores fetched script in public path | High | A08 | `src/index.ts` → `POST /api/assets/import` |


**Attack narrative**: 1. The attacker authenticates as a standard user.
2. The attacker triggers the import feature `/api/assets/import` with `url` and `filename` parameters. 
3. The server executes a `fetch` request to the target URL. Because the server does not check IP ranges, the attacker can specify internal network URLs.
4. The attacker provides a URL hosting a malicious JavaScript file (e.g. `http://attacker-internal/payload.js`) and sets the output filename to `payload.js`.
5. The server downloads the file and saves it in the public uploads directory `public/uploads/payload.js` without validating the `.js` extension.
6. The attacker invokes the script directly by calling `/uploads/payload.js` via HTTP, executing commands on the host server.

**Combined Impact**: `lateral_movement` — Attacker achieves Remote Code Execution (RCE) on the server environment.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
