# Chained Vulnerability Scenarios — Pet Adoption

## Chain: "Diagnostics Configuration Exposure → Remote Code Execution via Insecure Deserialization"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Diagnostics config leaks layout secret key | Medium | A05 | `src/index.js` → `GET /api/system/diagnostics` |
| 2 | Layout metadata parsed via eval() | High | A08 | `src/index.js` → `POST /api/pets/layout` |


**Attack narrative**: 1. The attacker queries `/api/system/diagnostics?debug=true` to obtain the API key: `PET-PORTAL-DEV-LAYOUT-KEY-2026`.
2. The attacker calls `/api/pets/layout` passing the header `x-layout-token: PET-PORTAL-DEV-LAYOUT-KEY-2026`.
3. In the request body, they supply a malicious layoutConfig evaluated by eval, such as: `(function(){ require('child_process').execSync('whoami') })()`.
4. The server runs the command and returns the shell output, achieving full code execution.

**Combined Impact**: `account_takeover` — Attacker gains full control of the web server host.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
