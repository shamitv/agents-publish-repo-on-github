# Audit Report: app-26 — Pharmaceutical Drug Tracking

**Language:** Java (Spring Boot)  
**Business Domain:** Pharma / Supply Chain  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR on Batch Details)

**Severity:** Medium  
**Location:** `BatchController.java:21-27` — `getBatchDetails()`  
**Lines:**
```java
// VULNERABILITY A01: IDOR on batch lookup allows any authenticated user to view any batch's details
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A01`
- Any authenticated user can view any batch's details
- No organization ownership check

### VULN-02: A02 — Cryptographic Failures (Weak MD5 Signature)

**Severity:** Medium  
**Location:** `CustodyService.java:18-31` — `generateCustodySignature()`  
**Lines:**
```java
// VULNERABILITY A02: Weak MD5 hashing algorithm without secret key used to sign custody transfers
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A02`
- MD5 used for signing without a secret key
- Forged signatures trivially generated

### VULN-03: A08 — Software Integrity (Java Deserialization)

**Severity:** Critical  
**Location:** `BatchImportService.java:17-26` — `importBatch()`  
**Lines:**
```java
// VULNERABILITY A08: Insecure Java deserialization on batch import allows arbitrary code execution
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A08`
- `ObjectInputStream.readObject()` on untrusted input
- No class filtering, enabling RCE

---

## Chained Attack: chain-01

**Chain Name:** IDOR Batch Enumeration → Forged Custody Signature → Supply Chain Tampering  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: MEDIUM**

### Link 1: IDOR on Batch Endpoint (A01 — Medium)

**Difficulty: EASY**

- Leaks shipment details from other organizations

### Link 2: Weak Custody Signature (A02 — Medium)

**Difficulty: EASY**

- MD5 without secret key allows off-platform signature generation
- Forged custody transfer entries injected

---

## Summary

App-26 is a Spring Boot pharma tracker with IDOR on batch details, weak MD5 custody signatures, and Java deserialization in batch import. Chain: enumerate batches → forge signatures → tamper with supply chain.

**Overall Difficulty Score:** 2/5 (Easy-Medium)