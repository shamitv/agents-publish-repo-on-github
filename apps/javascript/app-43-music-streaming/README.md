# Music Streaming Playlist Service

## Overview
A JavaScript Express application representing a music streaming database where listeners can create playlists, add tracks, and import custom cover art images.

## Business Domain
Entertainment & Media Streaming

## Tech Stack
- JavaScript (Node.js)
- Express
- SQLite (in-memory)
- Axios

## Features
- User registration and login
- Track playlist configurations (Decoy: secure user scoping)
- Add tracks to playlists (Decoy: parameterized SQL)
- Fetch playlist details (vulnerable to IDOR in private lists)
- Import cover art images (vulnerable to SSRF via custom art URLs)
- Diagnostics configuration console (vulnerable to integration secrets leak)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-43-music-streaming/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Diagnostics Configuration Exposure → SSRF Playlist Analytics Pivoting"

An attacker queries the diagnostics API to leak the metrics integration token, then makes an SSRF call targeting the internal playlist analytics node to download the database.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Diagnostics status leaks metrics secret token key | Medium | A05 | `src/index.js` → `GET /api/system/status` |
| 2 | Cover art proxy is vulnerable to SSRF | High | A10 | `src/index.js` → `GET /api/cover` |

**Attack narrative**:
1. The attacker queries `/api/system/status?debug=true` to obtain the API key: `INTERNAL-METRICS-API-SECRET-2026`.
2. The attacker calls `/api/cover?url=http://localhost:8043/api/internal/analytics?token=INTERNAL-METRICS-API-SECRET-2026`.
3. The server makes the HTTP request, bypassing internal database controls using the leaked token, and returns all playlist database entries, achieving lateral movement.

**Combined Impact**: `lateral_movement` — Attacker bypasses firewall filters to retrieve internal playlist logs.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new customer account |
| POST   | `/api/auth/login` | None | Authenticate customer |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/playlists` | Session | List logged-in user's playlists (Decoy: user scoped) |
| GET    | `/api/playlists/:id` | Session | Get specific playlist details (vulnerable to IDOR) |
| POST   | `/api/tracks` | Session | Add track to playlist (Decoy: parameterized SQL) |
| GET    | `/api/cover` | Session | Proxy cover art URLs (vulnerable to SSRF) |
| GET    | `/api/system/status` | None | Verify configuration status (vulnerable to key leak) |
| GET    | `/api/internal/analytics` | Token | Internal playlist database analytics (SSRF Target) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the application:
   ```bash
   npm start
   ```
3. The server runs on port `8043`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-43-music-streaming .
   ```
2. Run the container:
   ```bash
   docker run -p 8043:8043 app-43-music-streaming
   ```
