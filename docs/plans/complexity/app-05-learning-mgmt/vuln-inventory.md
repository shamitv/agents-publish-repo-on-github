# Vulnerability Inventory — App 05 (Online Learning Management System)

## Purpose

This document enumerates every intentionally planted vulnerability, chain link, and decoy in the **current** app-05 codebase. It serves as a **no-touch zone** reference during the upgrade — no implementation step may remove, weaken, or fix any item listed here.

---

## App Profile

| Property | Value |
|----------|-------|
| App ID | `app-05` |
| Language | Python |
| Framework | Flask |
| Source file count | 37 |
| Complexity rating | 4 — Complex |
| Entry point | `app.py` (Flask factory via `src/main.py`) |
| Manifest | `.vulns` |

---

## Standalone Vulnerabilities

### VULN-01 — IDOR on Quiz Submission

| Field | Value |
|-------|-------|
| OWASP | **A01** — Broken Access Control |
| CWE | CWE-639 |
| File | `src/services/submission_service.py` |
| Method | `get_submission` |
| Severity | High |
| Source Comment | `# CHAIN LINK 3 (chain-01): Forged sessions can read any submission because ownership is not checked.` |
| Source Comment | `# VULNERABILITY A01: Submission lookup does not verify the current session owns the record.` |
| Description | After authentication, the submission retrieval endpoint returns quiz responses by submission ID without verifying the requesting user owns the submission. |

### VULN-02 — Debug Configurations Exposure

| Field | Value |
|-------|-------|
| OWASP | **A05** — Security Misconfiguration |
| CWE | CWE-200 |
| File | `src/services/debug_service.py` |
| Method | `collect` |
| Severity | Medium |
| Source Comment | `# CHAIN LINK 1 (chain-01): Debug endpoint leaks the signing secret and environment without authentication.` |
| Source Comment | `# VULNERABILITY A05: Unauthenticated configuration exposure returns sensitive runtime details.` |
| Description | Unauthenticated `/api/debug/config` endpoint returns the Flask SECRET_KEY, environment variables, and runtime details. |

### VULN-03 — Unsafe Pickle Deserialization

| Field | Value |
|-------|-------|
| OWASP | **A08** — Software and Data Integrity Failures |
| CWE | CWE-502 |
| File | `src/workers/import_listener.py` |
| Method | `load_course` |
| Severity | Critical |
| Source Comment | `# VULNERABILITY A08: Untrusted pickle payload is deserialized without class restrictions.` |
| Description | Course import worker deserializes untrusted pickle bytes from Kafka events without restricting allowed classes, enabling RCE. |

---

## Chained Vulnerability Scenarios

### chain-01: Config Leak → Session Forgery → Quiz Submission Exfiltration

**Combined Impact**: `db_exfiltration`

| Step | OWASP | CWE | File | Method | Severity | Source Comment |
|------|-------|-----|------|--------|----------|----------------|
| 1 | A05 | CWE-200 | `src/services/debug_service.py` | `collect` | Low | `// CHAIN LINK 1 (chain-01): Debug endpoint leaks the signing secret and environment without authentication.` |
| 2 | A02 | CWE-347 | `src/services/auth_service.py` | `current_user` | Medium | `// CHAIN LINK 2 (chain-01): Session role is trusted once the leaked secret enables cookie forgery.` |
| 3 | A01 | CWE-639 | `src/services/submission_service.py` | `get_submission` | Medium | `// CHAIN LINK 3 (chain-01): Forged sessions can read any submission because ownership is not checked.` |

**Attack narrative**: An attacker sends `GET /api/debug/config` to recover the Flask signing secret, forges an instructor/admin session cookie, and then reads any student's quiz submission by ID via `GET /api/submissions/{id}`.

---

## Decoy Patterns (Safe Code Near Vulnerable Areas)

### DECOY-01 — Parameterized Login Query

| Field | Value |
|-------|-------|
| File | `src/repositories/user_repository.py` |
| Pattern | Parameterized SQL in user lookup |
| Why it looks vulnerable | Uses raw SQL with user input |
| Why it is safe | Uses parameterized `%s` placeholders with tuple args that prevent injection |

### DECOY-02 — Role-Gated Course Creation

| Field | Value |
|-------|-------|
| File | `src/controllers/course_controller.py` |
| Method | `create_course` |
| Pattern | Requires INSTRUCTOR or ADMIN role before writing |
| Why it looks vulnerable | Adjacent to the IDOR submission endpoint in the same controller layer |
| Why it is safe | Verifies `session["role"]` explicitly before executing write operations |

### DECOY-03 — Scoped Enrollment Listing

| Field | Value |
|-------|-------|
| File | `src/repositories/enrollment_repository.py` |
| Method | `list_by_user` |
| Pattern | Scopes enrollment rows to current session's user ID |
| Why it looks vulnerable | Colocated with enrollment write operations |
| Why it is safe | Queries always include `WHERE user_id = ?` bound to the authenticated user |

---

## No-Touch Files During Upgrade

These files contain vulnerability annotations and **must not be modified** in ways that weaken or remove the vulnerabilities:

