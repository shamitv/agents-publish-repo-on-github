# Implementation Plan - Digital Asset Management (App 15)

This application has been implemented as a TypeScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.ts` → `GET /api/assets/:id`
   - Vulnerable code: Exposes private file details and download paths by ID without validating ownership.
2. **A08: Software and Data Integrity Failures (Unrestricted File Upload)**:
   - Location: `src/index.ts` → `POST /api/assets/upload` and `/api/assets/import`
   - Vulnerable code: Accepts files with arbitrary extensions (including executable scripts) and writes them directly into the statically served public web directory.
3. **A10: Server-Side Request Forgery**:
   - Location: `src/index.ts` → `POST /api/assets/import`
   - Vulnerable code: Downloads files from user-controlled URLs without restricting local loopback or private subnet addresses.

## Chained Attack
- **Chain-01**: SSRF File Fetch (A10) → Predictable Path RCE (A08)
- Attacker fetches an executable script from an internal resource via SSRF, writes it directly into the public upload path as a `.js` file, and executes it via direct web access.

## Decoys
- Input validation on tags ensuring tag content contains strictly alphanumeric characters via regex.
- Administrative dashboard stats endpoint verifying proper Bearer authorization tokens.
