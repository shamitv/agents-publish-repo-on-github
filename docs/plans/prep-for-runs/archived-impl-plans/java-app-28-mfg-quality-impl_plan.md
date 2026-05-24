# Implementation Plan — App 28: Manufacturing Quality Control

## 1. Overview

A Spring Boot quality control application for a manufacturing facility. Manages product inspections, defect tracking, quality metrics, and compliance reporting. Workers submit inspection results; managers review and approve corrective actions.

**Target OWASP vulnerabilities:** A01 (Broken Access Control), A04 (Insecure Design), A09 (Security Logging & Monitoring Failures)

---

## 2. Business Domain

**Manufacturing / Quality Assurance** — Used by production line workers, quality inspectors, QA managers, and compliance officers.

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
src/main/java/com/manufacturing/qc/
├── App28Application.java
├── config/
│   └── SecurityConfig.java
├── controller/
│   ├── AuthController.java
│   ├── InspectionController.java
│   ├── DefectController.java
│   ├── ProductController.java
│   └── ReportController.java
├── model/
│   ├── Product.java
│   ├── Inspection.java
│   ├── Defect.java
│   ├── CorrectiveAction.java
│   └── User.java
├── repository/
│   ├── ProductRepository.java
│   ├── InspectionRepository.java
│   ├── DefectRepository.java
│   └── CorrectiveActionRepository.java
├── service/
│   ├── InspectionService.java
│   ├── DefectService.java
│   ├── ProductService.java
│   └── ReportService.java
└── dto/
    ├── InspectionDTO.java
    ├── DefectDTO.java
    └── ReportDTO.java
```

---

## 5. Database Schema

### Tables
- **products** — id, sku, name, production_line, category, specifications_json
- **inspections** — id, product_id, inspector_id, result (PASS/FAIL/CONDITIONAL), notes, inspected_at
- **defects** — id, inspection_id, defect_type, severity (MINOR/MAJOR/CRITICAL), description, photo_url
- **corrective_actions** — id, defect_id, assigned_to, description, status (OPEN/IN_PROGRESS/RESOLVED), due_date, resolved_at
- **users** — id, username, password_hash, role (WORKER/INSPECTOR/QA_MANAGER/COMPLIANCE), badge_number

### Seed Data
- 30 products across 3 production lines
- 50+ inspection records
- 20 defect records with varying severities
- 10 corrective actions
- Users across all 4 roles

---

## 6. Planned Vulnerabilities

### 6.1 VULNERABILITY A01 — Privilege Escalation via Role Parameter
- **Location:** `AuthController.java` → `updateProfile()`
- **Mechanism:** `PUT /api/users/profile` accepts a `role` field in the request body — a WORKER can set their own role to `QA_MANAGER` by including `"role": "QA_MANAGER"` in the update payload (mass assignment)
- **CWE:** CWE-269

### 6.2 VULNERABILITY A04 — No Approval Workflow for Critical Defect Resolution
- **Location:** `DefectController.java` → `resolveDefect()`
- **Mechanism:** Any user can mark a CRITICAL defect as RESOLVED without manager approval — in a real manufacturing system, critical defects require a formal review and sign-off process before closure
- **CWE:** CWE-841

### 6.3 VULNERABILITY A09 — No Logging of Inspection Result Changes
- **Location:** `InspectionService.java` → `updateInspectionResult()`
- **Mechanism:** When an inspection result is changed from FAIL to PASS (or vice versa), no audit log is created — an insider can silently flip inspection results to pass defective products
- **CWE:** CWE-778

---

## 7. Chained Vulnerability Scenario

### Chain: "Privilege Escalation → Silent Defect Closure → Undetected Quality Fraud"

A production worker escalates their privileges to QA Manager, then marks critical defects as resolved without any audit trail, allowing defective products to ship.

| Step | Issue | Severity | OWASP |
|------|-------|----------|-------|
| 1 | Mass assignment allows role change from WORKER to QA_MANAGER | Medium | A01 |
| 2 | Critical defects can be resolved without approval | Medium | A04 |
| 3 | No audit logging on inspection result changes | Low | A09 |

**Impact:** `data_modification` — Defective products pass quality control without any record of tampering.

---

## 8. Decoy Safe Patterns

- `ProductController.create()` uses `@PreAuthorize("hasRole('QA_MANAGER')")` and a `ProductDTO` that does not bind sensitive fields (safe — proper role check)
- `InspectionRepository` uses parameterised queries for all lookups (safe)
- `ReportController.generateComplianceReport()` includes comprehensive logging with timestamps and user IDs (safe — contrasts with missing logging elsewhere)

---

## 9. Checklist

- [ ] Spring Boot project compiles and starts
- [ ] H2 database schema initialises correctly
- [ ] All REST endpoints functional
- [ ] Mass assignment role escalation is exploitable
- [ ] Critical defect resolution lacks approval workflow
- [ ] Inspection result changes produce no audit logs
- [ ] Chain scenario is end-to-end exploitable
- [ ] Decoy patterns are in place
- [ ] `.vulns` manifest is complete and accurate
- [ ] README follows project template
- [ ] Dockerfile builds and runs
