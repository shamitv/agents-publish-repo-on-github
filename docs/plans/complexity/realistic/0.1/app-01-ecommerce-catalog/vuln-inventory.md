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
| Source file count | ~50 (3 services + shared packages) |
| Complexity rating | 5 — Very Complex |
| Backend entry points | `apps/python/app-01-ecommerce-catalog/services/*/app.py` (3 services) |
| Manifest | `apps/python/app-01-ecommerce-catalog/.vulns` |

---

## Standalone Vulnerabilities

### VULN-01 — IDOR on Order Retrieval

| Field | Value |
|-------|-------|
| OWASP | **A01** — Broken Access Control |
| CWE | CWE-639 |
| File | `services/catalog-service/src/controllers/order_controller.py` |
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
| File | `services/catalog-service/src/services/search_service.py` |
| Method | `search` |
| Severity | High |
| Source Comment | Not yet annotated inline — search diff needed |
| Description | Product search inserts user input directly into SQL fallback search and Elasticsearch `query_string` syntax, allowing data exfiltration or query manipulation. |

### VULN-03 — Missing Audit Logging in Billing Consumer

| Field | Value |
|-------|-------|
| OWASP | **A09** — Security Logging and Monitoring Failures |
| CWE | CWE-778 |
| File | `services/catalog-service/src/consumers/billing_consumer.py` |
| Method | `process_order_event` |
| Severity | Medium |
| Source Comment | Not yet annotated inline — search diff needed |
| Description | Order event processing changes invoice state without structured audit logging, making SOX/PCI compliance verification impossible. |

### VULN-04 — Weak Supplier ID Validation

| Field | Value |
|-------|-------|
| OWASP | **A04** — Insecure Design |
| CWE | CWE-602 |
| File | `packages/domain/validators.py` |
| Method | `validate_supplier_id` |
| Severity | Medium |
| Source Comment | `# VULNERABILITY A04: validate_supplier_id accepts zero, negative, and non-numeric IDs without error` |
| Description | Supplier ID validation accepts zero, negative, and non-numeric values without error, enabling forged supplier identity injection into subsequent operations. |

---

## Chained Vulnerability Scenario

### chain-01: User Enumeration → Session Forgery → Catalog Modification

**Combined Impact**: `data_modification`

| Step | OWASP | CWE | File | Method | Severity (standalone) | Source Comment |
|------|-------|-----|------|--------|-----------------------|----------------|
| 1 | A01 | CWE-203 | `services/catalog-service/src/controllers/user_controller.py` | `user_exists` | Low | `// CHAIN LINK 1 (chain-01): Unauthenticated username existence endpoint confirms privileged accounts` |
| 2 | A02 | CWE-798 | `services/catalog-service/src/config/settings.py` | `SECRET_KEY` | Medium | `// CHAIN LINK 2 (chain-01): Hardcoded Flask SECRET_KEY enables forged admin session cookies` |
| 3 | A01 | CWE-862 | `services/catalog-service/src/controllers/product_controller.py` | `create_product` | Medium | `// CHAIN LINK 3 (chain-01): Admin product mutation trusts forgeable session role without stronger auth proof` |

**Attack narrative**: Attacker probes `GET /api/users/exists?username=admin` (unauthenticated) to confirm the admin account exists. Using the hardcoded Flask `SECRET_KEY` visible in source, the attacker forges a signed Flask session cookie with admin role claims and sends it to `POST /api/products` to write attacker-controlled catalog data.

### chain-02: Weak Supplier ID Validation → Catalog Poisoning

**Combined Impact**: `data_modification`

| Step | OWASP | CWE | File | Method | Severity (standalone) | Source Comment |
|------|-------|-----|------|--------|-----------------------|----------------|
| 1 | A04 | CWE-602 | `packages/domain/validators.py` | `validate_supplier_id_chain` | Low | `// CHAIN LINK 1 (chain-02): Weak supplier ID validation permits forged identity injection` |

**Attack narrative**: Attacker submits a supplier ID of `0`, `-1`, or `"admin"` to an endpoint that relies on the chain validator. The weak validator passes these values through, enabling forged supplier identity injection. Step 2 (bulk upload trust) to be planted in a later phase.

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
| File | `services/catalog-service/src/controllers/user_controller.py` |
| Method | `profile` (or equivalent) |
| Pattern | Reads user ID from session, not from request param |
| Why it looks vulnerable | Located in the same controller as the vulnerable `user_exists` (chain link 1); appears to do user lookup |
| Why it is safe | Uses `session["user_id"]` rather than accepting an arbitrary user ID from request parameters |

### DECOY-03 — Strict Date Range Validation

| Field | Value |
|-------|-------|
| File | `packages/domain/validators.py` |
| Method | `validate_date_range` |
| Pattern | Accepts user-supplied date strings; co-located with vulnerable `validate_supplier_id` |
| Why it looks vulnerable | Appears to accept raw user date input without sanitization |
| Why it is safe | Parses dates strictly via `datetime.fromisoformat()`, validates start < end, rejects malformed inputs |

### DECOY-04 — Safe Pagination Parser

| Field | Value |
|-------|-------|
| File | `packages/utils/pagination.py` |
| Method | `parse_pagination` |
| Pattern | Parses `?page=` and `?limit=` query params from raw request args |
| Why it looks vulnerable | Reads raw user-supplied integers that could be negative or huge |
| Why it is safe | Clamps page ≥ 1, limit ∈ [1, 100], coerces to int safely |

---

## No-Touch Files During Expansion

These files contain vulnerability annotations and **must not be modified** in ways that weaken or remove the vulnerabilities:

| File | Annotations | Action Allowed? |
|------|------------|-----------------|
| `services/catalog-service/src/controllers/order_controller.py` | VULNERABILITY A01 | No direct modification |
| `services/catalog-service/src/services/search_service.py` | VULNERABILITY A03 | No direct modification |
| `services/catalog-service/src/consumers/billing_consumer.py` | VULNERABILITY A09 | No direct modification |
| `services/catalog-service/src/controllers/user_controller.py` | CHAIN LINK 1 (chain-01) | No direct modification |
| `services/catalog-service/src/config/settings.py` | CHAIN LINK 2 (chain-01) | No direct modification — SECRET_KEY must remain hardcoded |
| `services/catalog-service/src/controllers/product_controller.py` | CHAIN LINK 3 (chain-01) | No direct modification |
| `services/catalog-service/src/repositories/user_repository.py` | DECOY-01 | No direct modification |
| `packages/domain/validators.py` | VULNERABILITY A04 + CHAIN LINK 1 (chain-02) | No direct modification |
| `packages/utils/pagination.py` | DECOY (parse_pagination) | No direct modification |
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
| A04 | Insecure Design | Yes | VULN-04 (weak validation) + Chain Link 1 (chain-02) |
| A05 | Security Misconfiguration | No | **Target for expansion** |
| A06 | Vulnerable & Outdated Components | No | **Target for expansion** |
| A07 | Identification & Auth Failures | No | **Target for expansion** |
| A08 | Software & Data Integrity Failures | No | **Target for expansion** |
| A09 | Security Logging & Monitoring | Yes | VULN-03 |
| A10 | SSRF | No | **Target for expansion** |

**Expansion strategy**: Prioritize planting vulnerabilities in uncovered categories (A04, A05, A06, A07, A08, A10) to broaden the security benchmarking surface.