# Digital Asset Management

## Overview
A TypeScript Express application representing a digital asset manager where users can upload files, tag them, share assets, and import files from external links.

## Business Domain
Media, Publishing & Cloud Storage

## Tech Stack
- TypeScript
- Express
- Multer
- SQLite (in-memory)

## Features
- User login & session management
- File upload (Multer-based storage)
- Browse and download assets
- Import files from remote URLs
- Update tags on assets (with validation decoy)
- Admin statistics dashboard (with secure token authorization decoy)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/typescript/app-15-digital-assets/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "SSRF File Fetch → Predictable Path RCE"

An attacker uses the asset import feature to perform an SSRF fetch from a target server, which saves the retrieved script file in a web-accessible public path, permitting Remote Code Execution (RCE).

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SSRF in asset import fetches arbitrary network URLs | Medium | A10 | `src/index.ts` → `POST /api/assets/import` |
| 2 | Unrestricted upload stores fetched script in public path | High | A08 | `src/index.ts` → `POST /api/assets/import` |

**Attack narrative**:
1. The attacker authenticates as a standard user.
2. The attacker triggers the import feature `/api/assets/import` with `url` and `filename` parameters. 
3. The server executes a `fetch` request to the target URL. Because the server does not check IP ranges, the attacker can specify internal network URLs.
4. The attacker provides a URL hosting a malicious JavaScript file (e.g. `http://attacker-internal/payload.js`) and sets the output filename to `payload.js`.
5. The server downloads the file and saves it in the public uploads directory `public/uploads/payload.js` without validating the `.js` extension.
6. The attacker invokes the script directly by calling `/uploads/payload.js` via HTTP, executing commands on the host server.

**Combined Impact**: `lateral_movement` — Attacker achieves Remote Code Execution (RCE) on the server environment.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/login` | None | Authenticate user and initialize session |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/assets/:id` | Session | Retrieve asset metadata and download path (vulnerable to IDOR) |
| POST   | `/api/assets/upload` | Session | Upload a file asset (vulnerable to unrestricted file uploads) |
| POST   | `/api/assets/import` | Session | Import file asset from URL (vulnerable to SSRF & file write RCE) |
| POST   | `/api/assets/:id/tags` | Session | Update asset tags (Decoy: regex alphanumeric validation check) |
| GET    | `/api/admin/stats` | Token | Get total asset statistics (Decoy: Bearer token validation) |

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
4. The server runs on port `8015`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-15-digital-assets .
   ```
2. Run the container:
   ```bash
   docker run -p 8015:8015 app-15-digital-assets
   ```
