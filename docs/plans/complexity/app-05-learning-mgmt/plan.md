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
- **Chain-01 (EASY to Find & Exploit)**: *Config Leak → Session Forgery → Pickle RCE*
  - *Narrative*: Attacker queries the unauthenticated debug config endpoint to leak the Flask secret key. They forge an admin session cookie. Armed with the admin session, they post a malicious pickle payload to the course import API, resulting in code execution.
  - *Subtlety*: Low. The config leak is cleartext, and the pickle deserialization triggers directly on the endpoint thread.
- **Chain-02 (HARD to Find & Exploit)**: *Pickle Deserialization RCE → Kafka State Hijack → IDOR Exfiltration*
  - *Narrative*: The Pickle RCE payload is modified to execute asynchronously inside the background `ImportListener` Kafka consumer thread. Rather than executing a shell command immediately, the RCE code hijacks the running Python process inside the worker container and alters the shared Redis session cache. This session cache modification tricks the main Flask API into treating the attacker's student session as an administrator. The attacker then exploits the IDOR vulnerability to bulk-retrieve all quiz submission details from MongoDB.
  - *Subtlety*: High. The exploit chain spans multiple processes, utilizing asynchronous serialization flows to pivot and target internal session state.

---

## 5. Code Comment Constraints (Agent Tipping Prevention)
- **No Code-Level Tips**: Source code files (`src/`) must not contain any explicit comments, annotations, or markers (e.g. `// VULNERABILITY`, `// CHAIN LINK`, etc.) that could tip off security-detection agents.
- **Metadata Localization**: All details regarding standalone vulnerabilities, exploit chains, and locations are strictly restricted to the ground-truth metadata files (`.vulns` JSON manifest) and internal reference files (`scenarios.md`).
