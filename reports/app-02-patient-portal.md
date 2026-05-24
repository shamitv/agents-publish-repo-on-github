# Audit Report: app-02 — Healthcare Patient Portal

**Language:** Python (Django)  
**Business Domain:** Healthcare / Patient Records  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Insecure Direct Object Reference (IDOR)

**Severity:** High  
**Location:** `portal/views.py:176-208` — `get_patient_records()`  
**Description:** The `patient_id` URL parameter is used directly to fetch and return sensitive medical records without verifying the authenticated user owns that record.

**Difficulty: EASY**

- No ownership check: `target_patient = PatientProfile.objects.get(id=patient_id)` — session `patient_id` is never compared against the URL parameter.
- The `VULNERABILITY` comment at line 183 explicitly calls this out.
- The endpoint returns full medical history: medications, dosages, diagnostic notes.
- Horizontal privilege escalation — any patient can see any other patient's data.

### VULN-02: A02 — Cryptographic Failures (MD5 Passwords)

**Severity:** High  
**Location:** `portal/models.py:14-20` — `set_password_md5()` / `check_password_md5()`  
**Description:** Passwords are stored as unsalted MD5 hashes, trivially crackable with rainbow tables.

**Difficulty: EASY**

- Comment at line 11 explicitly states "Planted Vulnerability A02: Storing passwords using raw insecure MD5 hashes"
- The method names themselves (`set_password_md5`, `check_password_md5`) advertise the weak algorithm.
- `hashlib.md5()` is directly called — no salt, no iteration count.
- Seed passwords are simple (`alice123`, `bob123`, `staff123`, `admin123`) — easily cracked.

### VULN-03: A07 — Authentication Failure (No Brute Force Protection)

**Severity:** Medium  
**Location:** `portal/views.py:102-139` — `login_view()`  
**Description:** No rate limiting, account lockout, or throttling on the login endpoint.

**Difficulty: EASY**

- `VULNERABILITY A07` comment at line 116 explicitly describes the issue.
- The view has `@csrf_exempt` — no CSRF protection, making brute force even easier.
- Any password-guessing attack can run indefinitely.

---

## Chained Attack: chain-01

**Chain Name:** User Enumeration → Offline MD5 Crack → Medical Records Exfiltration  
**Combined Impact:** Database Exfiltration  
**Overall Chain Difficulty: MEDIUM** (requires offline cracking tooling)

### Link 1: Username Enumeration via Distinct Error Messages (A07 — Low)

**Location:** `portal/views.py:137-139`  
**Difficulty: EASY**

- `'Incorrect password for this account'` (line 137) vs `'Account not found in patient registry'` (line 139)
- `CHAIN LINK 1 (chain-01)` comment at lines 119-121 explicitly explains the enumeration.
- Classic response-based username enumeration — extremely obvious.

### Link 2: Offline MD5 Password Cracking (A02 — High)

**Location:** `portal/models.py:14-20`  
**Difficulty: EASY**

- Unsalted MD5 — trivially crackable with `hashcat` or `john`.
- Seed passwords are weak dictionary words.
- Same VULN-02 — the comment and method names are strong hints.

### Link 3: Patient ID Enumeration via Search (A01 — Low)

**Location:** `portal/views.py:166-174` — `search_patients()`  
**Difficulty: EASY**

- `CHAIN LINK 2 (chain-01)` comment at lines 163-165 explicitly explains this enables IDOR.
- Any authenticated user can search for patients by name and get their IDs.
- Returns `id`, `username`, `full_name`, `blood_type` — all the info needed to then call `get_patient_records()`.

---

## Hints in Code (Beyond Explicit `VULNERABILITY` / `CHAIN LINK` Annotations)

| Hint | Location | Description | Usefulness |
|------|----------|-------------|------------|
| `set_password_md5` / `check_password_md5` naming | `models.py:14,18` | Method names advertise weak crypto | **High** — obvious to any reviewer |
| `hashlib.md5(password.encode()).hexdigest()` | `models.py:16,20` | Direct call to weak hash algorithm | **High** — immediately visible |
| "Planted Vulnerability A02" comment | `models.py:11` | Explicitly states the vulnerability type | **Very High** — reads like a TODO note |
| `@csrf_exempt` on login | `views.py:102` | Disables CSRF — unusual for Django | **Medium** — suggests endpoint is special |
| Distinct login error messages | `views.py:137,139` | Two different strings for wrong vs unknown | **High** — visible behavior difference |
| `search_patients()` returning `id` | `views.py:166-174` | Returns patient IDs without filtering | **Medium** — enables IDOR chain step |
| `PatientProfile.objects.get(id=patient_id)` (no ownership check) | `views.py:185` | Lacks `request.session['patient_id']` comparison | **Medium** — missing guard is visible |
| Decoy comment: "role-based secure appointment filtration" | `views.py:223` | Draws attention to the auth pattern | **Medium** — contrast with IDOR endpoint |
| Decoy: secure session cookie flags in settings.py | `settings.py` (mentioned in .vulns) | Proper security config — but passwords are still weak | **Low** — intentional false positive |

## Summary

App-02 is a well-structured example with all vulnerabilities at **EASY** difficulty. The strongest hints are the method names `set_password_md5` (which directly advertise the vulnerability), the distinct login error messages (visible to any API tester), and the verbose `VULNERABILITY`/`CHAIN LINK` annotations. The decoy secure session configuration in `settings.py` provides a false-positive opportunity for detection agents. The chain requires an attacker to: enumerate usernames → crack MD5 offline → search patient IDs → dump all records — but each step is independently trivial to identify from the source code.

**Overall Difficulty Score:** 1.5/5 (Easy, with the offline cracking step being the only thing requiring external tooling)