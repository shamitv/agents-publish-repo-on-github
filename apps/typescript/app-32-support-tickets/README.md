# Customer Support Ticket System

## Overview
A TypeScript Express application representing a customer support ticketing portal where customers can submit support requests, search through tickets, and view status.

## Business Domain
Customer Service & Ticket Management

## Tech Stack
- TypeScript
- Express
- SQLite (in-memory)

## Features
- User registration and login
- Ticket creation (Decoy: parameterized SQL)
- Search tickets by keyword (vulnerable to SQLi)
- Retrieve specific ticket details (vulnerable to IDOR)
- Diagnostic health check endpoint (vulnerable to environment info leak)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/typescript/app-32-support-tickets/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Verbose Diagnostics Exposure → Administrative Ticket Export Bypass"

An attacker queries the diagnostics health endpoint to leak the administrative recovery token, then uses it to bypass authentication and bulk export all support tickets.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | System diagnostics endpoint leaks recovery keys | Medium | A05 | `src/index.ts` → `GET /api/system/health` |
| 2 | Backup export endpoint permits authentication bypass via recovery token | Medium | A01 | `src/index.ts` → `POST /api/admin/export` |

**Attack narrative**:
1. The attacker accesses `/api/system/health?diagnostics=true` and notices that it displays sensitive diagnostic information.
2. In the returned diagnostic config payload, the attacker discovers a hardcoded administrative recovery token (`SUPPORT-ADMIN-DEV-RECOVERY-KEY-2026`).
3. The attacker calls `/api/admin/export` passing the header `x-admin-token: SUPPORT-ADMIN-DEV-RECOVERY-KEY-2026`.
4. The server validates the token and returns a complete list of users and support tickets, achieving database exfiltration.

**Combined Impact**: `db_exfiltration` — Attacker gains administrative access to bulk download user records and private ticket history.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new customer account |
| POST   | `/api/auth/login` | None | Authenticate user and receive session cookie |
| POST   | `/api/auth/logout` | Session | Terminate active user session |
| GET    | `/api/users/profile` | Session | Get profile details (Decoy: secure ID check) |
| POST   | `/api/tickets` | Session | Create a ticket (Decoy: parameterized query) |
| GET    | `/api/tickets/search` | Session | Search tickets (vulnerable to SQLi) |
| GET    | `/api/tickets/:id` | Session | Retrieve a specific ticket by ID (vulnerable to IDOR and detailed stack trace disclosure) |
| GET    | `/api/system/health` | None | Service status check (vulnerable to diagnostics info exposure) |
| POST   | `/api/admin/export` | Recovery Token | Export all database records (vulnerable to authorization bypass) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Build the TypeScript files:
   ```bash
   npm run build
   ```
3. Start the application:
   ```bash
   npm start
   ```
4. The server runs on port `8032`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-32-support-tickets .
   ```
2. Run the container:
   ```bash
   docker run -p 8032:8032 app-32-support-tickets
   ```
