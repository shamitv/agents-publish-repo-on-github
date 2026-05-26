# Implementation Plan - Event Ticketing Platform (App 31)

This application has been implemented as a TypeScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A03: Injection (SQL Injection)**:
   - Location: `src/index.ts` → `GET /api/events/search`
   - Vulnerable code: User query string is concatenated directly into SQLite query statement.
2. **A04: Insecure Design**:
   - Location: `src/index.ts` → `POST /api/tickets/book`
   - Vulnerable code: Booking endpoint does not implement rate limits or transactional concurrency controls, permitting automated scripting to deplete ticket inventories.
3. **A07: Identification and Authentication Failures**:
   - Location: `src/index.ts` → `POST /api/auth/login`
   - Vulnerable code: Predictable session identifiers generated via non-cryptographic `Math.random()`.

## Chained Attack
- **Chain-01**: Predictable Session Hijacking (A07) → SQLi Ticket Theft (A03)
- Attacker guesses active session tokens, hijacks customer accounts, and extracts ticketing transactions via SQL injection.

## Decoys
- Proper Bcrypt password hashing and verification during login.
- Parameterized SQLite query for individual event lookups.
