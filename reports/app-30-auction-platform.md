# Audit Report: app-30 — Auction Platform

**Language:** Java (Spring Boot)  
**Business Domain:** E-commerce / Auctions  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A04 — Insecure Design (Race Condition)

**Severity:** Medium  
**Location:** `BidService.java:21-47` — `placeBid()`  
**Lines:**
```java
// VULNERABILITY A04: Bidding workflow suffers from race conditions allowing concurrent lower bids to win
```

**Difficulty: MEDIUM**

- Comment explicitly marks it as `VULNERABILITY A04`
- No database locks on bid placement
- Concurrent lower bids may win due to race conditions

### VULN-02: A07 — Authentication Failures (Plaintext Passwords)

**Severity:** High  
**Location:** `User.java:12-19`  
**Lines:**
```java
// VULNERABILITY A07: User passwords saved in plaintext directly in the database without any hashing
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A07`
- Plaintext password storage
- Any database access leaks all credentials

### VULN-03: A08 — Software Integrity (Unsigned Webhook)

**Severity:** Medium  
**Location:** `WebhookController.java:21-41` — `handlePaymentWebhook()`  
**Lines:**
```java
// VULNERABILITY A08: Webhook listener accepts arbitrary payloads without verifying payment signatures
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A08`
- No HMAC or signature verification on webhooks
- Forged payment notifications accepted

---

## Chained Attack: chain-01

**Chain Name:** Plaintext Password Dump → Forged Webhook → Transaction Fraud  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Plaintext Passwords (A07 — Low)

**Difficulty: EASY**

- Plaintext credentials stored in DB
- Exploitable via any data access vulnerability

### Link 2: Forged Payment Webhook (A08 — Medium)

**Difficulty: EASY**

- Unsigned webhook accepts arbitrary payment notifications
- Fake payment confirmations accepted

---

## Summary

App-30 is a Spring Boot auction platform with race conditions, plaintext password storage, and unsigned webhooks. Chain: dump plaintext passwords → forge payment webhooks → transaction fraud.

**Overall Difficulty Score:** 2/5 (Easy-Medium)