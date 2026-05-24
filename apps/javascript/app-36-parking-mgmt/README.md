# Parking Management System

## Overview
A JavaScript Express application representing a parking reservation dashboard where users can find available spaces, book reservations, and cancel tickets.

## Business Domain
Logistics & Parking Services

## Tech Stack
- JavaScript (Node.js)
- Express
- SQLite (in-memory)

## Features
- User registration and login
- Register new spots (Decoy: secure admin logs)
- Search available parking spots (vulnerable to SQLi)
- Parameterized spot profiles details (Decoy: secure parameters)
- Reserve parking spots (vulnerable to insecure cost verification)
- Cancel parking reservations (vulnerable to missing cancel logs)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-36-parking-mgmt/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "SQL Injection Data Mining → Zero-Fee Booking Exploitation"

An attacker uses SQL Injection on the search endpoint to extract the parking spots database schema, books premium spaces specifying a price rate of zero, and cancels orders without producing audit logs.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL injection on spot search | High | A03 | `src/index.js` → `GET /api/spots/search` |
| 2 | Cost rates trusted directly from client parameters | Medium | A04 | `src/index.js` → `POST /api/bookings/book` |

**Attack narrative**:
1. The attacker searches spots via `/api/spots/search?q=Standard' UNION SELECT 1,id,spot_number,price_rate FROM spots --`.
2. The server processes the query and returns the list of premium spot IDs.
3. The attacker requests a booking to `/api/bookings/book` submitting a payload with `total_cost: 0.0`.
4. The server records the transaction as successful, granting free access.
5. The attacker cancels past reservations at `/api/bookings/1/cancel` without leaving an audit log trail.

**Combined Impact**: `data_modification` — Attacker bypasses payment gates to book reservation assets.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new customer account |
| POST   | `/api/auth/login` | None | Authenticate customer |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/spots/search` | None | Search parking spots (vulnerable to SQLi) |
| GET    | `/api/spots/:id` | None | Get specific spot details (Decoy: parameterized SQL) |
| POST   | `/api/admin/spots` | Session (Admin) | Register new parking spots (Decoy: secure logs) |
| POST   | `/api/bookings/book` | Session | Book a parking spot (vulnerable to Insecure Design cost bypass) |
| POST   | `/api/bookings/:id/cancel` | Session | Cancel parking reservation (vulnerable to missing logs) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the application:
   ```bash
   npm start
   ```
3. The server runs on port `8036`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-36-parking-mgmt .
   ```
2. Run the container:
   ```bash
   docker run -p 8036:8036 app-36-parking-mgmt
   ```
