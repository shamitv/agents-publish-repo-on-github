# Phase 04: Real Kafka Streaming + Enterprise UI

## Goal

Replace the Kafka stub with a real `kafka-python` producer/consumer pipeline, wire the grading and import workers to real Kafka topics, build student and instructor portal dashboards, and plant A10 (SSRF) and A07 (weak session cookies) vulnerabilities.

## Scope

### Included
- [ ] Replace thread-queue stub transport with real `kafka.KafkaProducer` / `kafka.KafkaConsumer` publish/subscribe -- config connection already set up in Phase 1
- [ ] Wire `POST /api/submissions` to emit grading events to `grading` topic
- [ ] Wire `GradingListener` as real Kafka consumer on `grading` topic
- [ ] Wire `ImportListener` as real Kafka consumer on `course-imports` topic
- [ ] Verify pickle RCE (VULN-03) works via real Kafka topic
- [ ] Student dashboard: gradebook, active courses, enrollment
- [ ] Instructor dashboard: quiz builder, grading queue console
- [ ] Plant A10: SSRF in course content import
- [ ] Plant A07: dashboard session cookies missing `httpOnly`/`secure`
- [ ] Add decoys: URL allowlist on import GET, proper session config on auth

### Excluded
- No new API endpoints (dashboards served as static HTML)
- No verification pass (Phase 5)

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Dashboards served as Flask static templates | No React/Vite dependency; keeps scope manageable for LMS upgrade |
| Kafka topics auto-created on first produce | Simplifies configuration; matches Docker Compose default settings |
| A10 SSRF planted in course import URL fetch | The import flow naturally supports fetching remote course content — SSRF fits the domain |
| A07 planted in dashboard blueprint only | API auth endpoint retains proper cookie config as a nearby decoy |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone | A10 | CWE-918 | `src/services/import_service.py` → `fetch_content()` | Course content import fetches user-supplied URLs without hostname or private-network validation | High |
| 2 | Standalone | A07 | CWE-614 | `src/controllers/auth_controller.py` → `dashboard_login()` | Dashboard session cookie is set without `httpOnly` or `secure` flags, enabling client-side script access | Low |

### Chain-03 Step 2

| Chain | Step | OWASP | CWE | Location | Description | Severity |
|-------|------|-------|-----|----------|-------------|----------|
| chain-03 | 2 | A10 | CWE-918 | `src/services/import_service.py` → `fetch_content()` | Course import fetches attacker-controlled URLs without hostname validation; attacker uses leaked topology from chain-03 step 1 (A05) to pivot internally | Medium |

**Source comments**:
- `# VULNERABILITY A10: Course content import fetches user-supplied URLs without hostname or private-network validation`
- `# CHAIN LINK 2 (chain-03): SSRF in import_service.fetch_content() enables internal network pivot using leaked debug topology`
- `# VULNERABILITY A07: Dashboard session cookie set without httpOnly or secure flags`
- `# CHAIN LINK 1 (chain-03): Debug endpoint leaks internal service hostnames and topology, enabling SSRF-based internal pivot`

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `src/services/import_service.py` → `fetch_metadata()` | Co-located with SSRF; also accepts a URL parameter | Validates hostname against an allowlist before fetching |
| 2 | `src/controllers/auth_controller.py` → `login()` (API) | Same file as vulnerable `dashboard_login()` | Sets session cookie with `httpOnly=True, secure=True, samesite='Lax'` |

## Data Model Changes

No new tables or collections.

## API Contracts

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/dashboard/student` | Student | Student portal: gradebook, active courses, enrollments |
| GET | `/dashboard/instructor` | Instructor+ | Instructor portal: quiz builder, grading queue, student list |

## Artifact Updates

- `src/config/kafka_client.py`: Replace stub with real `kafka-python` producer/consumer
- `src/config/settings.py`: Add dashboard config, session cookie policy
- `src/controllers/auth_controller.py`: Add `dashboard_login()` with A07
- `src/services/import_service.py`: Add `fetch_content()` with A10
- `src/workers/grading_listener.py`: Wire to real Kafka consumer
- `src/workers/import_listener.py`: Wire to real Kafka consumer (VULN-03 preserved)
- `templates/dashboard_student.html`: New
- `templates/dashboard_instructor.html`: New
- `static/js/dashboard.js`: New
- `static/css/dashboard.css`: New
- `.vulns`: Add VULN-06 (A10), VULN-07 (A07), chain-03 components
- `README.md`: Add dashboard endpoints
- `scenarios.md`: Add chain-03 narrative

## Dependencies on Other Phases

- **Depends on Phase 1**: Real Kafka must be running
- **Depends on Phase 2**: Data models exist for dashboard queries
- **Depends on Phase 3**: Grading service exists for Kafka consumer to use
- **Phase 5** depends on Phase 4: Chain scenarios need finalized code
