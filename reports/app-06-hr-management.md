# Audit Report: app-06 — Enterprise HR Management System

**Language:** Java (Spring Boot)  
**Business Domain:** Human Resources / Payroll  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (Payroll IDOR)

**Severity:** High  
**Location:** `PayrollController.java:17-23` — `getPayroll()`  
**Description:** Payroll endpoint returns salary/SSN data for any employee to any authenticated user without role or ownership check.

**Difficulty: EASY**

- No `@PreAuthorize` annotation checking ownership or role
- Accepts employee ID as path parameter without verifying against authenticated user
- Any logged-in user can access any employee's payroll

### VULN-02: A08 — Insecure Deserialization

**Severity:** Critical  
**Location:** `EmployeeImportService.java:18-26` — `importEmployees()`  
**Description:** Uses `ObjectInputStream.readObject()` on untrusted file upload without any class filtering.

**Difficulty: MEDIUM**

- Requires knowledge of Java deserialization gadget chains
- No allowlist/denylist on deserialized classes
- Must craft a malicious serialized object

### VULN-03: A02 — XOR "Encryption" with Hardcoded Key

**Severity:** High  
**Location:** `Employee.java:42-69` — `setRawSsn()`  
**Description:** SSN "encrypted" using XOR cipher with hardcoded key `0xDEADBEEF`.

**Difficulty: EASY**

- XOR is trivially reversible (XOR twice with same key returns plaintext)
- Key `0xDEADBEEF` is hardcoded and visible in source
- Comment likely describes this as "encryption" but it's obfuscation at best

---

## Chained Attack: chain-01

**Chain Name:** Credential Hash Harvest → Offline Crack → Payroll + SSN Exfiltration  
**Combined Impact:** Database Exfiltration (SSNs, salaries)  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Audit Endpoint Leaks Password Hashes (A01 — Medium)

**Location:** `EmployeeController.java` — `getEmployeeAudit()`  
**Description:** Any authenticated user can access `/api/employees/{id}/audit` which returns `passwordHash` for any employee.

### Link 2: Weak Seed Passwords (A02 — Low)

**Location:** `DataInitializer.java` — `seed()`  
**Description:** Seed users have short common passwords. Hashes crackable offline with wordlist.

### Link 3: Payroll IDOR (A01 — High)

**Location:** `PayrollController.java` — `getPayroll()`  
**Description:** After cracking an HR admin password, dump all payroll records and decrypt SSNs using the hardcoded XOR key.

---

## Summary

App-06 combines Java deserialization (a uniquely Java-specific vulnerability) with IDOR and weak crypto. The XOR decoy is particularly noteworthy — it looks like encryption but is trivially reversible. Chain requires offline cracking which elevates difficulty moderately.

**Overall Difficulty Score:** 2/5 (Medium — deserialization requires gadget chain knowledge)