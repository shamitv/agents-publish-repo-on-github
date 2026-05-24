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

For chained vulnerability scenarios, see [scenarios.md](scenarios.md).
- User registration and login
- Register new spots (Decoy: secure admin logs)
- Search available parking spots (vulnerable to SQLi)
- Parameterized spot profiles details (Decoy: secure parameters)
- Reserve parking spots (vulnerable to insecure cost verification)
- Cancel parking reservations (vulnerable to missing cancel logs)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-36-parking-mgmt/.vulns) for the complete list of vulnerability targets.

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