# Security Report: app-06 — Enterprise HR Management System

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-06-hr-management`

---

## Application Information
- **App ID:** app-06
- **Name:** Enterprise HR Management System
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | High | src/main/java/com/hr/controller/PayrollController.java | CWE-639 |
| V2 | A08 | Software and Data Integrity Failures | Critical | src/main/java/com/hr/service/EmployeeImportService.java | CWE-502 |
| V3 | A02 | Cryptographic Failures | High | src/main/java/com/hr/model/Employee.java | CWE-327 |
| V4 | A08 | Software and Data Integrity Failures | High | src/main/java/com/hr/messaging/PayrollAuditConsumer.java | CWE-917 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `src/main/java/com/hr/controller/PayrollController.java`:19-26 (method: `getPayroll`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Payroll endpoint returns salary data and encrypted SSNs for any employee to any authenticated user without role or ownership check

### VULN-02: A08 — Software and Data Integrity Failures

- **Severity:** Critical
- **Location:** `src/main/java/com/hr/service/EmployeeImportService.java`:17-26 (method: `importEmployees`)
- **CWE:** [CWE-502](https://cwe.mitre.org/data/definitions/502.html)

#### Description
Bulk employee import uses ObjectInputStream.readObject() on untrusted upload without class filtering

### VULN-03: A02 — Cryptographic Failures

- **Severity:** High
- **Location:** `src/main/java/com/hr/model/Employee.java`:52-87 (method: `getRawSsn`)
- **CWE:** [CWE-327](https://cwe.mitre.org/data/definitions/327.html)

#### Description
SSN encryption uses reversible XOR cipher with hard-coded key 0xDEADBEEF

### VULN-04: A08 — Software and Data Integrity Failures

- **Severity:** High
- **Location:** `src/main/java/com/hr/messaging/PayrollAuditConsumer.java`:15-18 (method: `consume`)
- **CWE:** [CWE-917](https://cwe.mitre.org/data/definitions/917.html)

#### Description
Kafka audit consumer logs externally supplied event content through Log4j 2.14.1


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Payroll IDOR → Weak SSN Encryption → DB Exfiltration

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Medium
- **Subtlety Tags:** 

#### Prerequisites
- None specified

#### Attack Narrative
A low-privilege employee iterates the payroll endpoint for other employee IDs, collects encrypted SSNs in each payroll response, then reverses the XOR encryption using the hardcoded key in the Employee model.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | GET /api/payroll/{employeeId} returns another employee's payroll record and encrypted SSN to any authenticated user | Medium | A01 | CWE-639 | src/main/java/com/hr/controller/PayrollController.java | `getPayroll` |
| 2 | The Employee model uses a hardcoded XOR key, allowing exposed encrypted SSNs to be decrypted offline | Medium | A02 | CWE-327 | src/main/java/com/hr/model/Employee.java | `getRawSsn` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/hr/config/SecurityConfig.java | BCryptPasswordEncoder with default strength — this is SAFE and should NOT be flagged |
| src/main/java/com/hr/repository/EmployeeRepository.java | Spring Data JPA parameterised queries — NOT injectable |
| src/main/java/com/hr/controller/PayrollController.java | Payroll report endpoint requires HR_ADMIN authorization and should not be flagged as an IDOR |
