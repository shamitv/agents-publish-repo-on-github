# Vulnerability Inventory — App 06 (Enterprise HR Management System)

## Purpose

This document enumerates every intentionally planted vulnerability, chain link, and decoy in the **current** app-06 codebase. It serves as a **no-touch zone** reference during the upgrade — no implementation step may remove, weaken, or fix any item listed here.

---

## App Profile

| Property | Value |
|----------|-------|
| App ID | `app-06` |
| Language | Java |
| Framework | Spring Boot 3.2.5 |
| Build tool | Maven |
| Source file count | 41 (29 Java classes) |
| Complexity rating | 4 — Complex |
| Entry point | `App06Application.java` |
| Manifest | `.vulns` |

---

## Standalone Vulnerabilities

### VULN-01 — IDOR on Payroll Lookup

| Field | Value |
|-------|-------|
| OWASP | **A01** — Broken Access Control |
| CWE | CWE-639 |
| File | `src/main/java/com/hr/controller/PayrollController.java` |
| Method | `getPayroll` |
| Severity | High |
| Source Comment | `// VULNERABILITY A01: Payroll lookup lacks role or ownership checks.` |
| Source Comment | `// CHAIN LINK 1 (chain-01): Any authenticated employee can request another employee payroll profile by ID.` |
| Description | `GET /api/payroll/{employeeId}` returns another employee's payroll record (including encrypted SSN) to any authenticated user without ownership or role checks. |

### VULN-02 — Weak XOR Encryption for SSNs

| Field | Value |
|-------|-------|
| OWASP | **A02** — Cryptographic Failures |
| CWE | CWE-327 |
| File | `src/main/java/com/hr/model/Employee.java` |
| Method | `setRawSsn` / `getRawSsn` |
| Severity | High |
| Source Comment | `// VULNERABILITY A02: SSNs use reversible XOR with a hardcoded key.` |
| Source Comment | `// CHAIN LINK 2 (chain-01): The hardcoded XOR key decrypts SSNs exposed through payroll records.` |
| Description | Employee SSNs are encrypted with a reversible XOR cipher using hardcoded key `0xDEADBEEF`. Any attacker who obtains encrypted SSNs (via VULN-01) can decrypt them. |

### VULN-03 — Unsafe Java Deserialization in Employee Import

| Field | Value |
|-------|-------|
| OWASP | **A08** — Software and Data Integrity Failures |
| CWE | CWE-502 |
| File | `src/main/java/com/hr/service/EmployeeImportService.java` |
| Method | `importEmployees` |
| Severity | Critical |
| Source Comment | `// VULNERABILITY A08: Deserializes untrusted employee import uploads without a class allowlist.` |
| Description | The employee import endpoint deserializes Java objects from an `InputStream` using `ObjectInputStream.readObject()` without a class allowlist, enabling arbitrary code execution. |

### VULN-04 — Log4Shell in Payroll Audit Consumer

| Field | Value |
|-------|-------|
| OWASP | **A08** — Software and Data Integrity Failures |
| CWE | CWE-917 |
| File | `src/main/java/com/hr/messaging/PayrollAuditConsumer.java` |
| Method | `consume` |
| Severity | High |
| Source Comment | `// VULNERABILITY A08: Logs externally supplied audit event content through Log4j 2.14.1.` |
| Description | The Kafka audit consumer logs event payloads via Log4j 2.14.1 using string concatenation (`LOGGER.info("..." + event)`), enabling Log4Shell JNDI injection (CVE-2021-44228). |

---

## Unannotated Weakness (formalized during upgrade)

### AUDIT-01 — Employee Audit Endpoint Exposes Password Hash

| Field | Value |
|-------|-------|
| OWASP | **A01** / A05 — Broken Access Control / Security Misconfiguration |
| CWE | CWE-200 |
| File | `src/main/java/com/hr/controller/EmployeeController.java` |
| Method | `getEmployeeAudit` |
| Severity | Medium |
| Annotation | **NONE** — currently unannotated. To be formalized in Phase 2. |
| Description | `GET /api/employees/{id}/audit` returns the `passwordHash` field to any authenticated user for any employee ID, with no `@PreAuthorize` check. Enables offline password cracking. |

---

## Chained Vulnerability Scenarios

### chain-01: Payroll IDOR → Weak SSN Encryption → DB Exfiltration

**Combined Impact**: `db_exfiltration`

