# Charity Donation Platform

## Overview
A Flask web application representing a nonprofit platform where users can browse campaigns, make donations, and staff/administrators can manage donor list records and issue refunds.

## Business Domain
Nonprofit & Fundraising Services

## Tech Stack
- Python 3.10
- Flask
- SQLite (in-memory)

## Features
- User authentication and session management
- Browse active campaigns (with parameterized search decoy)
- Donate to campaigns (with CSRF validation decoy)
- Search donation logs and notes
- Issue refunds for specific donation transactions
- Admin view to check system audit logs

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/python/app-46-charity-donations/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "API Key Exposure → SQLi Donor Dump → Silent Refund Fraud"

An attacker reads a hardcoded Stripe API key, extracts transaction IDs via SQL injection, and executes silent refund fraud without audit trail logging.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Hardcoded Stripe key in source code | Low | A02 | `app.py` → `STRIPE_KEY` |
| 2 | SQL injection in donation search reveals transaction IDs | Medium | A03 | `app.py` → `search_donations()` |
| 3 | Refund processing writes no audit logs | Low | A09 | `app.py` → `process_refund()` |

**Attack narrative**:
1. The attacker inspects the codebase and extracts the hardcoded payment gateway credential `STRIPE_KEY`.
2. The attacker logs in as a staff member (or takes over a staff session).
3. The attacker calls the search endpoint `/api/donations/search?q=1' OR '1'='1` to trigger SQL injection, dumping the entire `donations` database table, exposing donor emails, names, amounts, and transaction IDs (e.g. `ch_1234567890abcdef`).
4. Using the Stripe API key and these transaction IDs, the attacker triggers refunds directly or via the refund endpoint `/api/donations/<donation_id>/refund`.
5. The application completes the refund via the payment gateway, but leaves no system audit log entries, making the theft extremely difficult to trace.

**Combined Impact**: `db_exfiltration` — Attacker dumps the complete donor registry containing personal information and performs financial theft without leaving logs.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/login` | None | Authenticate user and obtain CSRF token |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/auth/me` | Session | Get active user details |
| GET    | `/api/donations/search` | Staff/Admin | Search donation records (vulnerable to SQLi) |
| POST   | `/api/donations/<donation_id>/refund` | Staff/Admin | Issue donation refund (vulnerable to logging failure) |
| GET    | `/api/campaigns` | None | List active campaigns (Decoy: parameterized SQL) |
| POST   | `/api/donations` | Session | Submit new donation (Decoy: CSRF validation) |
| GET    | `/api/admin/audit/logs` | Admin | Retrieve administrative event logs |

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. The application runs on port `8096`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-46-charity-donations .
   ```
2. Run the container:
   ```bash
   docker run -p 8096:8096 app-46-charity-donations
   ```
