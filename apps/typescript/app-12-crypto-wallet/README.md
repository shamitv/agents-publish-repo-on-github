# App 12 — Crypto Wallet Service

## Overview

A full-stack crypto wallet service built with **NestJS / TypeScript** (Backend) and a decoupled client-side Single Page Application (**HTML5 + vanilla JS + CSS SPA**) served under static asset routes. The system manages user wallets, cryptographic keys, balances, and real-time asset transfers.

This application is built for security-agent benchmarking and evaluation purposes.

---

## Business Domain

**FinTech / Crypto** — Used by individuals to manage their digital assets, view balances, and transfer funds to other addresses.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Node.js, NestJS, TypeScript |
| Frontend | Decoupled client-side SPA (HTML5, JS, CSS) |
| Database | In-Memory Object Store |
| Containerisation | Docker |

---

## Features

### Wallet Management
- Securely create and manage digital wallets.
- View real-time wallet balances and public addresses.

### Asset Transfers
- Instantly send funds to other wallet addresses.
- View comprehensive transaction histories.

### Security Benchmarking

This application contains hidden, realistic vulnerabilities mapped to the OWASP Top 10 categories, designed to challenge security agents and code analysis systems.

For ground-truth details regarding the vulnerabilities, see the `.vulns` file in this directory.

---

## Chained Vulnerability Scenario

### Chain: "Wallet IDOR → Private Key Exposure → Unauthorized Asset Transfer"

A low-impact parameter manipulation escalates into theft of crypto assets from any wallet in the system.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/wallet?userId=X` accepts an optional `userId` query parameter without verifying it matches the authenticated user; any wallet holder can view any other wallet's full record | Medium | A01 | `wallet.controller.ts` → `getWallet()` |
| 2 | The wallet record returned by `getWallet()` includes the `privateKey` field stored in plaintext — the caller receives the victim's private key in the response body | High | A02 | `wallet.service.ts` → `getWallet()` |
| 3 | `POST /api/wallet/external-transfer` accepts `fromAddress` without verifying the authenticated user owns that address; an attacker can drain any wallet using only the address obtained in step 1 | High | A01 | `wallet.controller.ts` → `externalTransfer()` |

**Attack narrative**: The attacker calls `GET /api/wallet?userId=2` to fetch Alice's wallet record, obtaining her `address` and `privateKey`. They then post `{fromAddress: "alice_address", toAddress: "attacker_address", amount: 9999}` to `/api/wallet/external-transfer` which executes the transfer without any ownership validation, draining Alice's balance.

**Combined Impact**: Complete theft of cryptocurrency assets from arbitrary user wallets without possessing their credentials.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Serves the client-side SPA portal |
| POST | `/api/auth/login` | — | Authenticates and establishes session |
| POST | `/api/auth/logout` | — | Terminates active portal session |
| GET | `/api/auth/me` | ANY | Retrieves authenticated user profile |
| GET | `/api/wallet` | ANY | Retrieves user's wallet details |
| POST | `/api/wallet/transfer`| ANY | Initiates a fund transfer |
| GET | `/api/wallet/transactions`| ANY | Lists user's transaction history |

---

## Running Locally

```bash
cd apps/typescript/app-12-crypto-wallet
npm install
npm run build
npm run start:prod
# Frontend served at http://localhost:8012
```

## Running via Docker

```bash
docker build -t app-12-crypto-wallet .
docker run -p 8012:8012 app-12-crypto-wallet
```
