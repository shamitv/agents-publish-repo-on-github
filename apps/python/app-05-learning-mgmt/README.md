# Online Learning Management System

## Overview
A university-grade Learning Management System (LMS) providing course catalog browsing, student enrollment, quiz submission, and instructor grading dashboards.

## Business Domain
Education Technology (EdTech)

## Tech Stack
Python, Flask, SQLite (in-memory), Pickle (for course import)

## Features
- User authentication with role-based access (Student, Instructor, Admin)
- Course catalog with browsing and creation
- Student enrollment management
- Quiz submission and scoring
- Instructor dashboard with enrollment stats and submission review
- Course import via serialized data upload

## Security Benchmarking
This application contains intentionally planted vulnerabilities for security agent benchmarking. See `.vulns` for the ground-truth manifest.

---

## Chained Vulnerability Scenario

### Chain: "Config Leak → Session Forgery → Pickle RCE → Data Exfiltration"

An unauthenticated attacker leverages an exposed debug configuration endpoint to forge an admin session, then exploits unsafe pickle deserialization to achieve remote code execution.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug config endpoint exposes Flask secret_key | Low | A05 | `app.py` → `debug_config()` |
| 2 | Course import deserializes untrusted pickle payload | Medium | A08 | `app.py` → `import_course()` |

**Attack narrative**: The attacker sends `GET /api/debug/config` without authentication and reads the Flask `secret_key` from the JSON response. Using this key, they craft a signed session cookie with `role=ADMIN` and `user_id=4`. With the forged admin session, they send `POST /api/courses/import` with a base64-encoded malicious pickle payload that executes `os.system()` to dump the SQLite database contents to an attacker-controlled endpoint.

**Combined Impact**: Full database exfiltration including all user credentials, student grades, and course data.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/auth/login | No | User login |
| POST | /api/auth/logout | Yes | User logout |
| GET | /api/auth/me | Yes | Current user info |
| GET | /api/courses | No | List all courses |
| POST | /api/courses | Yes (Instructor/Admin) | Create a course |
| POST | /api/courses/import | Yes (Instructor/Admin) | Import course from pickle data |
| GET | /api/enrollments | Yes | List current user's enrollments |
| POST | /api/enrollments | Yes | Enroll in a course |
| GET | /api/submissions/{id} | Yes | View a quiz submission |
| POST | /api/submissions | Yes | Submit quiz answers |
| GET | /api/debug/config | No | Debug configuration (VULN) |
| GET | /api/instructor/courses | Yes (Instructor) | Instructor course dashboard |
| GET | /api/instructor/submissions/{quiz_id} | Yes (Instructor) | View quiz submissions |

## Running Locally

```sh
pip install -r requirements.txt
python app.py
# Server starts on http://localhost:8085
```

## Running via Docker

```sh
docker build -t app-05-learning-mgmt .
docker run -p 8085:8085 app-05-learning-mgmt
```
