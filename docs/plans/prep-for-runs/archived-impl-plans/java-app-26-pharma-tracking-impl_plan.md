# Implementation Plan — App 26: Pharmaceutical Drug Tracking

## 1. Overview

A Spring Boot application for tracking pharmaceutical drugs through the supply chain — from manufacturer to distributor to pharmacy. Manages drug batches, lot numbers, chain-of-custody records, and regulatory compliance checks.

**Target OWASP vulnerabilities:** A01 (Broken Access Control), A02 (Cryptographic Failures), A08 (Software & Data Integrity Failures)

---

## 2. Business Domain

**Pharmaceutical / Healthcare Supply Chain** — Used by drug manufacturers, wholesale distributors, pharmacy operators, and regulatory inspectors.

## 3. Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security |
| Database | H2 (embedded, in-memory) |
| Build | Maven |
| Containerisation | Docker |

---

## 4. Project Scaffold

### 4.1 Package Layout
```
src/main/java/com/pharma/tracking/
├── App26Application.java
├── config/
│   └── SecurityConfig.java
├── controller/
│   ├── AuthController.java
│   ├── DrugController.java
│   ├── BatchController.java
│   ├── CustodyController.java
│   └── InspectionController.java
├── model/
│   ├── Drug.java
│   ├── Batch.java
│   ├── CustodyRecord.java
│   ├── Inspection.java
│   └── User.java
├── repository/
│   ├── DrugRepository.java
│   ├── BatchRepository.java
│   ├── CustodyRecordRepository.java
│   └── InspectionRepository.java
├── service/
│   ├── DrugService.java
│   ├── BatchService.java
│   ├── CustodyService.java
│   ├── InspectionService.java
│   └── BatchImportService.java
└── dto/
    ├── DrugDTO.java
    ├── BatchDTO.java
    └── CustodyDTO.java
```

---

## 5. Database Schema

### Tables
- **drugs** — id, ndc_code, name, manufacturer, active_ingredient, schedule_class
- **batches** — id, drug_id, lot_number, manufacture_date, expiry_date, quantity, status (IN_TRANSIT/DELIVERED/RECALLED)
- **custody_records** — id, batch_id, from_entity, to_entity, transferred_at, signature_hash
- **inspections** — id, batch_id, inspector_id, result (PASS/FAIL), notes, inspected_at
- **users** — id, username, password_hash, role (MANUFACTURER/DISTRIBUTOR/PHARMACY/INSPECTOR), org_name

### Seed Data
- 10 drugs across schedules II–V
- 20+ batches with various statuses
- Chain-of-custody records for each batch
- 5+ inspection records
- Users across all 4 roles

---

## 6. Planned Vulnerabilities

### 6.1 VULNERABILITY A01 — IDOR on Batch Details
- **Location:** `BatchController.java` → `getBatchDetails()`
- **Mechanism:** `GET /api/batches/{id}` returns full batch details (including custody chain) for any batch ID without checking whether the requesting user's organisation is part of that batch's custody chain
- **CWE:** CWE-639

### 6.2 VULNERABILITY A02 — Weak Signature Hashing for Chain of Custody
- **Location:** `CustodyService.java` → `signTransfer()`
- **Mechanism:** Custody transfer signatures use MD5 hash of `batchId + timestamp` with no secret key — trivially forgeable
- **CWE:** CWE-328

### 6.3 VULNERABILITY A08 — Insecure Deserialization of Batch Import
- **Location:** `BatchImportService.java` → `importBatches()`
- **Mechanism:** Accepts Java-serialised objects from an uploaded file using `ObjectInputStream.readObject()` with no class whitelist — allows arbitrary code execution
- **CWE:** CWE-502

---

## 7. Chained Vulnerability Scenario

### Chain: "IDOR Batch Enumeration → Forged Custody Signature → Supply Chain Tampering"

A low-privilege distributor user exploits IDOR to enumerate all batch IDs, then forges custody transfer signatures to redirect drug shipments to an unauthorised destination.

| Step | Issue | Severity | OWASP |
|------|-------|----------|-------|
| 1 | IDOR on batch endpoint exposes all batch details | Medium | A01 |
| 2 | MD5 signatures are forgeable; attacker creates fake custody transfers | Medium | A02 |

**Impact:** `data_modification` — Attacker can insert fraudulent custody records, potentially diverting controlled substances.

---

## 8. Decoy Safe Patterns

- `DrugRepository` uses parameterised Spring Data JPA queries (safe)
- `InspectionController` properly checks that only users with INSPECTOR role can create inspection records via `@PreAuthorize("hasRole('INSPECTOR')")`
- Passwords stored with BCrypt (safe hashing — in contrast to the weak MD5 used for custody signatures)

---

## 9. Checklist

- [ ] Spring Boot project compiles and starts
- [ ] H2 database schema initialises correctly
- [ ] All REST endpoints functional
- [ ] IDOR on batch endpoint is exploitable
- [ ] MD5 custody signatures are forgeable
- [ ] Deserialization of batch import is exploitable
- [ ] Chain scenario is end-to-end exploitable
- [ ] Decoy patterns are in place
- [ ] `.vulns` manifest is complete and accurate
- [ ] README follows project template
- [ ] Dockerfile builds and runs
