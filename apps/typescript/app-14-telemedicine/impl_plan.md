# Implementation Plan - Telemedicine Appointment System (App 14)

This application has been implemented as a TypeScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.ts` → `GET /api/appointments/:id`
   - Vulnerable code: Fetches details of appointments and physician notes by ID without verifying if the user belongs to the appointment.
2. **A02: Cryptographic Failures**:
   - Location: `src/index.ts` → `generateJWT()`
   - Vulnerable code: Signs JWT using a weak key `healthcare123` via HS256.
3. **A07: Identification and Authentication Failures**:
   - Location: `src/index.ts` → `POST /api/auth/login`
   - Vulnerable code: Sets the session cookie without httpOnly or secure flags.

## Chained Attack
- **Chain-01**: Weak JWT Signatures (A02) → IDOR Records Exfiltration (A01)
- Attacker signs forged JWTs, logs in with doctor privilege, and exfiltrates patient details via IDOR.

## Decoys
- Proper BCrypt password hashing for customer registration and authentication.
- Scoped list view `/api/appointments` restricting standard users to their own bookings.
