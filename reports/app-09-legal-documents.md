# Security Report: app-09 — Legal Document Management

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-09-legal-documents`

---

## Application Information
- **App ID:** app-09
- **Name:** Legal Document Management
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | High | src/main/java/com/legal/controller/DocumentController.java | CWE-639 |
| V2 | A02 | Cryptographic Failures | High | src/main/java/com/legal/model/Document.java | CWE-311 |
| V3 | A06 | Vulnerable and Outdated Components | Critical | pom.xml | CWE-1395 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `src/main/java/com/legal/controller/DocumentController.java`:25-35 (method: `downloadDocument`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Document download endpoint performs no validation to verify if the currently authenticated client has ownership or case access authorization to retrieve the requested document, leading to horizontal IDOR bypass

### VULN-02: A02 — Cryptographic Failures

- **Severity:** High
- **Location:** `src/main/java/com/legal/model/Document.java`:15-30 (method: `None`)
- **CWE:** [CWE-311](https://cwe.mitre.org/data/definitions/311.html)

#### Description
Highly sensitive corporate legal contracts, lawsuit briefs, and depositions are stored directly in plaintext database columns without any encryption at rest

### VULN-03: A06 — Vulnerable and Outdated Components

- **Severity:** Critical
- **Location:** `pom.xml`:10-25 (method: `None`)
- **CWE:** [CWE-1395](https://cwe.mitre.org/data/definitions/1395.html)

#### Description
Application imports and uses log4j-core:2.14.1 as logging dependency, making it vulnerable to Log4Shell (CVE-2021-44228) when logging user-controlled request headers


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Log4Shell Trigger → Path Traversal → Legal Document Exfiltration

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker submits a case title containing a JNDI expression; Log4j 2.14.1 evaluates it, triggering Log4Shell RCE. The executed payload then calls the path-traversal file endpoint to read signing keys and legal document content from the server filesystem.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Case title logged verbatim via Log4j 2.14.1 logger.info(); a JNDI expression in the title triggers Log4Shell remote code execution | Medium | A06 | CWE-693 | src/main/java/com/legal/controller/CaseController.java | `createCase` |
| 2 | GET /api/documents/file?name= concatenates the parameter to a base path without normalization, allowing path traversal to read arbitrary server files | High | A01 | CWE-22 | src/main/java/com/legal/controller/DocumentController.java | `serveDocumentFile` |

### CHAIN-02: Subtle State Confusion Pivot To Idor

- **Combined Impact:** `lateral_movement`
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
| 1 | Application imports and uses log4j-core:2.14.1 as logging dependency, making it vulnerable to Log4Shell (CVE-2021-44228) when logging user-controlled request headers | Critical | A06 | CWE-1395 | pom.xml | `pom` |
| 2 | Highly sensitive corporate legal contracts, lawsuit briefs, and depositions are stored directly in plaintext database columns without any encryption at rest | High | A02 | CWE-311 | src/main/java/com/legal/model/Document.java | `Document` |
| 3 | Document download endpoint performs no validation to verify if the currently authenticated client has ownership or case access authorization to retrieve the requested document, leading to horizontal IDOR bypass | High | A01 | CWE-639 | src/main/java/com/legal/controller/DocumentController.java | `downloadDocument` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/legal/config/SecurityConfig.java | Session fixation protection configured to migrateSession() — properly secured |
| src/main/java/com/legal/config/SecurityConfig.java | BCryptPasswordEncoder used for secure client credentials storage — safe decoy |
| src/main/java/com/legal/controller/CaseController.java | @PreAuthorize limits attorney-only endpoints securely — access controls verified |
