# Compliance Document Tracker

## Overview
A TypeScript Express application representing a compliance document tracking portal where customers can submit documents, review audit files, and search diagnostic statistics.

## Business Domain
Regulatory Compliance & Risk Management

## Tech Stack
- TypeScript
- Express
- SQLite (in-memory)

## Features
- User registration and login
- Retrieve own profile details (Decoy: strict session checks)
- Upload documents (vulnerable to insecure deserialization in custom metadata)
- Safe upload document handler (Decoy: JSON.parse)
- Retrieve specific document details (vulnerable to IDOR)
- Admin debug health portal (vulnerable to credential disclosures in dev mode)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/typescript/app-35-compliance-tracker/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Dev Mode Config Leak → Admin Document Retrieval Bypass"

An attacker triggers the developer diagnostics endpoint to retrieve the administrative access key, then uses it to bypass authentication and retrieve arbitrary compliance documents.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug endpoint leaks administration recovery key | Medium | A05 | `src/index.ts` → `GET /api/admin/debug` |
| 2 | Document details endpoint allows IDOR retrieval via administration header | Medium | A01 | `src/index.ts` → `GET /api/documents/:id` |

**Attack narrative**:
1. The attacker visits `/api/admin/debug?dev=true` and retrieves the developer debug configuration.
2. In the returned payload, the attacker discovers a hardcoded administrative recovery key: `ADMIN-DEV-TOKEN-KEY-8871`.
3. The attacker requests a private document at `/api/documents/1` passing the header `x-admin-token: ADMIN-DEV-TOKEN-KEY-8871`.
4. The server validates the token, logs the caller in as administrative auditor, and returns the private tax compliance documents, achieving data bypass.

**Combined Impact**: `account_takeover` — Attacker gains administration access to bypass security boundaries and extract sensitive client files.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new customer account |
| POST   | `/api/auth/login` | None | Authenticate user and receive session cookie |
| POST   | `/api/auth/logout` | Session | Terminate active user session |
| GET    | `/api/users/me` | Session | Get active user profile (Decoy: secure session check) |
| POST   | `/api/documents` | Session/Dev Token | Upload document and evaluate metadata (vulnerable to insecure deserialization) |
| POST   | `/api/documents/safe` | Session/Dev Token | Upload document and parse metadata safely (Decoy: JSON.parse) |
| GET    | `/api/documents/:id` | Session/Dev Token | View compliance document details (vulnerable to IDOR) |
| GET    | `/api/admin/debug` | None | Dev debug diagnostics (vulnerable to information leak) |

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
4. The server runs on port `8035`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-35-compliance-tracker .
   ```
2. Run the container:
   ```bash
   docker run -p 8035:8035 app-35-compliance-tracker
   ```
