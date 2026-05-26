# IoT Device Dashboard

## Overview
A JavaScript Express application representing an IoT management dashboard where users can view connected device profiles, execute commands, and fetch live status updates.

## Business Domain
Smart Home & IoT Devices

## Tech Stack
- JavaScript (Node.js)
- Express
- SQLite (in-memory)
- Axios

## Features

For chained vulnerability scenarios, see [scenarios.md](scenarios.md).
- User registration and login
- Execute device commands (vulnerable to verbose configuration/token leak in errors)
- Fetch device profiles by ID (Decoy: parameterized SQL)
- Refresh device telemetry (vulnerable to SSRF via custom status URLs)
- Device secret configuration (vulnerable to plaintext storage in DB)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-17-iot-dashboard/.vulns) for the complete list of vulnerability targets.

---


## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new account |
| POST   | `/api/auth/login` | None | Authenticate session |
| POST   | `/api/auth/logout` | Session | Clear session |
| POST   | `/api/devices/command` | Session | Run commands (vulnerable to diagnostics info exposure) |
| POST   | `/api/devices/refresh` | Session | Query custom status URLs (vulnerable to SSRF) |
| GET    | `/api/devices/:id` | Session | View device profile (Decoy: parameterized SQL) |
| GET    | `/api/internal/telemetry` | Token | Internal diagnostic endpoint (SSRF Target) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the application:
   ```bash
   npm start
   ```
3. The server runs on port `8017`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-17-iot-dashboard .
   ```
2. Run the container:
   ```bash
   docker run -p 8017:8017 app-17-iot-dashboard
   ```