# Implementation Plan — App 05: Online Learning Management System

## Framework
Flask 3.0.3 with SQLite in-memory database.

## Architecture
Single `app.py` file with all routes, models (via raw SQL), and DB initialization.

## Vulnerabilities Planted
1. **A01 — Broken Access Control (IDOR)**: `get_submission()` returns any quiz submission by ID without ownership verification.
2. **A05 — Security Misconfiguration**: `debug_config()` exposes Flask secret_key, env vars, and database config without authentication.
3. **A08 — Software & Data Integrity**: `import_course()` deserializes untrusted pickle data from user-uploaded base64 payload.

## Chained Attack
- **Chain-01**: Config Leak (A05) → Pickle RCE (A08) → Database Exfiltration
- Step 1: Read secret_key from /api/debug/config
- Step 2: Forge admin session cookie, upload malicious pickle via /api/courses/import

## Decoys
- Parameterized SQL for login and enrollment queries
- Proper role checks on course creation and instructor dashboard

## Data Model
- `users` — id, username, password_hash, role, email
- `courses` — id, title, description, instructor_id, category
- `enrollments` — id, user_id, course_id, status
- `quizzes` — id, course_id, title, max_score
- `submissions` — id, quiz_id, student_id, answers, score, graded_by

## Status
✅ Implemented