| Step | OWASP | CWE | File | Method | Severity | Source Comment |
|------|-------|-----|------|--------|----------|----------------|
| 1 | A01 | CWE-639 | `controller/PayrollController.java` | `getPayroll` | Medium | `// CHAIN LINK 1 (chain-01): Any authenticated employee can request another employee payroll profile by ID.` |
| 2 | A02 | CWE-327 | `model/Employee.java` | `getRawSsn` | Medium | `// CHAIN LINK 2 (chain-01): The hardcoded XOR key decrypts SSNs exposed through payroll records.` |

**Attack narrative**: A low-privilege employee iterates `GET /api/payroll/{employeeId}` for other employee IDs, collects encrypted SSNs from each payroll response, then reverses the XOR encryption using the hardcoded `0xDEADBEEF` key in the Employee model to recover plaintext SSNs.

---

## Decoy Patterns (Safe Code Near Vulnerable Areas)

### DECOY-01 — BCrypt Password Encoder

| Field | Value |
|-------|-------|
| File | `src/main/java/com/hr/config/SecurityConfig.java` |
| Pattern | `BCryptPasswordEncoder` with default strength |
| Why it looks vulnerable | Co-located with security config that permits unauthenticated access to some endpoints |
| Why it is safe | BCrypt is industry-standard password hashing; default strength provides adequate work factor |

### DECOY-02 — Parameterized JPA Queries

| Field | Value |
|-------|-------|
| File | `src/main/java/com/hr/repository/EmployeeRepository.java` |
| Pattern | Spring Data JPA derived queries |
| Why it looks vulnerable | Some other endpoints use raw queries or lack parameterization |
| Why it is safe | Spring Data JPA derived queries are automatically parameterized and not injectable |

### DECOY-03 — Protected Payroll Report Endpoint

| Field | Value |
|-------|-------|
| File | `src/main/java/com/hr/controller/PayrollController.java` |
| Method | `getPayrollReport` |
| Pattern | Requires `HR_ADMIN` role |
| Why it looks vulnerable | Same controller as the vulnerable `getPayroll()` IDOR endpoint |
| Why it is safe | `@PreAuthorize("hasRole('HR_ADMIN')")` protects the report; role check is enforced |

---

## No-Touch Files During Upgrade

These files contain vulnerability annotations and **must not be modified** in ways that weaken or remove the vulnerabilities:

| File | Annotations | Action Allowed? |
|------|------------|-----------------|
| `controller/PayrollController.java` | VULNERABILITY A01, CHAIN LINK 1 (chain-01) | No direct modification |
| `model/Employee.java` | VULNERABILITY A02, CHAIN LINK 2 (chain-01) | No direct modification |
| `service/EmployeeImportService.java` | VULNERABILITY A08 (deserialization) | No direct modification |
| `messaging/PayrollAuditConsumer.java` | VULNERABILITY A08 (Log4j) | No direct modification |
| `config/SecurityConfig.java` | DECOY-01 (BCrypt) | No direct modification |
| `repository/EmployeeRepository.java` | DECOY-02 (parameterized queries) | No direct modification |
| `controller/PayrollController.java` | DECOY-03 (protected report) | No direct modification |
| `.vulns` | Ground truth manifest | Update to add entries only; never delete |

**Rule**: If a refactoring step must touch these files, the vulnerability code and comments must be preserved verbatim at the new location, and `.vulns` locations updated accordingly.

---

## OWASP Coverage Gap Analysis

Current coverage vs. OWASP Top 10: 2021:

| OWASP | Category | Covered? | How |
|-------|----------|----------|-----|
| A01 | Broken Access Control | Yes | VULN-01, Chain Link 1 |
| A02 | Cryptographic Failures | Yes | VULN-02, Chain Link 2 |
| A03 | Injection | **No** | **Target for this upgrade (Phase 3)** |
| A04 | Insecure Design | **No** | **Target for this upgrade (Phase 2)** |
| A05 | Security Misconfiguration | **No** | Covered by upgrade (audit endpoint formalized) |
| A06 | Vulnerable & Outdated Components | **No** | **Target for future expansion** |
| A07 | Identification & Auth Failures | **No** | **Target for this upgrade (Phase 4 — chain)** |
| A08 | Software & Data Integrity | Yes | VULN-03, VULN-04 |
| A09 | Security Logging & Monitoring | **No** | **Target for this upgrade (Phase 3)** |
| A10 | SSRF | **No** | **Target for future expansion** |

**Upgrade strategy**: Phase 2→A04, Phase 3→A03+A09, Phase 4→A07 (chain) to reach 7/10 coverage.
