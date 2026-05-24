# Implementation Plan — App 30: Auction Platform

## 1. Overview

A Spring Boot online auction platform where users list items, place bids, and complete transactions. Manages auction listings, bidding workflows, user wallets, and transaction settlements.

**Target OWASP vulnerabilities:** A04 (Insecure Design), A07 (Identification & Auth Failures), A08 (Software & Data Integrity Failures)

---

## 2. Business Domain

**E-Commerce / Online Auctions** — Used by sellers listing items, buyers placing bids, and platform administrators managing disputes and fees.

## 3. Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security |
| Database | H2 (embedded, in-memory) |
| Build | Maven |
| Containerisation | Docker |

---

## 4. Project Scaffold

### 4.1 Package Layout
```
src/main/java/com/auction/platform/
├── App30Application.java
├── config/
│   └── SecurityConfig.java
├── controller/
│   ├── AuthController.java
│   ├── ListingController.java
│   ├── BidController.java
│   ├── WalletController.java
│   ├── TransactionController.java
│   └── WebhookController.java
├── model/
│   ├── Listing.java
│   ├── Bid.java
│   ├── Wallet.java
│   ├── Transaction.java
│   └── User.java
├── repository/
│   ├── ListingRepository.java
│   ├── BidRepository.java
│   ├── WalletRepository.java
│   └── TransactionRepository.java
├── service/
│   ├── ListingService.java
│   ├── BidService.java
│   ├── WalletService.java
│   ├── TransactionService.java
│   └── NotificationService.java
└── dto/
    ├── ListingDTO.java
    ├── BidDTO.java
    └── WalletDTO.java
```

---

## 5. Database Schema

### Tables
- **users** — id, username, email, password, role (BUYER/SELLER/ADMIN), created_at
- **listings** — id, seller_id, title, description, category, starting_price, reserve_price, status (ACTIVE/ENDED/CANCELLED), end_time
- **bids** — id, listing_id, bidder_id, amount, placed_at
- **wallets** — id, user_id, balance, currency
- **transactions** — id, listing_id, buyer_id, seller_id, amount, platform_fee, status (PENDING/COMPLETED/DISPUTED), completed_at

### Seed Data
- 15 users (mix of buyers and sellers)
- 20 auction listings in various statuses
- 50+ bids across active and ended auctions
- Wallet balances for all users
- 10 completed transactions

---

## 6. Planned Vulnerabilities

### 6.1 VULNERABILITY A04 — Race Condition in Bidding (No Concurrency Control)
- **Location:** `BidService.java` → `placeBid()`
- **Mechanism:** Bid placement reads current highest bid and checks if the new bid exceeds it, but uses no database-level locking or optimistic concurrency — two simultaneous bids can both "win" at the same price, or a lower bid can be accepted
- **CWE:** CWE-362

### 6.2 VULNERABILITY A07 — Plaintext Password Storage
- **Location:** `User.java` and `AuthController.java` → `register()`
- **Mechanism:** User passwords are stored as plaintext in the `password` column — the registration endpoint does `user.setPassword(request.getPassword())` with no hashing
- **CWE:** CWE-256

### 6.3 VULNERABILITY A08 — Unsigned Webhook Processing
- **Location:** `WebhookController.java` → `handlePaymentWebhook()`
- **Mechanism:** `POST /api/webhooks/payment` accepts payment confirmation webhooks but does not verify the webhook signature or origin — attacker can send forged payment confirmations to complete transactions without paying
- **CWE:** CWE-345

---

## 7. Chained Vulnerability Scenario

### Chain: "Plaintext Password Dump → Forged Webhook → Transaction Fraud"

An attacker who gains read access to the database (e.g., via SQL injection in another service or DB backup exposure) reads plaintext passwords, logs in as a seller, then forges payment webhooks to mark transactions as completed without actual payment.

| Step | Issue | Severity | OWASP |
|------|-------|----------|-------|
| 1 | Plaintext passwords allow credential theft from any DB exposure | Medium | A07 |
| 2 | Unsigned webhooks allow forged payment confirmations | Medium | A08 |

**Impact:** `data_modification` — Attacker fraudulently completes auction transactions without payment, stealing listed items.

---

## 8. Decoy Safe Patterns

- `ListingController.create()` uses `@PreAuthorize("hasRole('SELLER')")` to restrict listing creation to sellers (safe — proper role check)
- `WalletService.deductBalance()` uses `@Transactional` with `SERIALIZABLE` isolation for wallet debits (safe — proper concurrency control, contrasts with the bid race condition)
- `BidController` validates that bid amount is positive and that the auction has not ended (safe input validation)

---

## 9. Checklist

- [ ] Spring Boot project compiles and starts
- [ ] H2 database schema initialises correctly
- [ ] All REST endpoints functional
- [ ] Bid race condition is exploitable with concurrent requests
- [ ] Passwords are stored in plaintext
- [ ] Webhook endpoint accepts unsigned forged payloads
- [ ] Chain scenario is end-to-end exploitable
- [ ] Decoy patterns are in place
- [ ] `.vulns` manifest is complete and accurate
- [ ] README follows project template
- [ ] Dockerfile builds and runs
