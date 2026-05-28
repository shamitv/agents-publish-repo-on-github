# Telemedicine Appointment System

## Overview
A TypeScript Express telemedicine portal for patient registration, appointment listing, and physician notes review.

## Business Domain
Healthcare and telemedicine appointment management.

## Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | Node.js, Express, TypeScript |
| Database / Cache | In-memory medical repository and appointment cache, PostgreSQL and Redis in Docker Compose |
| Search / Events | Patient search client, in-process audit producer/consumer, Elasticsearch and Redpanda in Docker Compose |
| Authentication | JSON Web Tokens |
| Containerisation | Docker, Docker Compose |

## Features
- Patient registration and login
- Scoped appointment list for patients and doctors
- Appointment detail view with physician notes
- Patient search indexing hook
- Audit event producer/consumer for appointment reads
- BCrypt password storage

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to `.vulns` for the complete machine-readable vulnerability manifest.

---

## Chained Vulnerability Scenario

### Chain: "Weak JWT Validation → Patient Notes IDOR → DB Exfiltration"

An attacker forges or tampers with a JWT because the server decodes tokens without signature validation, then enumerates appointment records that expose private physician notes by ID.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | JWT payload is decoded without validating the signature | Medium | A07 | `src/services/TokenService.ts` → `verify()` |
| 2 | Appointment detail loads patient notes by ID without patient or doctor ownership checks | Medium | A01 | `src/services/AppointmentService.ts` → `getAppointmentDetail()` |

**Attack narrative**: The attacker creates a JWT containing a chosen `userId`, `username`, and `role`, places it in the `token` cookie, then requests `/api/appointments/1`, `/api/appointments/2`, and subsequent IDs. Because token signatures are not verified and appointment details are not scoped to the caller, the responses include confidential physician notes.

**Combined Impact**: The attacker can bulk-read confidential appointment records and doctor notes, resulting in high-impact database exfiltration.

---

## API Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | None | Register a patient |
| POST | `/api/auth/login` | None | Authenticate user and set token cookie |
| POST | `/api/auth/logout` | Session | Clear authentication cookie |
| GET | `/api/auth/me` | Session | Retrieve current authenticated user details |
| GET | `/api/health` | None | Container health check |
| GET | `/api/appointments` | Session | List scoped appointments |
| GET | `/api/appointments/:id` | Session | Retrieve detailed appointment info |

## Running Locally
```bash
cd apps/typescript/app-14-telemedicine
npm install
npm run build
npm start
# API served at http://localhost:8014
```

## Running via Docker
```bash
docker compose up --build
# API served at http://localhost:8014
```
