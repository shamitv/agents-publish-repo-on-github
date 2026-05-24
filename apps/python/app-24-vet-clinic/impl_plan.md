# Implementation Plan - Veterinary Clinic Management (App 24)

This application has been implemented as a FastAPI-based microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A02: Cryptographic Failures**:
   - Location: `app.py` → `generate_token()`
   - Vulnerable code: Uses a hardcoded weak secret key `secret123` to sign JWT tokens.
2. **A03: Injection (SQL Injection)**:
   - Location: `app.py` → `search_pets()`
   - Vulnerable code: User query is concatenated directly into a raw SQL `SELECT` query.
3. **A09: Security Logging & Monitoring Failures**:
   - Location: `app.py` → `update_prescription()`
   - Vulnerable code: Crucial drug prescription updates occur without writing any audit log entries.

## Chained Attack
- **Chain-01**: Weak JWT (A02) → SQLi (A03) → Logging Failure (A09)
- Attacker forges Vet role JWT, queries all records using SQLi, and updates drug prescriptions silently.

## Decoys
- Input validation on pet age and weight using Pydantic field validators.
- Proper audit logging and parameterized queries for appointment scheduling.
