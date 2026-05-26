# Audit Report: app-23 — Government Permit Application Portal

**Language:** Python (Django)  
**Business Domain:** Government / Permits  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR on Permit Details)

**Severity:** Medium  
**Location:** `permits/views.py:56-82` — `permit_detail()`  
**Lines:**
```python
# VULNERABILITY A01: IDOR on permit details.
# Any authenticated user can view any permit application by ID.
# No check is performed to verify if the requesting user is the applicant or staff/reviewer.
def permit_detail(request, permit_id):
    ...
    permit = Permit.objects.get(id=permit_id)  # No ownership check
```

**Difficulty: EASY**

- Comment at line 56-58 explicitly marks it as `VULNERABILITY A01`
- Uses `Permit.objects.get(id=permit_id)` with zero ownership filtering
- Any authenticated user can view any permit by iterating IDs
- Contrasts with the decoy `permit_list()` endpoint which properly scopes queries per user

### VULN-02: A05 — Security Misconfiguration (Debug Mode & Hardcoded Secret)

**Severity:** Medium  
**Location:** `govt_permits/settings.py` — settings  
**Lines:**
```python
SECRET_KEY = 'django-insecure-dev-key-12345'
DEBUG = True
ALLOWED_HOSTS = ['*']
```

**Difficulty: EASY**

- `DEBUG=True` exposes detailed tracebacks, environment variables, and source code snippets on errors
- `SECRET_KEY` is a predictable hardcoded value — enables session forgery
- `ALLOWED_HOSTS = ['*']` creates SSRF and host header injection surface area
- All three settings are immediately visible in settings.py

### VULN-03: A08 — Software & Data Integrity Failures (Unrestricted File Upload)

**Severity:** High  
**Location:** `permits/views.py:84-115` — `upload_document()`  
**Lines:**
```python
# VULNERABILITY A08: Software and Data Integrity Failures (Unrestricted File Upload).
# The upload endpoint accepts any file type (e.g. .py, .sh, executable files)
# and saves it to a predictable directory under media root.
...
fs = FileSystemStorage()
filename = fs.save(f"documents/{uploaded_file.name}", uploaded_file)
```

**Difficulty: EASY**

- Comment at line 84-87 explicitly marks it as `VULNERABILITY A08`
- No file extension, MIME type, or content-type validation
- Files are saved with their original names in a predictable path
- With `DEBUG=True`, Django's static/media file handler serves uploaded files directly

---

## Chained Attack: chain-01

**Chain Name:** Debug Page Info Leak → Unrestricted Upload → RCE  
**Combined Impact:** Lateral Movement  
**Overall Chain Difficulty: EASY**

### Link 1: Debug Mode Leaks Internal Paths (A05 — Low)

**Location:** `govt_permits/settings.py` — `DEBUG=True`  
**Difficulty: EASY**

- Comment at line 84-87 (chain-linked in upload) references debug mode availability
- Attacker triggers an error (e.g. invalid ID, missing parameter) to get a debug traceback
- Debug page reveals MEDIA_ROOT, MEDIA_URL, file system paths, and database config
- This information is critical to locate uploaded files for the next step

### Link 2: Upload Arbitrary Executable via Unrestricted Upload (A08 — Medium)

**Location:** `permits/views.py:88-115` — `upload_document()`  
**Difficulty: EASY**

- Comment at line 85-87 marks it as `CHAIN LINK 2 (chain-01)`
- Attacker uploads a `.py` script (e.g. `exploit.py`) as a "document"
- File is saved to the predictable media directory with its original name
- Using the MEDIA_URL path learned from the debug page, attacker accesses the uploaded file directly
- With `DEBUG=True`, the Django dev server serves static/media files, executing Python files or serving malicious content

---

## Hints in Code (Beyond Explicit Annotations)

| Hint | Location | Description | Usefulness |
|------|----------|-------------|------------|
| `Permit.objects.get(id=permit_id)` | Line 64 | No ownership filter on permit lookup | **High** — IDOR indicator |
| `filename = fs.save(f"documents/{uploaded_file.name}", uploaded_file)` | Line 103 | Predictable path with original filename | **High** — unrestricted upload |
| No file extension check | Lines 100-103 | Absence of `if uploaded_file.name.endswith(...)` | **High** — allows .py files |
| `DEBUG=True` in settings | settings.py | Debug mode enabled in production | **High** — info leak enabler |
| `SECRET_KEY = 'django-insecure-dev-key-12345'` | settings.py | Hardcoded weak secret key | **High** — session tampering |
| Decoy: scoped query in `permit_list()` | Lines 39-44 | Proper ownership filter on list endpoint | **Medium** — contrasts with IDOR |
| Decoy: `is_staff` check on `approve_permit()` | Lines 120-124 | Proper privilege check on admin action | **Medium** — contrasts with upload |

## Summary

App-23 is a Django-based government permits portal with three vulnerabilities. The IDOR on `permit_detail` allows any authenticated user to view any permit application. The `DEBUG=True` and hardcoded `SECRET_KEY` in settings create a security misconfiguration that enables both info leakage and session manipulation. The unrestricted file upload is the most severe — it accepts `.py` scripts with no validation. The chained attack uses debug page leaks to learn file paths, then uploads and executes malicious scripts. All vulnerabilities are EASY difficulty with explicit annotation comments.

**Overall Difficulty Score:** 1/5 (Easy — all indicators are explicit and clearly visible)