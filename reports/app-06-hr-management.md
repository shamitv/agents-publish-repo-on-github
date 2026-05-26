# Audit Report: app-06 — Enterprise HR Management System

**Language:** Java (Spring Boot)  
**Business Domain:** HR / Enterprise  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR on Payroll)

**Severity:** High  
**Location:** `PayrollController.java:17-23` — `getPayroll()`  
**Lines:**
```java
// VULNERABILITY A01: Payroll endpoint returns salary data for any employee to any authenticated user without role or ownership check
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A01`
- Any authenticated user can view any employee's payroll
- No role or ownership validation

### VULN-02: A08 — Software Integrity (Java Deserialization)

**Severity:** Critical  
**Location:** `EmployeeImportService.java:18-26` — `importEmployees()`  
**Lines:**
```java
// VULNERABILITY A08: Bulk employee import uses ObjectInputStream.readObject() on untrusted upload without class filtering
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A08`
- Uses `ObjectInputStream.readObject()` on user-supplied data
- No class filtering, enabling arbitrary code execution

### VULN-03: A02 — Cryptographic Failures (Weak XOR Encryption)

**Severity:** High  
**Location:** `Employee.java:42-69` — `setRawSsn()`  
**Lines:**
```java
// VULNERABILITY A02: SSN encryption uses reversible XOR cipher with hard-coded key 0xDEADBEEF
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A02`
- XOR cipher with hardcoded key `0xDEADBEEF`
- Reversible encryption, trivially decrypted

---

## Chained Attack: chain-01

**Chain Name:** Credential Hash Harvest → Offline Crack → Payroll + SSN Exfiltration  
**Combined Impact:** Database Exfiltration  
**Overall Chain Difficulty: MEDIUM**

### Link 1: IDOR on Audit Endpoint (A01 — Medium)

**Difficulty: EASY**

- `GET /api/employees/{id}/audit` exposes password hash for any employee
- No role or ownership check

### Link 2: Weak Passwords in Seed Data (A02 — Low)

**Difficulty: EASY**

- Seed data uses short common passwords
- Hashes crackable offline with standard wordlists

### Link 3: IDOR on Payroll (A01 — High)

**Difficulty: EASY**

- Dumps payroll records and encrypted SSNs
- XOR key is hardcoded, trivially decryptable

---

## Summary

App-06 is a Spring Boot HR manager with IDOR on payroll, Java deserialization in employee import, and XOR-based SSN encryption. Chain: harvest hashes → crack offline → dump payroll data.

**Overall Difficulty Score:** 2/5 (Easy-Medium)