# Audit Report: app-28 — Manufacturing Quality Control

**Language:** Java (Spring Boot)  
**Business Domain:** Manufacturing / Quality Control  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (Mass Assignment)

**Severity:** High  
**Location:** `AuthController.java:32-43` — `updateProfile()`  
**Lines:**
```java
// VULNERABILITY A01: Mass assignment allows workers to escalate privilege to QA_MANAGER
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A01`
- Profile update accepts all fields, including `role`
- WORKER can escalate to QA_MANAGER

### VULN-02: A04 — Insecure Design (Missing Approval Check)

**Severity:** Medium  
**Location:** `DefectController.java:17-25` — `resolveDefect()`  
**Lines:**
```java
// VULNERABILITY A04: Critical defect resolution lacks manager approval check
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A04`
- No manager approval required for defect closure
- Self-resolution of critical defects

### VULN-03: A09 — Logging Failures (No Audit Trail)

**Severity:** Low  
**Location:** `InspectionService.java:21-30` — `updateInspectionResult()`  
**Lines:**
```java
// VULNERABILITY A09: Inspection log modifications lack audit logging
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A09`
- Inspection result updates are not logged
- Silent manipulation of QA reports

---

## Chained Attack: chain-01

**Chain Name:** Privilege Escalation → Silent Defect Closure → Undetected Quality Fraud  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Mass Assignment Escalation (A01 — Medium)

**Difficulty: EASY**

- Profile update accepts `role` parameter
- Escalate from WORKER to QA_MANAGER

### Link 2: Self-Approved Defect Closure (A04 — Medium)

**Difficulty: EASY**

- No manager approval required
- Close critical defects without oversight

### Link 3: Silent Inspection Tampering (A09 — Low)

**Difficulty: EASY**

- Pass failed inspections with no audit trail
- Undetectable quality fraud

---

## Summary

App-28 is a Spring Boot manufacturing QC system with mass assignment privilege escalation, missing defect closure approvals, and silent inspection tampering. Chain: escalate privilege → close defects → mute quality fraud.

**Overall Difficulty Score:** 2/5 (Easy-Medium)