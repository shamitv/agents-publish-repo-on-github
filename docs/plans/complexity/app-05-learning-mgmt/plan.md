# Complexity Upgrade Plan: app-05-learning-mgmt (Enterprise Architecture)

This document details the architectural plan to upgrade the Online Learning Management System to a multi-database, event-driven enterprise application.

## 1. Overview
The current Flask application will be restructured into a professional, decoupled MVC codebase:
- **Polyglot Storage**: PostgreSQL for student profiles, course metadata, and enrollments; MongoDB for dynamic quiz questions and flexible submission answers.
- **Event Streaming**: Apache Kafka for quiz grading streams and course import tasks.
- **Modular Codebase**: Implement Flask Blueprints to separate auth, course management, and quiz/grading controllers.
- **Complex Business Logic**: Prerequisite course completion validations, auto-grading logic rules, and submission retry rate limiting.
- **Enterprise UI**: Portal dashboard split into Student View (gradebook, active courses) and Instructor View (quiz builder, grading queue console).

---

## 2. Component Design

### A. Database Layer (PostgreSQL & MongoDB)
- **PostgreSQL**: Stores relational structures (`users`, `courses`, `enrollments`).
- **MongoDB**: Stores schema-less quiz configurations (which support multiple question types: multiple-choice, free-text, code snippets) and student submission arrays.

### B. Event Streaming (Apache Kafka)
- **Engine**: Apache Kafka
- **Role**: Handles background quiz grading workflows and async course imports.
- **Work Flow**:
  1. Student posts quiz response array to `/api/quizzes/submit`.
  2. The submission controller enqueues a `quiz-submitted` event to the `grading` Kafka topic.
  3. A background Kafka consumer (`GradingListener`) reads the event, pulls the correct answer keys from MongoDB, scores the submission, records the grade in PostgreSQL, and invalidates the cached gradebook in Redis.

---

## 3. Modular Code Structure
```
src/
├── blueprints/         # Flask blueprints (auth.py, courses.py, quizzes.py)
├── config/             # DB connection helpers and Kafka clients
├── controllers/        # Blueprints request-response controllers
├── services/           # GradingService, CourseService, PrereqValidator
├── models/             # Relational schemas and Mongo models
├── workers/            # Kafka event listeners (GradingListener)
├── static/             # Complex JavaScript-based dashboards
└── main.py             # App initialization and worker threading
```

---

## 4. Vulnerabilities & Exploit Chains Detail

### Standalone Vulnerabilities
- **VULN-01 (A01 - IDOR on Quiz Submission)**:
  - *Location*: `src/controllers/quizzes.py` → `get_submission()`
  - *Description*: Submission retrieval endpoint queries student submissions in MongoDB. It returns quiz responses solely by submission ID, lacking checks verifying if the logged-in student owns the submission.
  - *Decoy Safeguard*: The course edit endpoint validates that the user possesses the INSTRUCTOR role and created the course.
- **VULN-02 (A05 - Debug Configurations Exposure)**:
  - *Location*: `src/blueprints/auth.py` → `debug_config()`
  - *Description*: Unauthenticated API route exposes system settings including Kafka broker addresses, PostgreSQL passwords, and MongoDB credentials.
- **VULN-03 (A08 - Unsafe Pickle Deserialization)**:
  - *Location*: `src/services/CourseService.py` → `import_course()`
  - *Description*: De-serializes course outlines using `pickle.loads()` without restricting classes.

### Exploit Chains
#### chain-01: Config Leak -> Session Forgery -> Quiz Submission Exfiltration
- **Impact**: `db_exfiltration`
- **Attack narrative**: An attacker reads the unauthenticated debug configuration response to recover the Flask session signing secret, forges an instructor/admin session accepted by the auth helper, and then uses the quiz submission IDOR to retrieve other students' MongoDB submission documents in bulk.

| Step | Issue | Severity (standalone) | OWASP | CWE | Location | Method |
|------|-------|-----------------------|-------|-----|----------|--------|
| 1 | Debug configuration endpoint exposes secrets and backing service credentials without authentication. | Low | A05 | CWE-200 | `src/blueprints/auth.py` | `debug_config()` |
| 2 | Session trust logic accepts forged instructor/admin cookies signed with the leaked secret. | Medium | A02 | CWE-347 | `src/blueprints/auth.py` | `current_user()` |
| 3 | Quiz submission lookup returns records by ID without verifying student ownership. | Medium | A01 | CWE-639 | `src/controllers/quizzes.py` | `get_submission()` |

---

## 5. Benchmark Metadata Requirements
- **Source Annotations Required**: Source code must retain the `AGENTS.md` benchmark comments: `// VULNERABILITY <OWASP_ID>: <brief description>` for each standalone vulnerability and `// CHAIN LINK <N> (chain-<ID>): <description>` for every chain step.
- **Metadata Synchronization**: `.vulns`, the README chain section, this plan's chain table, and source comments must agree on OWASP ID, severity, CWE, impact, location, and method.
- **README Chain Section Required**: The app README must keep the required `Chained Vulnerability Scenario` section. `scenarios.md` may provide supplemental narrative, but it must not replace README or `.vulns` content.
- **Decoys Required**: Preserve nearby safe decoy patterns and list them in `.vulns.decoys`.
