# Implementation Plan - Restaurant Review Platform (App 16)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.js` → `POST /api/reviews/:id/edit`
   - Vulnerable code: Edits reviews by ID without verifying if the authenticated user is the owner.
2. **A03: Injection (SQL Injection)**:
   - Location: `src/index.js` → `GET /api/restaurants/search`
   - Vulnerable code: Directly interpolates user query strings into SQL commands.
3. **A07: Identification and Authentication Failures**:
   - Location: `src/index.js` → `POST /api/auth/login`
   - Vulnerable code: Generates session cookies using the predictable `Math.random()`.

## Chained Attack
- **Chain-01**: Predictable Session Hijacking (A07) → IDOR Review Sabotage (A01)
- The attacker predicts an active user session token, hijacks the session cookie, and modifies their restaurant reviews to arbitrary ratings or text.

## Decoys
- Proper Bcrypt hashing for password storage and validation.
- Secure role checks for administrative dashboard.
- Parameterized database query logic when fetching individual restaurant profiles.
