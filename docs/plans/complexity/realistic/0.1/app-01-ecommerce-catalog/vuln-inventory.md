# Vulnerability Inventory — App 01 (E-Commerce Product Catalog API)

## Purpose

This document enumerates every intentionally planted vulnerability, chain link, and decoy in the **current** app-01 codebase. It serves as a **no-touch zone** reference during the expansion — no implementation step may remove, weaken, or fix any item listed here.

---

## App Profile

| Property | Value |
|----------|-------|
| App ID | `app-01` |
| Language | Python |
| Framework | Flask |
| Source file count | 38 |
| Complexity rating | 5 — Very Complex |
| Backend entry point | `apps/python/app-01-ecommerce-catalog/app.py` |
| Manifest | `apps/python/app-01-ecommerce-catalog/.vulns` |

---

## Standalone Vulnerabilities

### VULN-01 — IDOR on Order Retrieval

| Field | Value |
|-------|-------|
| OWASP | **A01** — Broken Access Control |
| CWE | CWE-639 |
| File | `src/controllers/order_controller.py` |
| Method | `get_order_details` |
| Line | 19 |
| Severity | High |
| Source Comment | `// VULNERABILITY A01: IDOR returns any order by ID without checking ownership.` |
| Description | After authentication, the endpoint returns any order record by path parameter `{id}` without verifying the authenticated user owns the order. |

### VULN-02 — SQL/Elasticsearch Injection in Product Search

| Field | Value |
|-------|-------|
| OWASP | **A03** — Injection |
| CWE | CWE-943 |
| File | `src/services/search_service.py` |
| Method | `search` |
| Severity | High |
| Source Comment | Not yet annotated inline — search diff needed |
| Description | Product search inserts user input directly into SQL fallback search and Elasticsearch `query_string` syntax, allowing data exfiltration or query manipulation. |

### VULN-03 — Missing Audit Logging in Billing Consumer

| Field | Value |
|-------|-------|
| OWASP | **A09** — Security Logging and Monitoring Failures |
| CWE | CWE-778 |
| File | `src/consumers/billing_consumer.py` |
| Method | `process_order_event` |
| Severity | Medium |
| Source Comment | Not yet annotated inline — search diff needed |
| Description | Order event processing changes invoice state without structured audit logging, making SOX/PCI compliance verification impossible. |

---

## Chained Vulnerability Scenario

### chain-01: User Enumeration → Session Forgery → Catalog Modification

**Combined Impact**: `data_modification`

| Step | OWASP | CWE | File | Method | Severity (standalone) | Source Comment |
|------|-------|-----|------|--------|-----------------------|----------------|
| 1 | A01 | CWE-203 | `src/controllers/user_controller.py` | `user_exists` | Low | `// CHAIN LINK 1 (chain-01): Unauthenticated username existence endpoint confirms privileged accounts` |
| 2 | A02 | CWE-798 | `src/config/settings.py` | `SECRET_KEY` | Medium | `// CHAIN LINK 2 (chain-01): Hardcoded Flask SECRET_KEY enables forged admin session cookies` |
| 3 | A01 | CWE-862 | `src/controllers/product_controller.py` | `create_product` | Medium | `// CHAIN LINK 3 (chain-01): Admin product mutation trusts forgeable session role without stronger auth proof` |

**Attack narrative**: Attacker probes `GET /api/users/exists?username=admin` (unauthenticated) to confirm the admin account exists. Using the hardcoded Flask `SECRET_KEY` visible in source, the attacker forges a signed Flask session cookie with admin role claims and sends it to `POST /api/products` to write attacker-controlled catalog data.

---

## Decoy Patterns (Safe Code Near Vulnerable Areas)

### DECOY-01 — Parameterized Login Query

| Field | Value |
|-------|-------|
| File | `src/repositories/user_repository.py` |
| Pattern | Parameterized SQL in login |
| Why it looks vulnerable | Adjacent to the vulnerable product search query; uses raw SQL with user input |
| Why it is safe | Uses parameterized placeholders (`%s` with tuple args) that prevent injection |

### DECOY-02 — Session-based Profile Lookup

| Field | Value |
|-------|-------|
| File | `src/controllers/user_controller.py` |
| Method | `profile` (or equivalent) |
| Pattern | Reads user ID from session, not from request param |
| Why it looks vulnerable | Located in the same controller as the vulnerable `user_exists` (chain link 1); appears to do user lookup |
| Why it is safe | Uses `session["user_id"]` rather than accepting an arbitrary user ID from request parameters |

---

## No-Touch Files During Expansion

These files contain vulnerability annotations and **must not be modified** in ways that weaken or remove the vulnerabilities:

| File | Annotations | Action Allowed? |
|------|------------|-----------------|
| `src/controllers/order_controller.py` | VULNERABILITY A01 | No direct modification |
| `src/services/search_service.py` | VULNERABILITY A03 | No direct modification |
| `src/consumers/billing_consumer.py` | VULNERABILITY A09 | No direct modification |
| `src/controllers/user_controller.py` | CHAIN LINK 1 (chain-01) | No direct modification |
| `src/config/settings.py` | CHAIN LINK 2 (chain-01) | No direct modification — SECRET_KEY must remain hardcoded |
| `src/controllers/product_controller.py` | CHAIN LINK 3 (chain-01) | No direct modification |
| `src/repositories/user_repository.py` | DECOY-01 | No direct modification |
| `.vulns` | Ground truth manifest | Update to add entries only; never delete |

**Rule**: If a refactoring step must touch these files (e.g., moving to a new package), the vulnerability code and comments must be preserved verbatim at the new location, and `.vulns` locations updated accordingly.

---

## OWASP Coverage Gap Analysis

Current coverage vs. OWASP Top 10: 2021:

| OWASP | Category | Covered? | How |
|-------|----------|----------|-----|
| A01 | Broken Access Control | Yes | IDOR (VULN-01), Chain Links 1 & 3 |
| A02 | Cryptographic Failures | Yes | Chain Link 2 (hardcoded key) |
| A03 | Injection | Yes | VULN-02 |
| A04 | Insecure Design | No | **Target for expansion** |
| A05 | Security Misconfiguration | No | **Target for expansion** |
| A06 | Vulnerable & Outdated Components | No | **Target for expansion** |
| A07 | Identification & Auth Failures | No | **Target for expansion** |
| A08 | Software & Data Integrity Failures | No | **Target for expansion** |
| A09 | Security Logging & Monitoring | Yes | VULN-03 |
| A10 | SSRF | No | **Target for expansion** |

**Expansion strategy**: Prioritize planting vulnerabilities in uncovered categories (A04, A05, A06, A07, A08, A10) to broaden the security benchmarking surface.