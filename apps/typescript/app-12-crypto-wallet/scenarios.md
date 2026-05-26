# Chained Vulnerability Scenarios — Crypto Wallet

## Chain: "Wallet IDOR → Private Key Exposure → Unauthorized Asset Transfer"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/wallet?userId=X` accepts an optional `userId` query parameter without verifying it matches the authenticated user; any wallet holder can view any other wallet's full record | Medium | A01 | `wallet.controller.ts` → `getWallet()` |
| 2 | The wallet record returned by `getWallet()` includes the `privateKey` field stored in plaintext — the caller receives the victim's private key in the response body | High | A02 | `wallet.service.ts` → `getWallet()` |
| 3 | `POST /api/wallet/external-transfer` accepts `fromAddress` without verifying the authenticated user owns that address; an attacker can drain any wallet using only the address obtained in step 1 | High | A01 | `wallet.controller.ts` → `externalTransfer()` |


**Attack narrative**: The attacker calls `GET /api/wallet?userId=2` to fetch Alice's wallet record, obtaining her `address` and `privateKey`. They then post `{fromAddress: "alice_address", toAddress: "attacker_address", amount: 9999}` to `/api/wallet/external-transfer` which executes the transfer without any ownership validation, draining Alice's balance.

**Combined Impact**: Complete theft of cryptocurrency assets from arbitrary user wallets without possessing their credentials.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