| File | Annotations | Action Allowed? |
|------|------------|-----------------|
| `src/services/submission_service.py` | VULNERABILITY A01, CHAIN LINK 3 (chain-01) | No direct modification |
| `src/services/debug_service.py` | VULNERABILITY A05, CHAIN LINK 1 (chain-01) | No direct modification |
| `src/services/auth_service.py` | CHAIN LINK 2 (chain-01) | No direct modification — session trust logic must remain forgeable |
| `src/workers/import_listener.py` | VULNERABILITY A08 | No direct modification — pickle deserialization must remain unsafe |
| `src/repositories/user_repository.py` | DECOY-01 | No direct modification |
| `src/controllers/course_controller.py` | DECOY-02 | No direct modification |
| `src/repositories/enrollment_repository.py` | DECOY-03 | No direct modification |
| `.vulns` | Ground truth manifest | Update to add entries only; never delete |

**Rule**: If a refactoring step must touch these files (e.g., changing imports after config layer migration, or adding new `CHAIN LINK` annotations for additional chain scenarios), the vulnerability code and comments must be preserved verbatim. New annotations may be added to no-touch files as long as existing vulnerability code and comments remain unchanged. `.vulns` locations must be updated accordingly.

---

## OWASP Coverage Gap Analysis

Current coverage vs. OWASP Top 10: 2021:

| OWASP | Category | Covered? | How |
|-------|----------|----------|-----|
| A01 | Broken Access Control | Yes | VULN-01, Chain Link 3 |
| A02 | Cryptographic Failures | Chain only | Chain Link 2 (forgeable session trust) |
| A03 | Injection | **No** | **Target for future expansion** |
| A04 | Insecure Design | **No** | **Target for this upgrade (Phase 2)** |
| A05 | Security Misconfiguration | Yes | VULN-02, Chain Link 1 |
| A06 | Vulnerable & Outdated Components | **No** | **Target for future expansion** |
| A07 | Identification & Auth Failures | **No** | **Target for this upgrade (Phase 4)** |
| A08 | Software & Data Integrity | Yes | VULN-03 |
| A09 | Security Logging & Monitoring | **No** | **Target for this upgrade (Phase 3)** |
| A10 | SSRF | **No** | **Target for this upgrade (Phase 4)** |

## Planned Vulnerability Additions

The following vulnerabilities will be planted during the complexity upgrade. They are documented here so implementers know the target state before writing code.

### VULN-04 — Insecure Enrollment Design
| Field | Value |
|-------|-------|
| OWASP | **A04** — Insecure Design |
| CWE | CWE-602 |
| Planned file | `src/controllers/enrollment_controller.py` |
| Planned method | `enroll()` |
| Severity | Medium |
| Phase | 2 |
| Description | Enrollment endpoint trusts client-supplied `role` parameter and arbitrary `course_id` without server-side validation of course existence, active status, student prerequisites, or role authorization. |
| Chain role | chain-02 step 1: role escalation via enrollment |

### VULN-05 — Missing Audit Logging
| Field | Value |
|-------|-------|
| OWASP | **A09** — Security Logging & Monitoring Failures |
| CWE | CWE-778 |
| Planned file | `src/workers/grading_listener.py` |
| Planned method | `process_submission()` |
| Severity | Medium |
| Phase | 3 |
| Description | Grading listener writes score updates to PostgreSQL `grades` table without writing corresponding entries to `audit_log`. No record exists of who changed a grade, when, or from what prior value. |
| Chain role | chain-02 step 2: missing audit makes grade tampering undetectable |

### VULN-06 — SSRF in Course Content Import
| Field | Value |
|-------|-------|
| OWASP | **A10** — Server-Side Request Forgery |
| CWE | CWE-918 |
| Planned file | `src/services/import_service.py` |
| Planned method | `fetch_content()` |
| Severity | High |
| Phase | 4 |
| Description | Course content import fetches user-supplied URLs via `requests.get(url)` without hostname or private-network validation. Enables accessing internal-only endpoints from within the Docker network. |
| Chain role | chain-03 step 2: SSRF enables internal pivot using leaked topology from chain-03 step 1 |

### VULN-07 — Weak Dashboard Session Cookies
| Field | Value |
|-------|-------|
| OWASP | **A07** — Identification & Authentication Failures |
| CWE | CWE-614 |
| Planned file | `src/controllers/auth_controller.py` |
| Planned method | `dashboard_login()` |
| Severity | Low |
| Phase | 4 |
| Description | Dashboard session cookie set without `httpOnly` or `secure` flags, enabling client-side script access. API login endpoint retains proper cookie config as a decoy. |
| Chain role | Standalone only |

### Planned Chain Scenarios

| Chain | Name | Steps | Impact | Phases |
|-------|------|-------|--------|--------|
| chain-02 | Enrollment Role Escalation → Missing Audit → Undetected Grade Tampering | A04 (role escalation) → A09 (no audit on grade writes) | `data_modification` | 2, 3 |
| chain-03 | Debug Config Leak → SSRF Internal Pivot | A05 (leaked topology) → A10 (SSRF to `/admin/internal/metrics`) | `lateral_movement` | 4, 5 |

### Planned Decoys

| # | Location | Phase |
|---|----------|-------|
| DECOY-04 | `src/controllers/enrollment_controller.py` `→ list_enrollments()` (scoped, ignores client role) | 2 |
| DECOY-05 | `src/services/import_service.py` `→ fetch_metadata()` (hostname allowlist) | 4 |
| DECOY-06 | `src/controllers/auth_controller.py` `→ login()` API (secure cookie flags) | 4 |
| DECOY-07 | `src/workers/grading_listener.py` `→ audit_enrollment_change()` (proper audit for enrollment only) | 3 |

**Upgrade strategy**: Phase 2→A04, Phase 3→A09, Phase 4→A10+A07 to reach 8/10 coverage.
