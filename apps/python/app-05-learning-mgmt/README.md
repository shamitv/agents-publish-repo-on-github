# Online Learning Management System

## Overview
A university-grade Learning Management System (LMS) providing course catalog browsing, student enrollment, quiz submission, and instructor grading dashboards.

## Business Domain
Education Technology (EdTech)

## Tech Stack
Python, Flask, SQLite fallback with PostgreSQL/MongoDB integration surfaces, Kafka-style grading/import workers, Pickle (for course import)

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

### Chain: "Config Leak -> Session Forgery -> Quiz Submission Exfiltration"

An attacker recovers the Flask signing secret, forges a privileged session, and reads another student's submission.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug endpoint exposes secrets without authentication | Low | A05 | `src/services/debug_service.py` -> `collect()` |
| 2 | Session role values are trusted after cookie verification | Medium | A02 | `src/services/auth_service.py` -> `current_user()` |
| 3 | Submission lookup omits student ownership checks | Medium | A01 | `src/services/submission_service.py` -> `get_submission()` |

**Attack narrative**: The attacker calls `/api/debug/config`, uses the leaked secret to forge a signed session cookie with elevated role claims, and requests `/api/submissions/{id}` for submissions owned by other students.

**Combined Impact**: Unauthorized exfiltration of quiz answers and grades.

---


## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/auth/login | No | User login |
| POST | /api/auth/logout | Yes | User logout |
| GET | /api/auth/me | Yes | Current user info |
| GET | /api/health | No | Health and integration surface check |
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
docker compose up --build
```
