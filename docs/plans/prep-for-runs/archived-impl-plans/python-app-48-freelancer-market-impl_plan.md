# Implementation Plan - Freelancer Marketplace (App 48)

This application has been implemented as a FastAPI-based microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `app.py` → `get_proposal()`
   - Vulnerable code: Exposes freelancer bids to any user by ID without checking job ownership.
2. **A04: Insecure Design**:
   - Location: `app.py` → `release_payment()`
   - Vulnerable code: Release payment endpoint contains no escrow checks, nor does it check authorization of the client.
3. **A07: Identification and Authentication Failures**:
   - Location: `app.py` → `login()`
   - Vulnerable code: Predictable session tokens generated via `random.randint()`.

## Chained Attack
- **Chain-01**: Weak Token (A07) → IDOR Bid Espionage (A01)
- Attacker predicts session tokens, hijacks client sessions, and accesses competitor proposals via IDOR.

## Decoys
- Proper role-based authorization check on admin user listing endpoints.
- Bid range checking using Pydantic field validators.
