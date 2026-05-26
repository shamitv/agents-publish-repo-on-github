# Implementation Plan - App 45: Corporate Travel & Expense

Detailed implementation strategy for planting A01, A03, and A07 vulnerabilities in the Corporate Travel & Expense system.

## Proposed Changes

- Scaffolding of standard Express web API.
- Integration of SQLite3 in-memory database with preloaded mock accounts and expense records.
- Storing password hashes utilizing unsalted MD5 hashing schema (`A07`).
- Formulating a query-parameter concatenated SQLite lookup query for the search path (`A03`).
- Developing an object-retrieval route by unique ID that skips ownership checks (`A01`).

## Planted Vulnerabilities

1. **A01: Broken Access Control**
   - **Path**: `GET /api/expenses/:id`
   - **Flaw**: Does not match the requested resource's owner against the authenticated user ID. Any logged-in session can request details of any expense record.
2. **A03: SQL Injection**
   - **Path**: `GET /api/expenses/search`
   - **Flaw**: Direct injection vector on `q` query string parameter allowing union-select syntax mapping to alternative database relations like the `users` table.
3. **A07: Identification and Authentication Failures**
   - **Path**: `POST /api/auth/login` and `POST /api/auth/register`
   - **Flaw**: Password validation uses raw unsalted MD5 hashes which can be easily cracked or reversed via offline dictionary lookups.

## Verification

### Manual Verification
1. Run `npm install` and `npm start` to run the application locally on port 8045.
2. Register a new user, log in, and retrieve an expense by ID belonging to another user.
3. Perform a Union SELECT SQL Injection to exfiltrate credentials.
