# Phase 04 TODO — Real Kafka Streaming + Enterprise UI

## Pre-requisites
- [ ] Phase 3 complete: grading service working, rate limiter active
- [ ] Read vuln-inventory.md — confirm no-touch files

## Real Kafka Producer
- [ ] Rewrite `src/config/kafka_client.py`:
  - `KafkaProducer` singleton connected to `KAFKA_BROKER` from settings
  - `publish(topic, key, value)` method
  - Import and use `kafka-python` library
- [ ] Update `src/controllers/submission_controller.py` → `submit_quiz()`:
  - After grading, call `kafka_client.publish('grading', submission_id, result)`

## Real Kafka Consumer — GradingListener
- [ ] Rewrite `src/workers/grading_listener.py`:
  - `KafkaConsumer` on `grading` topic
  - Consume message, retrieve score from grading service, write to PostgreSQL grades table
  - Add A09 annotation (if not present from Phase 3)
  - Add decoy print stub

## Real Kafka Consumer — ImportListener
- [ ] Rewrite `src/workers/import_listener.py`:
  - `KafkaConsumer` on `course-imports` topic
  - Consume message, deserialize pickle bytes → VULN-03 preserved
  - Add `kafka-python` import, keep existing pickle RCE logic verbatim

## A10 Vulnerability — SSRF in Course Import
- [ ] Edit `src/services/import_service.py`:
  - Add `fetch_content(url)` method
  - Use `requests.get(url)` with NO validation on scheme, hostname, or IP range
  - Add comment: `# VULNERABILITY A10: Course content import fetches user-supplied URLs without hostname or private-network validation`
  - Add comment: `# CHAIN LINK 2 (chain-03): SSRF in import_service.fetch_content() enables internal network pivot using leaked debug topology`
- [ ] Add decoy `fetch_metadata(url)`:
  - Same signature but validates against an allowlist before fetching
  - Add comment noting it's safe
- [ ] Wire `fetch_content` into course import endpoint or worker

## A07 Vulnerability — Weak Dashboard Session
- [ ] Edit `src/controllers/auth_controller.py`:
  - Add `dashboard_login()` route
  - Set session cookie without `httpOnly` or `secure` flags
  - Add comment: `# VULNERABILITY A07: Dashboard session cookie set without httpOnly or secure flags`
- [ ] Add decoy in existing API `login()`:
  - Ensure existing API login sets `httpOnly=True, secure=True, samesite='Lax'`
  - Add comment noting it's the safe variant

## Student Dashboard
- [ ] Create `templates/dashboard_student.html`:
  - Gradebook: list of quiz scores per course
  - Active courses: enrolled courses with progress
  - Enrollment: link/button to available courses
- [ ] Create `static/js/dashboard.js`: Chart.js or inline charts for grade visualization
- [ ] Create `static/css/dashboard.css`: clean dashboard styling
- [ ] Register route in Flask: `GET /dashboard/student`

## Instructor Dashboard
- [ ] Create `templates/dashboard_instructor.html`:
  - Quiz builder: list of quizzes per course, create/edit links
  - Grading queue: submissions pending manual review
  - Student list: enrolled students per course
- [ ] Register route in Flask: `GET /dashboard/instructor`

## Verification
- [ ] Restart app with Docker Compose
- [ ] Verify real Kafka producer/consumer works:
  - Submit a quiz → event published to `grading` topic
  - GradingListener consumes event → score written to PostgreSQL
- [ ] Verify pickle RCE (VULN-03) via real Kafka:
  - Publish malicious pickle to `course-imports` topic
  - ImportListener deserializes → RCE triggered
- [ ] Verify A10 SSRF:
  - Submit import URL pointing to `http://localhost:8085/api/debug/config`
  - Content is fetched from the internal debug endpoint
- [ ] Verify A07 weak session:
  - Login via dashboard → inspect cookie → `httpOnly` and `secure` flags absent
  - Login via API → inspect cookie → `httpOnly` and `secure` flags present (decoy)
- [ ] Verify dashboards render at `/dashboard/student` and `/dashboard/instructor`
- [ ] Verify existing vulnerabilities still exploitable
- [ ] Verify decoys:
  - `fetch_metadata()` rejects internal hostnames
  - API login has secure cookie flags
- [ ] Run `tests/test_modular_contract.py`

## Regular Commits
- [ ] Commit after each major task:
  `git add -A && git commit -m "app-05 phase-04: <descriptive message>"`
- [ ] Push to remote after each commit

## Phase Status Report
- [ ] Create `phase-04/status-report.md` after completion:
  - What was implemented
  - Files created (count)
  - Files modified (count)
  - Vulnerabilities planted (type, location)
  - Decoys planted (location)
  - Existing vulns still intact? (yes/no)
  - Chains functional? (yes/no)
  - Tests passing? (yes/no)
  - Blockers
