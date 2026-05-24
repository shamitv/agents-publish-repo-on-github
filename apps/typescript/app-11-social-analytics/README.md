# App 11 — Social Media Analytics Dashboard

## Overview

A full-stack analytics platform built with **Express / TypeScript** (Backend) and a decoupled client-side Single Page Application (**HTML5 + vanilla JS + CSS SPA**) served under static asset routes. The system manages social media metrics tracking, custom widgets, and campaign URL previews.

This application is built for security-agent benchmarking and evaluation purposes.

---

## Business Domain

**Marketing / Social Media** — Used by marketing professionals to track campaign performance, monitor engagement, and preview external links.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Node.js, Express, TypeScript |
| Frontend | Decoupled client-side SPA (HTML5, JS, CSS) |
| Database | In-Memory Object Store |
| Containerisation | Docker |

---

## Features

### Analytics Dashboard
- Dynamic widgets displaying real-time marketing metrics.
- Customizable dashboard layout.

### Campaign URL Preview
- Fetch and preview metadata for external campaign links before publishing.

### Security Benchmarking

This application contains hidden, realistic vulnerabilities mapped to the OWASP Top 10 categories, designed to challenge security agents and code analysis systems.

For ground-truth details regarding the vulnerabilities, see the `.vulns` file in this directory.

---

## Chained Vulnerability Scenario

### Chain: "SSRF to Cloud Metadata → Full Credential Response → IAM Key Exfiltration"

Three individually weak issues chain into complete cloud IAM credential theft via a single unauthenticated request sequence.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `POST /api/preview` fetches any URL server-side via `axios.get()` with no IP blocklist, hostname validation, or DNS rebinding protection — allows reaching `169.254.169.254` (AWS IMDS) | Medium | A10 | `src/index.ts` → `/api/preview` handler |
| 2 | The SSRF response previously truncated output to 500 characters; truncation removed so the full metadata service response body is returned to the caller. AWS IMDSv1 IAM credential payloads are 600+ bytes and would have been cut off | Low | A05 | `src/index.ts` → `/api/preview` handler |
| 3 | `GET /api/debug/headers` returns all incoming request headers, including proxy-injected internal routing headers; a client proxying through the metadata fetch can extract forwarded authorization headers | Low | A05 | `src/index.ts` → `/api/debug/headers` handler |

**Attack narrative**: The attacker posts `{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}` to `/api/preview`. The SSRF returns the full IAM role name. A follow-up request fetches `http://169.254.169.254/latest/meta-data/iam/security-credentials/{role}` and the complete response (now untruncated) delivers `AccessKeyId`, `SecretAccessKey`, and `Token`. The attacker uses these temporary credentials to assume the instance role and pivot across cloud resources.

**Combined Impact**: Complete AWS IAM credential exfiltration enabling lateral movement across cloud infrastructure.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Serves the client-side SPA portal |
| POST | `/api/auth/login` | — | Authenticates and establishes session |
| POST | `/api/auth/logout` | — | Terminates active portal session |
| GET | `/api/auth/me` | ANY | Retrieves authenticated user profile |
| GET | `/api/widgets` | ANY | Retrieves user dashboard widgets |
| POST | `/api/widgets` | ANY | Creates a new widget |
| POST | `/api/preview`| ANY | Generates preview for a given URL |

---

## Running Locally

```bash
cd apps/typescript/app-11-social-analytics
npm install
npm run build
npm start
# Frontend served at http://localhost:8011
```

## Running via Docker

```bash
docker build -t app-11-social-analytics .
docker run -p 8011:8011 app-11-social-analytics
```
