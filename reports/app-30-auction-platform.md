# Security Report: app-30 — Auction Platform

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-30-auction-platform`

---

## Application Information
- **App ID:** app-30
- **Name:** Auction Platform
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A04 | Insecure Design | Medium | src/main/java/com/auction/platform/service/BidService.java | CWE-362 |
| V2 | A07 | Identification and Authentication Failures | High | src/main/java/com/auction/platform/model/User.java | CWE-256 |
| V3 | A08 | Software and Data Integrity Failures | Medium | src/main/java/com/auction/platform/controller/WebhookController.java | CWE-345 |

---

## Standalone Vulnerabilities

### VULN-01: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `src/main/java/com/auction/platform/service/BidService.java`:21-47 (method: `placeBid`)
- **CWE:** [CWE-362](https://cwe.mitre.org/data/definitions/362.html)

#### Description
Bidding workflow suffers from race conditions allowing multiple concurrent lower bids to win or execute due to lack of db locks

### VULN-02: A07 — Identification and Authentication Failures

- **Severity:** High
- **Location:** `src/main/java/com/auction/platform/model/User.java`:12-19 (method: `n/a`)
- **CWE:** [CWE-256](https://cwe.mitre.org/data/definitions/256.html)

#### Description
User passwords are saved in plaintext directly in the database without any hashing

### VULN-03: A08 — Software and Data Integrity Failures

- **Severity:** Medium
- **Location:** `src/main/java/com/auction/platform/controller/WebhookController.java`:21-41 (method: `handlePaymentWebhook`)
- **CWE:** [CWE-345](https://cwe.mitre.org/data/definitions/345.html)

#### Description
Webhook listener accepts arbitrary payloads without verifying payment signatures, allowing forged payment notifications


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Plaintext Password Dump → Forged Webhook → Transaction Fraud

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker exfiltrates plaintext passwords via database access or a separate SQL injection, logs in as a seller to list items, and forges unsigned payment webhooks directly to the server to fake payment completion without transfer of actual money.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Plaintext passwords stored directly in the DB allows easy credential theft. | Low | A07 | CWE-256 | src/main/java/com/auction/platform/model/User.java | `n/a` |
| 2 | Webhook endpoint accepts payment notifications without signature verification. | Medium | A08 | CWE-345 | src/main/java/com/auction/platform/controller/WebhookController.java | `handlePaymentWebhook` |

### CHAIN-02: Subtle Ssrf Pivot To State Confusion

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
| 1 | Webhook listener accepts arbitrary payloads without verifying payment signatures, allowing forged payment notifications | Medium | A08 | CWE-345 | src/main/java/com/auction/platform/controller/WebhookController.java | `handlePaymentWebhook` |
| 2 | User passwords are saved in plaintext directly in the database without any hashing | High | A07 | CWE-256 | src/main/java/com/auction/platform/model/User.java | `n/a` |
| 3 | Bidding workflow suffers from race conditions allowing multiple concurrent lower bids to win or execute due to lack of db locks | Medium | A04 | CWE-362 | src/main/java/com/auction/platform/service/BidService.java | `placeBid` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/auction/platform/controller/ListingController.java | getListings endpoint is properly secured restricting list lookups to users with SELLER roles |
| src/main/java/com/auction/platform/service/WalletService.java | deductBalance utilizes serializable transactional isolation levels to avoid balance race conditions |
