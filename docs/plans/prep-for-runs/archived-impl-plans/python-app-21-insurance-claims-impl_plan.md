# Implementation Plan - Insurance Claims Processor (App 21)

This application has been implemented as a Flask-based microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `app.py` → `get_claim()`
   - Vulnerable code: Fetches claim by ID without validating if the current session's user owns the policy/claim.
2. **A03: Injection (SQL Injection)**:
   - Location: `app.py` → `search_claims()`
   - Vulnerable code: User query parameter is directly concatenated into a raw SQL query string.
3. **A09: Security Logging & Monitoring Failures**:
   - Location: `app.py` → `approve_claim()`
   - Vulnerable code: Financial transactions and administrative decisions (approving claims, issuing payouts) occur with zero logging/auditing.

## Chained Attack
- **Chain-01**: SQLi (A03) → IDOR (A01) → Logging Failure (A09)
- Attacker leaks claim records via SQLi, enumerates claims using IDOR, and initiates payout approvals without being logged.

## Decoys
- Secure parameterized SQL query for user login (`/api/auth/login`).
- Admin role authorization check on `/api/admin/stats`.
- Scoped policy query restricting customers to see only their own policies in `/api/policies`.
