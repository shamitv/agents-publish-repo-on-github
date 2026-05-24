# Audit Report: app-09 — Legal Document Management

**Language:** Java (Spring Boot)  
**Business Domain:** Legal / Document Management  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR on Document Download)

**Severity:** High  
**Location:** `DocumentController.java:25-35` — `downloadDocument()`  
**Lines:**
```java
// VULNERABILITY A01: Document download endpoint performs no ownership or case access validation
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A01`
- No validation that caller owns or is authorized for the document
- Horizontal IDOR on any document

### VULN-02: A02 — Cryptographic Failures (Plaintext Document Storage)

**Severity:** High  
**Location:** `Document.java:15-30`  
**Lines:**
```java
// VULNERABILITY A02: Highly sensitive legal documents stored in plaintext without encryption at rest
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A02`
- Contracts, lawsuits, and depositions stored in plaintext
- No encryption at rest

### VULN-03: A06 — Vulnerable Components (Log4j 2.14.1)

**Severity:** Critical  
**Location:** `pom.xml:10-25`  
**Lines:**
```xml
<!-- VULNERABILITY A06: Application imports log4j-core:2.14.1 — vulnerable to Log4Shell (CVE-2021-44228) -->
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A06`
- Log4j 2.14.1 pinned in dependencies
- User-controlled request headers get logged, triggering RCE

---

## Chained Attack: chain-01

**Chain Name:** Log4Shell Trigger → Path Traversal → Legal Document Exfiltration  
**Combined Impact:** Lateral Movement  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Log4Shell via Case Title (A06 — Medium)

**Difficulty: MEDIUM**

- Case title containing JNDI expression triggers Log4Shell RCE
- JNDI expression in logger.info() evaluates the expression

### Link 2: Path Traversal (A01 — High)

**Difficulty: EASY**

- `GET /api/documents/file?name=` concatenates param to base path
- No normalization, allows reading arbitrary server files

---

## Summary

App-09 is a Spring Boot legal document manager with IDOR, plaintext document storage, and Log4j 2.14.1. Chain: JNDI injection → path traversal → document exfiltration.

**Overall Difficulty Score:** 2/5 (Easy-Medium)