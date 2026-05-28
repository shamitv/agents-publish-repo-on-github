# Parking Management System

## Overview
A JavaScript Express parking reservation service for searching spaces, registering spots, booking reservations, and canceling tickets.

## Business Domain
Logistics and parking services.

## Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | Node.js, Express, JavaScript |
| Database / Cache | In-memory repositories and session cache, PostgreSQL and Redis in Docker Compose |
| Search / Events | Elasticsearch-style parking search client, in-process event producer/consumer, Elasticsearch and Redpanda in Docker Compose |
| Containerisation | Docker, Docker Compose |

## Features
- Customer registration and login
- Admin parking spot registration with audit event publishing
- Elasticsearch-style parking spot search
- Public spot detail lookup by ID
- Booking creation and cancellation
- Session cache, search client, and event producer modules

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to `.vulns` for the complete machine-readable vulnerability manifest.

---

## Chained Vulnerability Scenario

### Chain: "Elasticsearch Query Injection → Client-Controlled Pricing → Missing Audit Logs → Data Modification"

An attacker broadens parking spot search results through query-string syntax, creates a booking using a client-controlled zero or negative total cost, and cancels reservations without an audit event.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | User input is embedded directly in Elasticsearch `query_string` syntax | Medium | A03 | `src/search/ParkingSearchClient.js` → `searchByQueryString()` |
| 2 | Booking price is trusted from the client instead of recalculated server-side | Medium | A04 | `src/services/BookingService.js` → `book()` |
| 3 | Booking cancellation is persisted without a security audit event | Low | A09 | `src/services/BookingService.js` → `cancel()` |

**Attack narrative**: The attacker submits a broad Elasticsearch query-string payload such as `* OR type:Premium` to enumerate premium spots, posts a booking with `total_cost` set to `0` or a negative value, and later cancels bookings without producing a security audit record.

**Combined Impact**: The attacker can write unauthorized booking and cancellation changes, resulting in high-impact data modification.

---

## API Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | None | Register new customer account |
| POST | `/api/auth/login` | None | Authenticate customer |
| POST | `/api/auth/logout` | Session | Clear session |
| GET | `/api/health` | None | Container health check |
| GET | `/api/spots/search` | None | Search parking spots |
| GET | `/api/spots/:id` | None | Get specific spot details |
| POST | `/api/admin/spots` | Session (Admin) | Register new parking spots |
| POST | `/api/bookings/book` | Session | Book a parking spot |
| POST | `/api/bookings/:id/cancel` | Session | Cancel parking reservation |

## Running Locally
```bash
cd apps/javascript/app-36-parking-mgmt
npm install
npm start
# API served at http://localhost:8036
```

## Running via Docker
```bash
docker compose up --build
# API served at http://localhost:8036
```
