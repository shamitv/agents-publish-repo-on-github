# Election Polling System

## Overview
A JavaScript Express application representing a municipal election database where citizens can register, review candidate lists, and cast ballots.

## Business Domain
Government & E-Voting

## Tech Stack
- JavaScript (Node.js)
- Express
- SQLite (in-memory)

## Features
- User registration and login
- Add candidates (Decoy: secure admin logs)
- List candidates and cast ballots (vulnerable to plaintext vote leakage)
- Cast a ballot (vulnerable to race-based double-voting)
- Close election polling (vulnerable to missing close logs)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-44-election-polling/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Predictable Voter Ballot Retrieval → Concurrent Vote Casting"

An attacker mines plaintext ballot selections to find voters who have not cast votes, then exploits a race condition in casting votes to cast multiple ballots under those identities.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Voter ballot choices leaked in plaintext | Medium | A02 | `src/index.js` → `GET /api/candidates` |
| 2 | Casting votes timing delay allows race condition | Medium | A04 | `src/index.js` → `POST /api/vote/cast` |

**Attack narrative**:
1. The attacker queries `/api/candidates` and extracts all voter ballot rows.
2. The attacker identifies voter IDs that have not yet registered any ballot.
3. The attacker logs in under those users (or targets their API keys) and triggers concurrent `POST` requests to `/api/vote/cast`.
4. The timing window allows inserting multiple ballots before the user state is set to `has_voted = 1`, achieving double-voting.
5. The attacker cancels old logs without logs tracking at `/api/admin/polls/close`.

**Combined Impact**: `data_modification` — Attacker manipulates polling results and ballot counts.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new voter account |
| POST   | `/api/auth/login` | None | Authenticate voter |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/candidates` | None | List candidates and ballots (vulnerable to plaintext leak) |
| POST   | `/api/vote/cast` | Session | Cast a ballot (vulnerable to race conditions) |
| POST   | `/api/admin/candidates` | Session (Admin) | Register new candidate (Decoy: secure logs) |
| POST   | `/api/admin/polls/close` | Session (Admin) | Close the election (vulnerable to missing logs) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the application:
   ```bash
   npm start
   ```
3. The server runs on port `8044`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-44-election-polling .
   ```
2. Run the container:
   ```bash
   docker run -p 8044:8044 app-44-election-polling
   ```
