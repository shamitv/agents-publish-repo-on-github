# Chained Vulnerability Scenarios — Construction Tracker

## Chain: "IDOR Information Mining → Insecure Deserialization Remote Code Execution"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Contract details is vulnerable to IDOR | Medium | A01 | `src/index.js` → `GET /api/contracts/:id` |
| 2 | Template configuration evaluated via eval() | High | A08 | `src/index.js` → `POST /api/contracts/template` |


**Attack narrative**: 1. The attacker logs in as a manager, and queries `/api/contracts/1` to mine road construction configurations.
2. The attacker calls `/api/contracts/template`.
3. In the request body, they supply a malicious custom template evaluated by eval: `(function(){ require('child_process').execSync('whoami') })()`.
4. The server runs the command and returns the shell output, achieving full code execution.

**Combined Impact**: `account_takeover` — Attacker gains full control of the web server host.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
