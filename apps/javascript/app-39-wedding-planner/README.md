# Wedding Planning Platform

## Overview
A JavaScript Express application representing a wedding planning database where clients can manage guest lists, RSVPs, and registry settings.

## Business Domain
Events & Wedding Planning

## Tech Stack
- JavaScript (Node.js)
- Express
- SQLite (in-memory)

## Features
- User registration and login (vulnerable to unsalted MD5 password hashing)
- Event planning trackers (Decoy: owner user scoping)
- Event details search (Decoy: parameterized SQL)
- Manage event guest RSVPs (vulnerable to IDOR)
- Session cookies (vulnerable to predictable session keys)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-39-wedding-planner/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Predictable Session Hijacking → IDOR Guest List Harvesting"

An attacker guesses active session identifiers, hijacks coordinator sessions, and downloads guest databases containing emails and names via the IDOR endpoint.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Predictable session key generation via Math.random() | Medium | A07 | `src/index.js` → `POST /api/auth/login` |
| 2 | Guest list is vulnerable to IDOR | Medium | A01 | `src/index.js` → `GET /api/events/:id/guests` |

**Attack narrative**:
1. The attacker observes that session cookies generated at login are numbers created via `Math.random()`.
2. The attacker guesses the active session ID of a wedding coordinator.
3. The attacker sets this hijacked cookie in their browser.
4. Using the hijacked session, the attacker makes a GET request to `/api/events/2/guests` to retrieve guest list records.
5. The guest lists are returned without checking if the hijacked user owns the event.

**Combined Impact**: `db_exfiltration` — Attacker hijacks victim accounts and harvests client guest databases.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new candidate account |
| POST   | `/api/auth/login` | None | Authenticate candidate (vulnerable to predictable session ID) |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/events` | Session | List logged-in user's events (Decoy: secure scoping) |
| GET    | `/api/events/:id` | Session | Get specific event details (Decoy: parameterized SQL) |
| GET    | `/api/events/:id/guests` | Session | Get guest list for event (vulnerable to IDOR) |
| POST   | `/api/events/:id/guests` | Session | Add guest to list |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the application:
   ```bash
   npm start
   ```
3. The server runs on port `8039`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-39-wedding-planner .
   ```
2. Run the container:
   ```bash
   docker run -p 8039:8039 app-39-wedding-planner
   ```
