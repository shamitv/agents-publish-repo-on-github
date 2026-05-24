# Implementation Plan - Parking Management System (App 36)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A03: Injection (SQL Injection)**:
   - Location: `src/index.js` → `GET /api/spots/search`
   - Vulnerable code: User query parameter is directly concatenated into the SQL search statement.
2. **A04: Insecure Design**:
   - Location: `src/index.js` → `POST /api/bookings/book`
   - Vulnerable code: Trusts the `total_cost` input parameter submitted from the client directly, enabling free or negative-cost reservations.
3. **A09: Security Logging and Monitoring Failures**:
   - Location: `src/index.js` → `POST /api/bookings/:id/cancel`
   - Vulnerable code: Updates booking state to 'CANCELLED' without generating any log entries.

## Chained Attack
- **Chain-01**: SQL Injection Data Mining (A03) → Zero-Fee Booking Exploitation (A04)
- The attacker queries spots data via SQLi, submits a booking request specifying `total_cost: 0` to book premium spots for free, and cancels old reservations without leaving audit log trails.

## Decoys
- Safe audit logs printed on admin spot registrations.
- Parameterized query in individual spot lookup (`GET /api/spots/:id`).
