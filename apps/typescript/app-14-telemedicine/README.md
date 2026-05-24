# Telemedicine Appointment System

## Overview
A TypeScript Express application representing a telemedicine portal where patients can register, book appointments, and doctors can view histories and add consultation notes.

## Business Domain
Healthcare & Telemedicine Services

## Tech Stack
- TypeScript
- Express
- SQLite (in-memory)
- JSONWebToken

## Features
- User registration and login
- Book appointments (patients)
- View appointment listings (patients see only theirs, doctors see all assigned to them)
- View individual appointment details (including private physician notes)
- Patient password storage using proper BCrypt hashing

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/typescript/app-14-telemedicine/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Weak JWT Signatures → IDOR Records Exfiltration"

An attacker compromises a weak JWT signature key to forge administrative or doctor sessions, and then exfiltrates patient consultation records via IDOR.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | JWT signature signed with a weak secret key | High | A02 | `src/index.ts` → `generateJWT()` |
| 2 | IDOR on appointments retrieves private patient records | High | A01 | `src/index.ts` → `GET /api/appointments/:id` |

**Attack narrative**:
1. The attacker discovers that the application uses a weak JWT secret `healthcare123` to sign its tokens.
2. The attacker uses offline tools to sign a forged JWT with claims `{"userId": 3, "username": "dr_house", "role": "DOCTOR"}`.
3. The attacker sets this forged token in the session cookie.
4. Using doctor authority, the attacker enumerates the appointment endpoint `/api/appointments/<id>`. Because the endpoint suffers from IDOR, they fetch all consultation notes and details of every patient.

**Combined Impact**: `db_exfiltration` — Attacker steals confidential patient records and physician notes.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register a patient (Decoy: uses BCrypt) |
| POST   | `/api/auth/login` | None | Authenticate user and receive token cookie (vulnerable to weak signature & missing httpOnly flag) |
| POST   | `/api/auth/logout` | Session | Clear authentication cookie |
| GET    | `/api/auth/me` | Session | Retrieve current authenticated user details |
| GET    | `/api/appointments` | Session | List appointments (Decoy: correctly scoped) |
| GET    | `/api/appointments/:id` | Session | Retrieve detailed appointment info (vulnerable to IDOR) |

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
4. The server runs on port `8014`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-14-telemedicine .
   ```
2. Run the container:
   ```bash
   docker run -p 8014:8014 app-14-telemedicine
   ```
