# Audit Report: app-12 — Crypto Wallet Service

**Language:** TypeScript (NestJS)  
**Business Domain:** Cryptocurrency / Finance  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A02 — Plaintext Private Key Storage

**Severity:** Critical  
**Location:** `src/wallet/wallet.service.ts:20-35` — `createWallet()`  
**Description:** Wallet private keys stored in database in plaintext without encryption or secure enclave protection.

**Difficulty: VERY EASY**

- Private keys directly stored as plaintext strings
- Any database breach or SQLi yields all private keys
- No Hardware Security Module (HSM) or secure enclave

### VULN-02: A04 — No Transaction Confirmation (Insecure Design)

**Severity:** High  
**Location:** `src/wallet/wallet.controller.ts:40-60` — `transferFunds()`  
**Description:** Transfer endpoint executes immediately upon request without any confirmation step or intent verification.

**Difficulty: EASY**

- No CSRF protection on transfer
- No confirmation prompt or 2FA step-up
- Single request causes irreversible fund transfer

### VULN-03: A07 — Missing MFA on High-Value Transactions

**Severity:** High  
**Location:** `src/wallet/wallet.service.ts:45-70` — `executeTransfer()`  
**Description:** High-value transfers processed without requiring Multi-Factor Authentication.

**Difficulty: EASY**

- No step-up authentication for large transfers
- Single-factor auth sufficient for any amount
- Violates financial best practices

---

## Chained Attack: chain-01

**Chain Name:** Wallet IDOR → Private Key Exposure → Unauthorized Asset Transfer  
**Combined Impact:** Data Modification (Theft of Cryptocurrency)  
**Overall Chain Difficulty: EASY**

### Link 1: Wallet IDOR (A01 — Medium)

**Location:** `wallet.controller.ts` — `getWallet()`  
**Description:** GET `/api/wallet?userId=X` accepts optional userId param without verifying it matches authenticated user.

### Link 2: Private Key Exposure (A02 — High)

**Location:** `wallet.service.ts` — `getWallet()`  
**Description:** Wallet record includes privateKey field in plaintext, giving attacker full cryptographic control.

### Link 3: External Transfer Without Ownership Check (A01 — High)

**Location:** `wallet.controller.ts` — `externalTransfer()`  
**Description:** POST `/api/wallet/external-transfer` accepts fromAddress in body without verifying ownership.

---

## Summary

App-12 is a NestJS crypto wallet with devastating vulnerabilities. Plaintext private key storage is the most critical finding. The chain from IDOR to private key exposure to unauthorized transfer is trivially exploitable. This app tests for crypto-specific security awareness.

**Overall Difficulty Score:** 1/5 (Very Easy — chain is three simple API calls)