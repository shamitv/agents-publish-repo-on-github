# Veterinary Clinic Management

## Overview
A FastAPI application representing a veterinary clinic management system, allowing pet owners to schedule appointments, and veterinarians/staff to manage pet health records and issue prescriptions.

## Business Domain
Healthcare & Veterinary Services

## Tech Stack
- Python 3.10
- FastAPI
- PyJWT
- SQLite (in-memory)

## Features
- User login / JWT token authentication
- Search pet records
- Manage pet health profiles (species, age, weight) with strict field validation
- View and update prescriptions (e.g. drug name, dosages)
- Schedule clinic appointments with audit logging
- View appointment lists

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/python/app-24-vet-clinic/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Weak JWT → SQL Injection → Prescription Tampering"

An attacker cracks a weak JWT signature to impersonate a veterinarian, uses SQL injection to identify pet IDs, and modifies drug prescriptions without logging or detection.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Weak JWT signature key allows offline forgery | Medium | A02 | `app.py` → `generate_token()` |
| 2 | SQL injection in pet search exposes database details | Medium | A03 | `app.py` → `search_pets()` |
| 3 | Prescription updates write no audit logs | Low | A09 | `app.py` → `update_prescription()` |

**Attack narrative**:
1. The attacker notes that the JWT tokens are signed using a weak secret key `secret123`.
2. The attacker crafts a custom JWT offline containing the claim `"role": "VET"`, giving them veterinarian-level access privileges.
3. Using the forged JWT, the attacker calls the search endpoint `/api/pets/search?q=1' OR '1'='1` to trigger SQL injection, obtaining all pet IDs and owner records from the database.
4. Armed with a target pet ID, the attacker sends a post request to `/api/prescriptions/<prescription_id>/update` to change a prescription (e.g., increasing a controlled substance dosage or introducing a dangerous drug interaction).
5. The application accepts the change but produces no logs, leaving clinic administration unaware of the unauthorized medication change.

**Combined Impact**: `data_modification` — Unauthorized dosage and drug alterations on patient prescriptions go entirely undetected.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/login` | None | Exchange credentials for a JWT token |
| GET    | `/api/pets/search` | JWT (Vet/Admin) | Search pet records (vulnerable to SQLi) |
| POST   | `/api/pets` | JWT (Vet/Admin) | Add a new pet record (Decoy: input validation) |
| POST   | `/api/prescriptions/<prescription_id>/update` | JWT (Vet/Admin) | Update dosage/drug details (vulnerable to logging failure) |
| POST   | `/api/appointments` | JWT | Schedule a new clinic appointment (Decoy: audit logged) |
| GET    | `/api/appointments` | JWT | List appointments |
| GET    | `/api/audit/logs` | JWT (Admin) | Retrieve system audit logs |

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. The application runs on port `8094`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-24-vet-clinic .
   ```
2. Run the container:
   ```bash
   docker run -p 8094:8094 app-24-vet-clinic
   ```
