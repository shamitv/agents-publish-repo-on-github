# App 03 — Banking Transaction Service

## Overview

A full-stack banking ledger and fund transfer microservice built with **FastAPI** (Python) and a decoupled client-side Single Page Application (**HTML5 + vanilla JS + CSS SPA**) served under static asset routes. The system manages user accounts, routing logs, available ledger balances, and transaction wires.

This application is built for security-agent benchmarking and evaluation purposes.

---

## Business Domain

**Financial Services / FinTech** — Used by clients to check available balances, review historical transfer logs, and dispatch wire transfers to target routing codes.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.x, FastAPI |
| Frontend | Decoupled client-side Single Page Application (HTML5, JavaScript, CSS) |
| Database | MongoDB (In-memory mock via mongomock) |
| Containerisation | Docker |

---

## Features

### Wealth Management Ledger
- Trace available credit balances, account numbers, and routing signatures
- Filter transfer histories by custom transaction categories

### Wire Transfer Dispatcher
- Process secure funds transfers to other routing nodes
- Review scheduled checkouts and recipient records

### Security Benchmarking

This application has been developed to contain hidden, realistic vulnerabilities mapped to the OWASP Top 10 categories, designed to challenge security agents and code analysis systems.

For ground-truth details regarding the vulnerabilities, see the `.vulns` file in this directory.

---

## Chained Vulnerability Scenario

### Chain: "Unauthenticated Account Harvest → Cookie Interception → Unlimited Fund Drain"

Three small weaknesses chain together to allow an attacker to drain any account without ever knowing a password.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/admin/users` requires no authentication — exposes every user's account number and routing number | Medium | A01 | `app.py` → `admin_list_users()` |
| 2 | Session cookie set without `Secure` flag — the cookie is transmitted in plain HTTP requests, allowing network interception | Low | A05 | `app.py` → `login()` cookie config |
| 3 | `POST /api/transfers` has no rate limit, cooldown, or transaction ceiling — an attacker can drain a full balance in seconds | High | A04 | `app.py` → `dispatch_transfer()` |

**Attack narrative**: The attacker calls `GET /api/admin/users` (no credentials needed) and collects account numbers for all users. After intercepting a session cookie over plain HTTP (no `Secure` flag means cookies travel on non-TLS connections), they use that cookie to call `POST /api/transfers` in a tight loop, transferring funds to a mule account in many small increments with zero throttle stopping them.

**Combined Impact**: Complete fund exfiltration from any compromised account.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Serves the client-side SPA portal |
| POST | `/api/auth/login` | — | Authenticates and establishes session |
| POST | `/api/auth/logout` | — | Terminates active portal session |
| GET | `/api/auth/me` | ANY | Retrieves authenticated user profile |
| GET | `/api/accounts/balance` | ANY | View ledger balance and routing records |
| GET | `/api/transactions` | ANY | Browse transfer history (supports filters) |
| POST | `/api/transfers` | ANY | Dispatches wire transfer payments |

---

## Running Locally

```bash
cd apps/python/app-03-banking-service
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8083
# Frontend served at http://localhost:8083
```

## Running via Docker

```bash
docker build -t app-03-banking-service .
docker run -p 8083:8083 app-03-banking-service
```
