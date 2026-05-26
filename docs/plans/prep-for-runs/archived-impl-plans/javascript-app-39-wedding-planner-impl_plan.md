# Implementation Plan - Wedding Planning Platform (App 39)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.js` → `GET /api/events/:id/guests`
   - Vulnerable code: Retrieves attendee guest lists by event ID without verifying if the caller owns the wedding event.
2. **A02: Cryptographic Failures**:
   - Location: `src/index.js` → `POST /api/auth/login` and seed code
   - Vulnerable code: Stores passwords in the database using unsalted MD5 hashes, leaving them prone to cracking.
3. **A07: Identification and Authentication Failures**:
   - Location: `src/index.js` → `POST /api/auth/login`
   - Vulnerable code: Session cookies are generated via predictable `Math.random()` outputs.

## Chained Attack
- **Chain-01**: Predictable Session Hijacking (A07) → IDOR Guest List Harvesting (A01)
- The attacker guesses active coordinator session tokens, sets the cookie, and extracts user guest list records (names/emails) via the IDOR endpoint.

## Decoys
- Scoped listing `/api/events` limits basic users to their own planners.
- Parameterized SQLite query for individual event detail lookups.
