# Audit Report: app-05 — Online Learning Management System

**Language:** Python (Flask)  
**Business Domain:** Education Technology (EdTech)  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Insecure Direct Object Reference (IDOR)

**Severity:** High  
**Location:** `app.py:251-281` — `get_submission()`  
**Line:** `cursor.execute("SELECT s.id, s.answers, s.score, s.submitted_at, q.title as quiz_title, u.username as student_name FROM submissions s ... WHERE s.id = ?", (submission_id,))`

**Difficulty: EASY**

- The `submission_id` path parameter is taken directly from the URL with no ownership verification.
- Any authenticated user can view any submission by enumerating IDs.
- No check that `student_id == session['user_id']` is performed.
- The `VULNERABILITY A01` comment explicitly calls out the IDOR.

### VULN-02: A05 — Security Misconfiguration (Exposed Debug Endpoint)

**Severity:** Medium  
**Location:** `app.py:306-321` — `debug_config()`  
**Line:** `GET /api/debug/config` returns `app.secret_key`, full environment variables, database path, and server working directory

**Difficulty: EASY**

- No authentication required — completely unauthenticated endpoint.
- Returns the Flask `secret_key` directly, enabling session cookie forgery.
- Also leaks all environment variables, Python version, and server working directory.
- The `VULNERABILITY A05` comment explicitly marks it.

### VULN-03: A08 — Insecure Deserialization (Pickle RCE)

**Severity:** Critical  
**Location:** `app.py:325-358` — `import_course()`  
**Line:** `course_obj = pickle.loads(raw_bytes)` — deserializes user-supplied base64-encoded pickle data

**Difficulty: EASY**

- Unvalidated `pickle.loads()` on attacker-controlled input allows arbitrary code execution.
- The data arrives as base64-encoded user input from `data.get('course_data', '')`.
- Role check exists (INSTRUCTOR/ADMIN required), but session can be forged via VULN-02.
- The `VULNERABILITY A08` comment explicitly marks it as picke deserialization RCE.

---

## Chained Attack: chain-01

**Chain Name:** Config Leak → Session Forgery → Pickle RCE → Data Exfiltration  
**Combined Impact:** Database Exfiltration  
**Overall Chain Difficulty: EASY**

### Link 1: Debug Config Endpoint (A05 — Low)

**Location:** `app.py:306-321` — `debug_config()`  
**Difficulty: EASY**

- Unauthenticated `GET /api/debug/config` returns the Flask `secret_key`.
- The `CHAIN LINK 1` comment at line 311 explicitly explains this enables session cookie forgery.
- Also exposes environment variables which may contain additional secrets.

### Link 2: Pickle Deserialization (A08 — Medium)

**Location:** `app.py:325-358` — `import_course()`  
**Difficulty: EASY**

- `pickle.loads(raw_bytes)` on attacker-controlled input allows arbitrary code execution.
- Requires INSTRUCTOR or ADMIN role, but the secret_key from Link 1 can be used to forge a session with `role=ADMIN`.
- The `CHAIN LINK 2` comment at line 330 explicitly explains this is the RCE step after forging admin session.

---

## Hints in Code (Beyond Explicit `VULNERABILITY` / `CHAIN LINK` Annotations)

| Hint | Location | Description | Usefulness |
|------|----------|-------------|------------|
| Hardcoded `app.secret_key` | Line 8 | `'lms_secret_key_quantum_learn_2026'` is a highly conspicuous string | **High** — obvious to any code reviewer |
| `CHAIN LINK 1` comment explaining session forgery | Lines 10-11 | Directly explains the attack chain | **Very High** — the comment itself outlines the scenario |
| `debug_config` function name | Line 307 | Clearly indicates debug/configuration exposure | **Medium** — naming draws attention |
| No auth check on debug endpoint | Lines 306-321 | Entire method has no `if 'user_id' not in session` guard | **High** — absence of auth is obvious |
| `CHAIN LINK 2` comment explaining pickle RCE | Lines 329-331 | Directly explains this is the RCE step after forging admin | **Very High** — explicit chain documentation |
| `pickle.loads(raw_bytes)` | Line 343 | The dangerous call is on its own line with a comment | **High** — picke deserialization is a well-known code smell |
| Decoy: Secure parameterized login query | Lines 128-131 | Parameterized SQL for login — draws contrast to the picke risk | **Medium** — tells analyst secure patterns exist nearby |
| Decoy: Instructor role check on course creation | Lines 183-184 | Proper role guard — contrasts with the exposed debug endpoint | **Medium** — shows where auth is done properly vs not |
| Decoy: Enrollment scoped to current user | Lines 211-214 | Secure data scoping — contrasts with IDOR on submissions | **Medium** — highlights the missing ownership check |
| `app.run(debug=True)` | Line 413 | Debug mode enabled in production | **Low** — standard Flask misconfig |

## Summary

App-05 features three clear vulnerabilities with a clean 2-step chained attack. The debug endpoint leaking the Flask `secret_key` is the most obvious entry point, enabling session forgery that bypasses the role check on the picke deserialization endpoint. All vulnerabilities are explicitly annotated with `VULNERABILITY` and `CHAIN LINK` comments. Three decoy safe patterns (parameterized login, role-guarded course creation, user-scoped enrollment listing) are placed nearby as false-positive tests for detection agents.

**Overall Difficulty Score:** 1/5 (Easiest)