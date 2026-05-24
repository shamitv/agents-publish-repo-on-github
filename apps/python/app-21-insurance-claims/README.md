# Insurance Claims Processor

## Overview
A web application for processing insurance policies and claims, allowing customers to file claims and adjusters/admins to review and approve payouts.

## Business Domain
Insurance & Financial Services

## Tech Stack
- Python 3.10
- Flask
- SQLite (in-memory)

## Features
- User login / session management (roles: CUSTOMER, ADJUSTER, ADMIN)
- View and search claims
- File new claims against active policies
- Adjuster dashboard to approve claims and trigger payouts
- Admin dashboard to view aggregate financial stats and list users

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/python/app-21-insurance-claims/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "SQL Injection → IDOR Claim Access → Silent Payout Fraud"

An attacker uses SQL injection to identify claim details, accesses claims belonging to other users via IDOR, and approves payouts silently without audit logging.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL injection in claim search reveals internal claim IDs | Medium | A03 | `app.py` → `search_claims()` |
| 2 | IDOR on claim detail endpoint allows viewing/modifying any claim | Medium | A01 | `app.py` → `get_claim()` |
| 3 | No audit logging on claim approval allows silent payout | Low | A09 | `app.py` → `approve_claim()` |

**Attack narrative**:
1. The attacker logs in as a low-privileged customer.
2. The attacker uses the claim search endpoint `/api/claims/search?q=1' OR '1'='1` (or union-based payloads) to trigger SQL injection, leaking claim IDs, status, and request details for other users.
3. The attacker requests specific claim details using the IDOR vulnerability at `/api/claims/<claim_id>`. Since there is no ownership check, they retrieve the claimant's information.
4. Using adjuster credentials (or session takeover/escalation if combined, or directly if they possess an adjuster account but want to perform actions without detection), they approve the claims at `/api/claims/<claim_id>/approve`. Because the system fails to log this action, the fraud goes completely unnoticed.

**Combined Impact**: `data_modification` — Attacker executes unauthorized payouts silently without any audit trail or logging records.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/login` | None | User authentication |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/auth/me` | Session | Current session details |
| GET    | `/api/policies` | Session | List policies (scoped to customer, or all for adjusters) |
| GET    | `/api/claims/search` | Session | Search claims (vulnerable to SQLi) |
| GET    | `/api/claims/<claim_id>` | Session | Get claim details (vulnerable to IDOR) |
| POST   | `/api/claims` | Session | File a claim |
| POST   | `/api/claims/<claim_id>/approve` | Adjuster/Admin | Approve claim and trigger payout (vulnerable to logging failure) |
| GET    | `/api/admin/stats` | Admin | System financial statistics (Decoy) |
| GET    | `/api/admin/users` | Admin | List all users |

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. The application runs on port `8091`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-21-insurance-claims .
   ```
2. Run the container:
   ```bash
   docker run -p 8091:8091 app-21-insurance-claims
   ```
