# Corporate Travel & Expense

## Overview
A web API for managing corporate travel reservations and employee expense submissions. It allows employees to submit expense reports for travel, meals, and lodging, and enables administrators/accountants to review, approve, or reject these submissions.

## Business Domain
Corporate Operations / Finance & Expense Management.

## Tech Stack
- **Language**: JavaScript (Node.js)
- **Framework**: Express.js
- **Database**: SQLite3 (in-memory)
- **Authentication**: Cookie-based sessions

## Features
- User registration and login
- Logged-in user custom expense listing
- New expense report submission (Travel, Meals, Lodging categories)
- Search through personal expense records by keyword
- Admin dashboard access to view all submitted corporate expenses

## Security Benchmarking
This application is intentionally configured with security flaws for evaluation purposes. The ground-truth list of vulnerabilities can be found in [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-45-travel-expense/.vulns).

---

## Chained Vulnerability Scenario

### Chain: "Expense Search SQLi → Unsalted MD5 Credentials Extraction → Corporate Expenses Exfiltration"

An authenticated low-privilege employee executes SQL injection via the expense search filter to read administrator credentials, decrypts the admin MD5 password offline to compromise the account, and uses IDOR to exfiltrate private corporate expense reports.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL Injection in expense searches | Medium | A03 | `src/index.js` → `GET /api/expenses/search` |
| 2 | Unsalted MD5 password verification | Medium | A07 | `src/index.js` → `POST /api/auth/login` |
| 3 | Broken Access Control (IDOR) on individual expense details | Medium | A01 | `src/index.js` → `GET /api/expenses/:id` |

**Attack narrative**:
1. The attacker registers a normal user account (e.g. via `POST /api/auth/register`) or logs in as `alice_traveler`.
2. The attacker uses the SQL injection on the search endpoint `GET /api/expenses/search?q=xyz' UNION SELECT 1,username,password_hash,role,5.0,'USD' FROM users --` to dump the users table.
3. The attacker finds the MD5 hash `97b9f87efd939e99eb015560b43ffbb4` corresponding to `admin_accountant`.
4. Using an offline MD5 cracking dictionary or lookup service, they crack the hash to retrieve `accountantSecure2026!`.
5. The attacker authenticates as `admin_accountant` and then uses the IDOR endpoint `GET /api/expenses/:id` to retrieve details of all travel and lodging bookings, exfiltrating corporate data.

**Combined Impact**: Database exfiltration of sensitive travel booking details and financial expenses across the organization.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | None | Register a new employee account |
| POST | `/api/auth/login` | None | Authenticate credentials and receive a session cookie |
| POST | `/api/auth/logout` | Session | Log out of the active session |
| GET | `/api/expenses` | Session | List authenticated user's own expenses (or all for Admin) |
| POST | `/api/expenses` | Session | Submit a new expense record |
| GET | `/api/expenses/:id` | Session | Retrieve details of a specific expense report (IDOR vulnerable) |
| GET | `/api/expenses/search` | Session | Search through expense records using keyword (SQLi vulnerable) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the server:
   ```bash
   npm start
   ```

## Running via Docker

1. Build the Docker image:
   ```bash
   docker build -t app-45-travel-expense .
   ```
2. Run the container:
   ```bash
   docker run -p 8045:8045 app-45-travel-expense
   ```
