# Chained Vulnerability Scenarios — Govt Permits

## Chain: "Debug Page Info Leak → Unrestricted Upload → RCE"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Django DEBUG=True exposes settings, paths, and environment on error | Low | A05 | `govt_permits/settings.py` |
| 2 | Document upload endpoint allows uploading any file extension | Medium | A08 | `permits/views.py` → `upload_document()` |


**Attack narrative**: 1. The attacker accesses the portal and purposefully triggers an unhandled exception or 404 error page. Because `DEBUG = True` is enabled in `govt_permits/settings.py`, the details on the page reveal internal file system paths and settings.
2. The attacker authenticates as a normal citizen and files a permit application.
3. The attacker calls the upload endpoint at `/api/permits/<permit_id>/upload`, uploading a malicious Python payload named `exploit.py` as a document.
4. Due to missing filename sanitization or extension validation, the file is saved as-is in the predictable path `media/documents/exploit.py`.
5. Since the Django static files view is serving media files directly in debug mode, the attacker requests `/media/documents/exploit.py` or imports/triggers it, obtaining execution context or remote control over the app server environment.

**Combined Impact**: `lateral_movement` — The attacker gains execution capability on the local filesystem of the server.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
