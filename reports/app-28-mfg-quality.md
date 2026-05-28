# Security Report: app-28 — Manufacturing Quality Control

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-28-mfg-quality`

---

## Application Information
- **App ID:** app-28
- **Name:** Manufacturing Quality Control
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | High | src/main/java/com/manufacturing/qc/controller/AuthController.java | CWE-915 |
| V2 | A04 | Insecure Design | Medium | src/main/java/com/manufacturing/qc/controller/DefectController.java | CWE-841 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | src/main/java/com/manufacturing/qc/service/InspectionService.java | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `src/main/java/com/manufacturing/qc/controller/AuthController.java`:32-43 (method: `updateProfile`)
- **CWE:** [CWE-915](https://cwe.mitre.org/data/definitions/915.html)

#### Description
Mass assignment vulnerability on user profile update allows workers to escalate privilege to QA_MANAGER

### VULN-02: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `src/main/java/com/manufacturing/qc/controller/DefectController.java`:17-25 (method: `resolveDefect`)
- **CWE:** [CWE-841](https://cwe.mitre.org/data/definitions/841.html)

#### Description
Critical defect resolution workflow lacks formal manager approval check, allowing self-resolution

### VULN-03: A09 — Security Logging and Monitoring Failures

- **Severity:** Low
- **Location:** `src/main/java/com/manufacturing/qc/service/InspectionService.java`:21-30 (method: `updateInspectionResult`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Inspection log modifications lack audit logging, permitting silent changes to QA reports


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Privilege Escalation → Silent Defect Closure → Undetected Quality Fraud

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker registers as WORKER, updates profile via mass assignment to gain QA_MANAGER role, marks critical defects as resolved, and changes failed inspection records to passed without any audit trails.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Mass assignment allows escalating privilege from WORKER to QA_MANAGER. | Medium | A01 | CWE-915 | src/main/java/com/manufacturing/qc/controller/AuthController.java | `updateProfile` |
| 2 | Lack of defect closure approval allows self-resolution of major defects. | Medium | A04 | CWE-841 | src/main/java/com/manufacturing/qc/controller/DefectController.java | `resolveDefect` |
| 3 | No logging on inspection modifications allows silent data tampering. | Low | A09 | CWE-778 | src/main/java/com/manufacturing/qc/service/InspectionService.java | `updateInspectionResult` |

### CHAIN-02: Subtle State Confusion Pivot To Idor

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy` `secondary_chain`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Inspection log modifications lack audit logging, permitting silent changes to QA reports | Low | A09 | CWE-778 | src/main/java/com/manufacturing/qc/service/InspectionService.java | `updateInspectionResult` |
| 2 | Critical defect resolution workflow lacks formal manager approval check, allowing self-resolution | Medium | A04 | CWE-841 | src/main/java/com/manufacturing/qc/controller/DefectController.java | `resolveDefect` |
| 3 | Mass assignment vulnerability on user profile update allows workers to escalate privilege to QA_MANAGER | High | A01 | CWE-915 | src/main/java/com/manufacturing/qc/controller/AuthController.java | `updateProfile` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/manufacturing/qc/controller/ProductController.java | getProducts endpoint is properly secured via PreAuthorize QA_MANAGER check |
| src/main/java/com/manufacturing/qc/config/SecurityConfig.java | Strong password encryption (BCrypt) used for storing user credentials |
