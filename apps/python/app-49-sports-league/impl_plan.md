# Implementation Plan - Sports League Management (App 49)

This application has been implemented as a Flask-based microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `app.py` → `get_player()` and `update_score()`
   - Vulnerable code: Returns private player contract/salary details without checks, and allows any logged-in user to modify game scores.
2. **A03: Injection (SQL Injection)**:
   - Location: `app.py` → `search_players()`
   - Vulnerable code: Player search name input directly formatted into raw SQL select query.
3. **A05: Security Misconfiguration**:
   - Location: `app.py` → `export_standings()`
   - Vulnerable code: Exposes raw DB schema structure and internal query logs in HTTP response headers.

## Chained Attack
- **Chain-01**: SQLi Player Dump (A03) → IDOR Contract Access (A01) → Score Manipulation (A01)
- Attacker runs SQLi to leak player IDs, retrieves contract details via IDOR, and modifies game scores.

## Decoys
- Parameterized SQLite query for standings team-name search.
- Commissioner role authorization validation check before team registration.
