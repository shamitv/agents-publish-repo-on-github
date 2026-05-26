# Security Report: app-10 — Telecom Billing Platform

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-10-telecom-billing`

---

## Application Information
- **App ID:** app-10
- **Name:** Telecom Billing Platform
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | High | src/main/java/com/telecom/billing/controller/UsageController.java | CWE-89 |
| V2 | A04 | Insecure Design | Medium | src/main/java/com/telecom/billing/service/PaymentService.java | CWE-799 |
| V3 | A01 | Broken Access Control | Medium | src/main/java/com/telecom/billing/controller/AdminController.java | CWE-862 |
| V4 | A04 | Insecure Design | Medium | src/main/java/com/telecom/billing/controller/AdminController.java | CWE-840 |
| V5 | A09 | Security Logging and Monitoring Failures | Low | src/main/java/com/telecom/billing/controller/AdminController.java | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** High
- **Location:** `src/main/java/com/telecom/billing/controller/UsageController.java`:23-28 (method: `getUsageByDateRange`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
Usage search builds native SQL with user-controlled date values.

### VULN-02: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `src/main/java/com/telecom/billing/service/PaymentService.java`:18-32 (method: `processPayment`)
- **CWE:** [CWE-799](https://cwe.mitre.org/data/definitions/799.html)

#### Description
Payment processing lacks replay, idempotency, and rate-limit checks.

### VULN-03: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/main/java/com/telecom/billing/controller/AdminController.java`:37-45 (method: `updatePlanRate`)
- **CWE:** [CWE-862](https://cwe.mitre.org/data/definitions/862.html)

#### Description
Billing-admin plan rate endpoint accepts low-privilege CUSTOMER users.

### VULN-04: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `src/main/java/com/telecom/billing/controller/AdminController.java`:47-50 (method: `updatePlanRate`)
- **CWE:** [CWE-840](https://cwe.mitre.org/data/definitions/840.html)

#### Description
Plan pricing accepts caller-controlled negative or arbitrary custom rates.

### VULN-05: A09 — Security Logging and Monitoring Failures

- **Severity:** Low
- **Location:** `src/main/java/com/telecom/billing/controller/AdminController.java`:52-54 (method: `updatePlanRate`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Plan rate changes are persisted without publishing an audit event.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Weak Billing Admin Auth → Unvalidated Custom Rate → Missing Audit Logs → Data Modification

- **Combined Impact:** `data_modification`
- **Difficulty:** Medium
- **Subtlety Tags:** 

#### Prerequisites
- None specified

#### Attack Narrative
A low-privilege customer reaches a billing-admin pricing endpoint, submits an arbitrary negative plan rate, and the pricing mutation is saved without an audit event.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Plan rate endpoint authorizes CUSTOMER users for billing-admin functionality. | Medium | A01 | CWE-862 | src/main/java/com/telecom/billing/controller/AdminController.java | `updatePlanRate` |
| 2 | Caller-controlled custom rates, including negative values, are written directly to plan pricing. | Medium | A04 | CWE-840 | src/main/java/com/telecom/billing/controller/AdminController.java | `updatePlanRate` |
| 3 | The pricing mutation bypasses the available billing audit producer. | Low | A09 | CWE-778 | src/main/java/com/telecom/billing/controller/AdminController.java | `updatePlanRate` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/telecom/billing/config/SecurityConfig.java | BCryptPasswordEncoder is used for customer passwords and should not be flagged. |
| src/main/java/com/telecom/billing/controller/CustomerController.java | Customer profile endpoint checks principal ownership or admin identity before returning profile details. |
| src/main/java/com/telecom/billing/messaging/BillingAuditProducer.java | Audit producer is available for safe workflows; the vulnerability is the pricing endpoint bypassing it. |
