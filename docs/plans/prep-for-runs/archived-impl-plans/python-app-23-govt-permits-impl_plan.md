# Implementation Plan - Government Permit Application Portal (App 23)

This application has been implemented as a Django-based application using SQLite in-memory database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `permits/views.py` → `permit_detail()`
   - Vulnerable code: View returns permit details and associated documents without verifying if the user owns the permit or is staff.
2. **A05: Security Misconfiguration**:
   - Location: `govt_permits/settings.py`
   - Vulnerable code: `DEBUG = True`, `SECRET_KEY` hardcoded, `ALLOWED_HOSTS = ['*']`.
3. **A08: Software and Data Integrity Failures**:
   - Location: `permits/views.py` → `upload_document()`
   - Vulnerable code: Accepts arbitrary file extensions and saves files into predictable path exposed by Django's media server.

## Chained Attack
- **Chain-01**: Debug Page Info Leak (A05) → Unrestricted Upload (A08)
- Attacker triggers errors to read path config from Django DEBUG page, uploads an executable script, and calls it directly via media URL.

## Decoys
- CSRF middleware enabled on all forms.
- Role check on permit approval requiring staff access.
- Filtered permit list scoping ordinary citizens to their own permit records.
