# Government Permit Application Portal

## Overview
A Django application representing a government citizen portal where residents can file permit applications, upload supporting documentation, and track application reviews.

## Business Domain
Government & Public Services

## Tech Stack
- Python 3.10
- Django 4.2
- SQLite (in-memory)

## Features
- Citizen registration & login
- File permit applications (e.g., Residential Building Permit, Commercial Zone License)
- Upload supporting documents (e.g. site plans, blueprints)
- Citizen dashboard to track owned permits
- Reviewer dashboard to approve or reject applications

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/python/app-23-govt-permits/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Debug Page Info Leak → Unrestricted Upload → RCE"

An attacker uses a Django debug page to perform reconnaissance of internal file system paths, then uploads a malicious script without restriction, and executes it via direct media access.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Django DEBUG=True exposes settings, paths, and environment on error | Low | A05 | `govt_permits/settings.py` |
| 2 | Document upload endpoint allows uploading any file extension | Medium | A08 | `permits/views.py` → `upload_document()` |

**Attack narrative**:
1. The attacker accesses the portal and purposefully triggers an unhandled exception or 404 error page. Because `DEBUG = True` is enabled in `govt_permits/settings.py`, the details on the page reveal internal file system paths and settings.
2. The attacker authenticates as a normal citizen and files a permit application.
3. The attacker calls the upload endpoint at `/api/permits/<permit_id>/upload`, uploading a malicious Python payload named `exploit.py` as a document.
4. Due to missing filename sanitization or extension validation, the file is saved as-is in the predictable path `media/documents/exploit.py`.
5. Since the Django static files view is serving media files directly in debug mode, the attacker requests `/media/documents/exploit.py` or imports/triggers it, obtaining execution context or remote control over the app server environment.

**Combined Impact**: `lateral_movement` — The attacker gains execution capability on the local filesystem of the server.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/login` | None | User login and session creation |
| POST   | `/api/auth/logout` | Session | User logout |
| GET    | `/api/permits` | Session | List permit applications (Decoy: scoped citizen lookup) |
| GET    | `/api/permits/<permit_id>` | Session | Get permit details (vulnerable to IDOR) |
| POST   | `/api/permits/<permit_id>/upload` | Session | Upload permit document (vulnerable to unrestricted upload) |
| POST   | `/api/permits/<permit_id>/approve` | Staff/Reviewer | Approve or reject permit (Decoy: proper staff check) |

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the Django dev server:
   ```bash
   python manage.py runserver 8093
   ```
3. The application runs on port `8093`. The database is created in-memory and seeded automatically.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-23-govt-permits .
   ```
2. Run the container:
   ```bash
   docker run -p 8093:8093 app-23-govt-permits
   ```
