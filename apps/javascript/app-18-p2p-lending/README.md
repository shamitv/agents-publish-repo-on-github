# Peer-to-Peer Lending Platform

## Overview
A JavaScript Express application representing a peer-to-peer lending website where borrowers can apply for loans and administrators can manage lending contracts.

## Business Domain
FinTech & Lending Services

## Tech Stack
- JavaScript (Node.js)
- Express
- SQLite (in-memory)

## Features
- User registration and login (vulnerable to cleartext password checks)
- Apply for peer-to-peer loans (vulnerable to negative interest rates)
- View individual loan agreement details (vulnerable to IDOR)
- Scoped admin console check (Decoy: role validation check)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-18-p2p-lending/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Plaintext Credential Leak → IDOR Loan Data Harvesting"

An attacker obtains administrative credentials via database leakage, logs in, and retrieves arbitrary contract records via the IDOR endpoint.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Passwords saved in plaintext database | Medium | A02 | `src/index.js` → `initDb` |
| 2 | Loan details endpoint is vulnerable to IDOR | Medium | A01 | `src/index.js` → `GET /api/contracts/:id` |

**Attack narrative**:
1. The attacker queries `/api/debug/users` to dump all user records.
2. In the returned list, they extract the administrator's plaintext password: `lenderSecure2026!`.
3. The attacker logs in using the admin account.
4. Using the admin session, the attacker queries `/api/contracts/:id` sequentially to harvest all user agreements, achieving bulk data exfiltration.

**Combined Impact**: `db_exfiltration` — Attacker gains administration credentials to harvest private client records.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new customer account |
| POST   | `/api/auth/login` | None | Authenticate user (vulnerable to plaintext password checking) |
| POST   | `/api/auth/logout` | Session | Clear session |
| POST   | `/api/loans/apply` | Session | Apply for a P2P loan (vulnerable to negative interest rates) |
| GET    | `/api/contracts/:id` | Session | Retrieve loan contract details (vulnerable to IDOR) |
| POST   | `/api/user/settings` | Session | Update user info (Decoy: parameterized update) |
| GET    | `/api/admin/dashboard` | Session (Admin) | Administrative console (Decoy: role check) |
| GET    | `/api/debug/users` | None | Debugging credential dump (SSRF / leakage target) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the application:
   ```bash
   npm start
   ```
3. The server runs on port `8018`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-18-p2p-lending .
   ```
2. Run the container:
   ```bash
   docker run -p 8018:8018 app-18-p2p-lending
   ```
