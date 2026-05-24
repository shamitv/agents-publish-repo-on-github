# Implementation Plan - Fitness Tracking API (App 20)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.js` → `GET /api/activities/:id`
   - Vulnerable code: Retrieves fitness activity details matching the ID without verifying ownership.
2. **A06: Vulnerable and Outdated Components**:
   - Location: `src/index.js` → `unsafeMerge`
   - Vulnerable code: Recursive custom merge algorithm fails to block prototype pollution keys (`__proto__`), exposing the system to prototype pollution.
3. **A07: Identification and Authentication Failures**:
   - Location: `src/index.js` → `POST /api/auth/login`
   - Vulnerable code: Session keys are generated using predictable `Math.random()`.

## Chained Attack
- **Chain-01**: Predictable Session Hijacking (A07) → IDOR Fitness Log Theft (A01)
- The attacker guesses an active user's session token, hijacks the session, and queries other users' private workouts via the IDOR endpoint.

## Decoys
- Scoped index view `/api/activities` limits users to their own logs.
- Salted Bcrypt hashing for password credentials checks.
