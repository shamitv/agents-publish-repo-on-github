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

## 4. Impact on Planted Vulnerabilities
- **VULN-01 (A01 - IDOR)**: The quiz grading service retrieves student submission records from MongoDB. The quiz controller (`controllers/quizController.py`) fails to check if the authenticated user's ID matches the submission owner's ID, exposing MongoDB document contents.
- **VULN-02 (A05 - Security Misconfiguration)**: The debug configuration endpoint is moved to a dedicated helper route. It leaks full system profiles including Kafka brokers, PostgreSQL connections, MongoDB URIs, and Flask secrets.
- **VULN-03 (A08 - Software and Data Integrity Failures)**: The course import service receives base64 encoded pickle data representing course outlines. This import task is enqueued to the `course-imports` Kafka topic. The `ImportListener` consumer pulls the message and runs `pickle.loads()`, causing RCE on the backend Kafka worker.
- **Chain-01 (Config Leak → Session Forgery → Pickle RCE)**: Attacker reads configuration via debug endpoint, signs an admin session, uploads the payload, and exploits the background Kafka consumer worker.
- **Chain-02 (State Confusion Pivot to IDOR)**: Attacker manipulates prerequisite validation states inside MongoDB through race conditions in the enrollment queue, bypassing access blocks.
