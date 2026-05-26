# Chained Vulnerability Scenario — Auction Platform

## Chain: "Plaintext Password Dump → Forged Webhook → Transaction Fraud"

An attacker who gains database access (or exploits a separate injection) steals plaintext passwords, logs in as a seller, and forges payment webhook notifications to fake payment completion.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|----------------------|-------|----------|
| 1 | Plaintext passwords stored directly in the DB allows easy credential theft. | Low | A07 | `User.java` → (model) |
| 2 | Webhook endpoint accepts payment notifications without signature verification. | Medium | A08 | `WebhookController.java` → `handlePaymentWebhook()` |

**Attack narrative**: The attacker gains access to the database (via a separate SQL injection or credential leak) and extracts plaintext passwords for all users. Using a seller's credentials, the attacker logs in, lists items for auction, and places winning bids. The attacker then sends forged payment webhook notifications directly to the server, which accepts them without signature verification, causing the platform to release items without actual payment transfer.

**Combined Impact**: Data modification — attacker fraudulently completes transactions and receives goods without paying.