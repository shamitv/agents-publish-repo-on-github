# Security Report: app-12 — Crypto Wallet Service

**Language:** Typescript (Nestjs)
**Directory:** `apps/typescript/app-12-crypto-wallet`

---

## Application Information
- **App ID:** app-12
- **Name:** Crypto Wallet Service
- **Language:** Typescript
- **Framework:** Nestjs

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A02 | Cryptographic Failures | Critical | src/wallet/wallet.service.ts | CWE-256 |
| V2 | A04 | Insecure Design | High | src/wallet/wallet.controller.ts | CWE-352 |
| V3 | A07 | Identification and Authentication Failures | High | src/wallet/wallet.service.ts | CWE-308 |

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures

- **Severity:** Critical
- **Location:** `src/wallet/wallet.service.ts`:20-35 (method: `createWallet`)
- **CWE:** [CWE-256](https://cwe.mitre.org/data/definitions/256.html)

#### Description
Cryptographic Failures. Wallet private keys are stored in the database in plaintext without any encryption or secure enclave protection.

### VULN-02: A04 — Insecure Design

- **Severity:** High
- **Location:** `src/wallet/wallet.controller.ts`:40-60 (method: `transferFunds`)
- **CWE:** [CWE-352](https://cwe.mitre.org/data/definitions/352.html)

#### Description
Insecure Design. The transfer funds endpoint executes immediately upon request without any transaction confirmation step, multi-step validation, or intent verification.

### VULN-03: A07 — Identification and Authentication Failures

- **Severity:** High
- **Location:** `src/wallet/wallet.service.ts`:45-70 (method: `executeTransfer`)
- **CWE:** [CWE-308](https://cwe.mitre.org/data/definitions/308.html)

#### Description
Identification and Authentication Failures. High-value transactions (transfers of any amount) are processed without requiring Multi-Factor Authentication (MFA) or step-up authentication.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Wallet IDOR → Private Key Exposure → Unauthorized Asset Transfer

- **Combined Impact:** `data_modification`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker calls GET /api/wallet?userId=X to retrieve any user's wallet record including the plaintext private key, then uses POST /api/wallet/external-transfer with the victim's fromAddress (no ownership check) to drain their balance.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | GET /api/wallet accepts optional userId query param without verifying it matches the authenticated user, exposing any wallet's full record including address | Medium | A01 | CWE-639 | src/wallet/wallet.controller.ts | `getWallet` |
| 2 | Wallet record returned by getWallet() includes the privateKey field stored in plaintext, giving the caller full cryptographic control over the victim's wallet | High | A02 | CWE-312 | src/wallet/wallet.service.ts | `getWallet` |
| 3 | POST /api/wallet/external-transfer accepts fromAddress in the request body without verifying the authenticated user owns that address, allowing arbitrary fund transfers | High | A01 | CWE-862 | src/wallet/wallet.controller.ts | `externalTransfer` |

### CHAIN-02: Subtle Auth Session Pivot To Crypto

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
| 1 | Identification and Authentication Failures. High-value transactions (transfers of any amount) are processed without requiring Multi-Factor Authentication (MFA) or step-up authentication. | High | A07 | CWE-308 | src/wallet/wallet.service.ts | `executeTransfer` |
| 2 | Insecure Design. The transfer funds endpoint executes immediately upon request without any transaction confirmation step, multi-step validation, or intent verification. | High | A04 | CWE-352 | src/wallet/wallet.controller.ts | `transferFunds` |
| 3 | Cryptographic Failures. Wallet private keys are stored in the database in plaintext without any encryption or secure enclave protection. | Critical | A02 | CWE-256 | src/wallet/wallet.service.ts | `createWallet` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/auth/auth.guard.ts | Standard JWT authentication guard protecting endpoints. |
