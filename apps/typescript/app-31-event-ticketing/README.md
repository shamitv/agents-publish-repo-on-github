# Event Ticketing Platform

## Overview
A TypeScript Express application representing an online event ticketing platform where users can browse events, search for shows, purchase tickets, and track reservations.

## Business Domain
Entertainment & Ticketing Services

## Tech Stack
- TypeScript
- Express
- SQLite (in-memory)

## Features
- User registration and login
- Search events by keywords (e.g. Rock, Tech)
- Retrieve specific event details (with parameterized query decoy)
- Book event tickets (with validation checking)
- View customer booking histories

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/typescript/app-31-event-ticketing/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Predictable Session Hijacking → SQLi Ticket Theft"

An attacker exploits weak PRNG session keys to take over target customer sessions, and uses SQL injection to extract private ticket details and steal booking assets.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Predictable session key generation via Math.random() | Medium | A07 | `src/index.ts` → `POST /api/auth/login` |
| 2 | SQL injection in event search leaks ticket details | High | A03 | `src/index.ts` → `GET /api/events/search` |

**Attack narrative**:
1. The attacker observes that session cookies generated at login are predictable numbers created via `Math.random()`.
2. The attacker uses PRNG state prediction techniques to guess the session ID of an active customer who recently logged in.
3. The attacker sets the hijacked session cookie in their browser.
4. Using the hijacked session, the attacker calls `/api/events/search?q=1' UNION SELECT ...` to execute SQL injection, dumping the database tables containing booking references (e.g., `REF-8871`) and customer transaction IDs.
5. The attacker cancels or redirects the ticket assets to their own account.

**Combined Impact**: `account_takeover` — Attacker hijacks victim customer accounts and steals digital ticketing assets.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/login` | None | Authenticate user and receive session ID cookie (vulnerable to weak PRNG generation) |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/events/search` | None | Search events (vulnerable to SQLi) |
| GET    | `/api/events/:id` | None | Get specific event details (Decoy: parameterized SQL) |
| POST   | `/api/tickets/book` | Session | Book tickets (vulnerable to missing rate limits/concurrency checks) |
| GET    | `/api/bookings` | Session | List authenticated user's bookings |

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
4. The server runs on port `8031`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-31-event-ticketing .
   ```
2. Run the container:
   ```bash
   docker run -p 8031:8031 app-31-event-ticketing
   ```
