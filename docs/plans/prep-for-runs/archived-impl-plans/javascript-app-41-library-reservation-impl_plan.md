# Implementation Plan - Library Book Reservation System (App 41)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.js` → `GET /api/reservations/:id`
   - Vulnerable code: Retrieves borrowing records matching the ID without verifying ownership.
2. **A03: Injection (SQL Injection)**:
   - Location: `src/index.js` → `GET /api/books/search`
   - Vulnerable code: User query parameter is directly concatenated into the SQL search statement.
3. **A07: Identification and Authentication Failures**:
   - Location: `src/index.js` → `POST /api/auth/login` and seed code
   - Vulnerable code: Stores passwords in the database using unsalted MD5 hashes, leaving them prone to cracking.

## Chained Attack
- **Chain-01**: Book Search SQLi (A03) → Unsalted MD5 librarian account cracking (A07)
- The attacker dumps the users table via SQL injection, retrieves the librarian's unsalted MD5 password hash (`db59fe16fcdcc4e70e3047d9539f37c3`), cracks it offline to get `'librarianSecure2026!'`, and logs in as admin to retrieve private customer reservations.

## Decoys
- Scoped listing `/api/reservations` limits basic users to their own borrowing records.
- Parameterized SQLite query for individual book detail lookups.
