# Subscription Box Service

## Overview
A TypeScript Express application representing a subscription box ordering portal where users can browse subscription packages, manage their subscription states, and update profile settings.

## Business Domain
E-commerce & Subscription Services

## Tech Stack
- TypeScript
- Express
- SQLite (in-memory)

## Features
- User registration and login (vulnerable to unsalted MD5 password checking)
- Search subscription box catalog (vulnerable to SQLi)
- Parameterized package details lookup (Decoy: secure parameters)
- Update profile details (Decoy: secure logs audit)
- Cancel/Update subscriptions (vulnerable to missing security logs)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/typescript/app-34-subscription-box/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Package Search SQLi → Unsalted MD5 Credential Cracking"

An attacker executes SQL injection in package search to dump the users table, cracks the administrator's unsalted MD5 password hash offline, and signs in to gain full account takeover.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL injection in package search leaks user details | High | A03 | `src/index.ts` → `GET /api/packages/search` |
| 2 | MD5 unsalted password storage leads to authentication bypass | Medium | A07 | `src/index.ts` → `POST /api/auth/login` |

**Attack narrative**:
1. The attacker visits `/api/packages/search?q=coffee' UNION SELECT 1,username,password_hash,role FROM users --`.
2. The server processes the malformed search query, executing the SQL union and returning the user names and unsalted MD5 password hashes.
3. The attacker copies the MD5 hash `a57e4e138a08d3744952bd0176cd1f91` belonging to `admin_agent`.
4. The attacker runs a brute-force or rainbow table lookup tool offline, discovering the password is `'adminpass2026'`.
5. The attacker logs in via the login API, taking over the administrator account.

**Combined Impact**: `account_takeover` — Attacker obtains full administrative access to control all customer subscriptions and orders.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new customer account |
| POST   | `/api/auth/login` | None | Authenticate user (vulnerable to unsalted MD5 hashing) |
| POST   | `/api/auth/logout` | Session | Terminate active user session |
| POST   | `/api/user/profile` | Session | Edit user profile (Decoy: audit logs printed) |
| GET    | `/api/packages/search` | None | Search subscription boxes (vulnerable to SQLi) |
| GET    | `/api/packages/:id` | None | Get specific package details (Decoy: parameterized SQL) |
| POST   | `/api/subscriptions/update` | Session | Modify subscription status (vulnerable to missing audit logs) |

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
4. The server runs on port `8034`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-34-subscription-box .
   ```
2. Run the container:
   ```bash
   docker run -p 8034:8034 app-34-subscription-box
   ```
