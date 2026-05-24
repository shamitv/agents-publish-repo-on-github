# Implementation Plan - Charity Donation Platform (App 46)

This application has been implemented as a Flask-based microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A02: Cryptographic Failures**:
   - Location: `app.py` → `STRIPE_KEY`
   - Vulnerable code: Hardcoded Stripe secret key constant.
2. **A03: Injection (SQL Injection)**:
   - Location: `app.py` → `search_donations()`
   - Vulnerable code: Input value is directly formatted into SQLite query.
3. **A09: Security Logging & Monitoring Failures**:
   - Location: `app.py` → `process_refund()`
   - Vulnerable code: Donation refund triggers with zero audit logging.

## Chained Attack
- **Chain-01**: API Key Exposure (A02) → SQLi Donor Dump (A03) → Silent Refund Fraud (A09)
- Attacker reads Stripe secret key, performs SQLi to leak transaction IDs, and silently executes refunds.

## Decoys
- Proper CSRF validation check requiring a matching header token for donation submissions.
- Parameterized SQL query for campaign listing.
