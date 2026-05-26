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

For chained vulnerability scenarios, see [scenarios.md](scenarios.md).

### Analytics Dashboard
- Dynamic widgets displaying real-time marketing metrics.
- Customizable dashboard layout.

### Campaign URL Preview
- Fetch and preview metadata for external campaign links before publishing.

### Security Benchmarking

This application contains hidden, realistic vulnerabilities mapped to the OWASP Top 10 categories, designed to challenge security agents and code analysis systems.

For ground-truth details regarding the vulnerabilities, see the `.vulns` file in this directory.

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