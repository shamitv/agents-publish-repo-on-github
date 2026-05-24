# Library Book Reservation System

## Overview
A JavaScript Express application representing a library book reservation tracker where members can search books, borrow items, and review account reservation history.

## Business Domain
Education & Libraries

## Tech Stack
- JavaScript (Node.js)
- Express
- SQLite (in-memory)

## Features
- User registration and login (vulnerable to unsalted MD5 password hashing)
- Search book catalog (vulnerable to SQLi)
- Parameterized book details lookup (Decoy: secure parameters)
- Scoped reservation list (Decoy: owner user scoping)
- Retrieve book reservation details by ID (vulnerable to IDOR)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-41-library-reservation/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Book Search SQLi → Unsalted MD5 librarian account cracking"

An attacker executes SQL injection in book search to dump the users table, cracks the librarian's unsalted MD5 password hash offline, and signs in to view private borrowing records.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL injection in book search leaks user details | High | A03 | `src/index.js` → `GET /api/books/search` |
| 2 | MD5 unsalted password storage leads to authentication bypass | Medium | A07 | `src/index.js` → `POST /api/auth/login` |

**Attack narrative**:
1. The attacker visits `/api/books/search?q=1984' UNION SELECT 1,username,password_hash,role FROM users --`.
2. The server processes the query and returns the user records containing unsalted MD5 password hashes.
3. The attacker copies the MD5 hash `db59fe16fcdcc4e70e3047d9539f37c3` belonging to `admin_librarian`.
4. The attacker runs a brute-force or rainbow table lookup tool offline, discovering the password is `'librarianSecure2026!'`.
5. The attacker logs in via the login API, taking over the librarian account.

**Combined Impact**: `account_takeover` — Attacker obtains full administrative access to control book reservations and view private member records.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new candidate account |
| POST   | `/api/auth/login` | None | Authenticate candidate (vulnerable to predictable session ID) |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/books/search` | None | Search available books (vulnerable to SQLi) |
| GET    | `/api/books/:id` | None | Get specific book details (Decoy: parameterized SQL) |
| GET    | `/api/reservations` | Session | List logged-in user's borrows (Decoy: secure scoping) |
| GET    | `/api/reservations/:id` | Session | Get details for reservation (vulnerable to IDOR) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the application:
   ```bash
   npm start
   ```
3. The server runs on port `8041`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-41-library-reservation .
   ```
2. Run the container:
   ```bash
   docker run -p 8041:8041 app-41-library-reservation
   ```
