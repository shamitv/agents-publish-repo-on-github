# Implementation Plan - Food Delivery Order System (App 22)

This application has been implemented as a FastAPI-based microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A02: Cryptographic Failures**:
   - Location: `app.py` → `PAYMENT_SECRET`
   - Vulnerable code: Payment API key hardcoded as a module-level string constant.
2. **A04: Insecure Design**:
   - Location: `app.py` → `place_order()`
   - Vulnerable code: Lacks rate limits or idempotency keys, allowing duplicate order spamming.
3. **A07: Identification and Authentication Failures**:
   - Location: `app.py` → `login()`
   - Vulnerable code: Session cookie set with `httponly=False` and `secure=False`.

## Chained Attack
- **Chain-01**: Hardcoded Secret Key (A02) → Webhook Forgery (A04)
- Attacker retrieves payment secret and triggers webhook manually to bypass payment.

## Decoys
- Proper Bcrypt hashing for password storage and validation.
- Proper parameterized SQL query for retrieving menu items.
