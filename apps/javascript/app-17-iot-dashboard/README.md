# IoT Device Dashboard

## Overview
A JavaScript Express IoT dashboard for user login, device command execution, device status refresh, and internal telemetry diagnostics.

## Business Domain
Smart home and IoT device fleet management.

## Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | Node.js, Express, JavaScript |
| Database / Cache | In-memory repositories and session cache, PostgreSQL and Redis in Docker Compose |
| Search / Events | Device search client, in-process event producer/consumer, Elasticsearch and Redpanda in Docker Compose |
| HTTP Client | Axios |
| Containerisation | Docker, Docker Compose |

## Features
- User registration and login
- Execute commands against IoT devices
- View public device profiles by ID
- Refresh device status from custom URLs
- Internal telemetry endpoint for device diagnostics
- Device search indexing hook and event publisher

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to `.vulns` for the complete machine-readable vulnerability manifest.

---

## Chained Vulnerability Scenario

### Chain: "Debug Config Leak → HTTP SSRF → Plaintext Device Token Exposure → Lateral Movement"

An authenticated user triggers a command error that leaks an internal telemetry URL and token, then uses the device refresh SSRF to reach that internal telemetry endpoint and retrieve plaintext device tokens.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Verbose command errors return internal telemetry URL and access token | Medium | A05 | `src/services/DeviceService.js` → `commandError()` |
| 2 | Device refresh fetches caller-controlled URLs server-side | Medium | A10 | `src/services/RefreshService.js` → `refreshStatus()` |
| 3 | Internal telemetry returns plaintext device tokens | Medium | A02 | `src/services/TelemetryService.js` → `internalTelemetry()` |

**Attack narrative**: The attacker submits a command containing `TRIGGER-ERROR`, extracts `telemetry_server_url` and `telemetry_access_key` from the verbose response, then submits that internal telemetry URL to `/api/devices/refresh`. The server performs the internal HTTP request and returns device secrets from telemetry.

**Combined Impact**: The attacker pivots from the public dashboard into internal telemetry and obtains device tokens, enabling lateral movement.

---

## API Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | None | Register new account |
| POST | `/api/auth/login` | None | Authenticate session |
| POST | `/api/auth/logout` | Session | Clear session |
| GET | `/api/health` | None | Container health check |
| POST | `/api/devices/command` | Session | Run commands |
| POST | `/api/devices/refresh` | Session | Query custom status URLs |
| GET | `/api/devices/:id` | Session | View public device profile |
| GET | `/api/internal/telemetry` | Token | Internal telemetry endpoint |

## Running Locally
```bash
cd apps/javascript/app-17-iot-dashboard
npm install
npm start
# API served at http://localhost:8017
```

## Running via Docker
```bash
docker compose up --build
# API served at http://localhost:8017
```
