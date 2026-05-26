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

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `src/main/java/com/hr/controller/PayrollController.java`:17-23 (method: `getPayroll`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Payroll endpoint returns salary data for any employee to any authenticated user without role or ownership check

### VULN-02: A08 — Software and Data Integrity Failures

- **Severity:** Critical
- **Location:** `src/main/java/com/hr/service/EmployeeImportService.java`:18-26 (method: `importEmployees`)
- **CWE:** [CWE-502](https://cwe.mitre.org/data/definitions/502.html)

#### Description
Bulk employee import uses ObjectInputStream.readObject() on untrusted upload without class filtering

### VULN-03: A02 — Cryptographic Failures

- **Severity:** High
- **Location:** `src/main/java/com/hr/model/Employee.java`:42-69 (method: `setRawSsn`)
- **CWE:** [CWE-327](https://cwe.mitre.org/data/definitions/327.html)

#### Description
SSN encryption uses reversible XOR cipher with hard-coded key 0xDEADBEEF


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Credential Hash Harvest → Offline Crack → Payroll + SSN Exfiltration

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
A low-privilege employee iterates the audit endpoint to collect password hashes for all employees, cracks the hashes offline using a wordlist attack, re-authenticates as an HR Admin, then dumps all payroll records and decrypts SSNs using the hardcoded XOR key.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | GET /api/employees/{id}/audit exposes passwordHash for any employee to any authenticated user — no role or ownership check | Medium | A01 | CWE-639 | src/main/java/com/hr/controller/EmployeeController.java | `getEmployeeAudit` |
| 2 | Seed data uses short common passwords; hashes crackable offline with a standard wordlist, providing access to higher-privilege accounts | Low | A02 | CWE-521 | src/main/java/com/hr/config/DataInitializer.java | `seed` |
| 3 | Payroll endpoint returns salary and encrypted SSN for any employee to any authenticated session without role or ownership validation | High | A01 | CWE-639 | src/main/java/com/hr/controller/PayrollController.java | `getPayroll` |

### CHAIN-02: Subtle Crypto Pivot To Idor

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy` `direct_data_flow` `secondary_chain`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | SSN encryption uses reversible XOR cipher with hard-coded key 0xDEADBEEF | High | A02 | CWE-327 | src/main/java/com/hr/model/Employee.java | `setRawSsn` |
| 2 | Bulk employee import uses ObjectInputStream.readObject() on untrusted upload without class filtering | Critical | A08 | CWE-502 | src/main/java/com/hr/service/EmployeeImportService.java | `importEmployees` |
| 3 | Payroll endpoint returns salary data for any employee to any authenticated user without role or ownership check | High | A01 | CWE-639 | src/main/java/com/hr/controller/PayrollController.java | `getPayroll` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/hr/config/SecurityConfig.java | BCryptPasswordEncoder with default strength — this is SAFE and should NOT be flagged |
| src/main/java/com/hr/repository/EmployeeRepository.java | Spring Data JPA parameterised queries — NOT injectable |
