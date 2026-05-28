# Security Report: app-26 — Pharmaceutical Drug Tracking

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-26-pharma-tracking`

---

## Application Information
- **App ID:** app-26
- **Name:** Pharmaceutical Drug Tracking
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/main/java/com/pharma/tracking/controller/BatchController.java | CWE-639 |
| V2 | A02 | Cryptographic Failures | Medium | src/main/java/com/pharma/tracking/service/CustodyService.java | CWE-328 |
| V3 | A08 | Software and Data Integrity Failures | Critical | src/main/java/com/pharma/tracking/service/BatchImportService.java | CWE-502 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/main/java/com/pharma/tracking/controller/BatchController.java`:21-27 (method: `getBatchDetails`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
IDOR on batch lookup allows any authenticated user to view details of any batch without checks

### VULN-02: A02 — Cryptographic Failures

- **Severity:** Medium
- **Location:** `src/main/java/com/pharma/tracking/service/CustodyService.java`:18-31 (method: `generateCustodySignature`)
- **CWE:** [CWE-328](https://cwe.mitre.org/data/definitions/328.html)

#### Description
Weak MD5 hashing algorithm without a secret key is used to sign custody transfers, allowing forged signatures

### VULN-03: A08 — Software and Data Integrity Failures

- **Severity:** Critical
- **Location:** `src/main/java/com/pharma/tracking/service/BatchImportService.java`:17-26 (method: `importBatch`)
- **CWE:** [CWE-502](https://cwe.mitre.org/data/definitions/502.html)

#### Description
Insecure Java deserialization on batch import endpoint allows execution of arbitrary code via malicious payloads


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: IDOR Batch Enumeration → Forged Custody Signature → Supply Chain Tampering

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker logs in, uses IDOR to search all batch shipment details, and generates a fake MD5 custody signature to divert or inject custom chain-of-custody transfer entries.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | IDOR batch endpoint leaks details of batches not belonging to the current user's organization. | Medium | A01 | CWE-639 | src/main/java/com/pharma/tracking/controller/BatchController.java | `getBatchDetails` |
| 2 | Weak custody signature algorithm allows generating valid transfer signatures off-platform. | Medium | A02 | CWE-328 | src/main/java/com/pharma/tracking/service/CustodyService.java | `generateCustodySignature` |

### CHAIN-02: Subtle Deserialization Pivot To Idor

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
| 1 | Insecure Java deserialization on batch import endpoint allows execution of arbitrary code via malicious payloads | Critical | A08 | CWE-502 | src/main/java/com/pharma/tracking/service/BatchImportService.java | `importBatch` |
| 2 | Weak MD5 hashing algorithm without a secret key is used to sign custody transfers, allowing forged signatures | Medium | A02 | CWE-328 | src/main/java/com/pharma/tracking/service/CustodyService.java | `generateCustodySignature` |
| 3 | IDOR on batch lookup allows any authenticated user to view details of any batch without checks | Medium | A01 | CWE-639 | src/main/java/com/pharma/tracking/controller/BatchController.java | `getBatchDetails` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/pharma/tracking/config/SecurityConfig.java | Strong password encryption (BCrypt) used for storing user credentials |
| src/main/java/com/pharma/tracking/controller/InspectionController.java | createInspection endpoint restricts creation of inspection logs to the INSPECTOR role |
