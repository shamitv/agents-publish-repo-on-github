# Phase 05: Caching, Scheduled Reports, Feature Flags, Webhook Retry

## Goal

Add production hardening features: response caching for dashboard KPIs, scheduled periodic report generation, feature flag system with A/B testing support, and webhook delivery retry with exponential backoff. Plant chain-03 step 2 and A08 (Integrity Failure) vulnerabilities.

## Scope

### Included
- **Caching**: In-memory TTL cache for dashboard KPI queries and report definitions
- **Scheduled Reports**: Cron-like scheduler that auto-generates daily/weekly/monthly reports
- **Feature Flags**: Boolean and percentage-rollout flags managed via admin API, consumed by frontend
- **Webhook Retry**: Failed webhook deliveries retried with exponential backoff (max 3 attempts)
- **Admin Console** (React): Feature flag management, scheduler overview, cache stats
- **Cache-Control headers** on API responses

### Excluded
- Redis/external cache (in-memory only)
- Real cron/scheduler (simulated with threading.Timer)
- Multi-region flag distribution
- Webhook signature verification (mock only)

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| In-memory cache dict with TTL tracking | Realistic enough for benchmarking; avoids Redis dependency |
| Scheduler uses `threading.Timer` loop | Simple, realistic mock; no Celery/Cron dependency |
| Feature flags stored as JSON file on disk | Simulates a config service; easy to inspect and diff |
| Webhook retry uses incremental backoff in-memory | Standard pattern; easy to verify |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Chain Link 2 (chain-03) | A06 | CWE-79 | `services/reporting-service/src/controllers/feature_flags_controller.py` → `get_feature_flag_metadata` | Feature flag metadata endpoint returns user-supplied flag descriptions unsanitized in JSON response; these get rendered by the admin console's flag detail view without escaping | Low |
| 2 | Standalone | A08 | CWE-502 | `services/reporting-service/src/services/cache_service.py` → `load_cache_from_disk` | Cache persistence uses `pickle.load()` on a user-writable file; if an attacker can write a malicious pickle payload to the cache file (via path traversal or SSRF write primitive), deserialization executes arbitrary code | High |

**Chain-03 completed** after this phase:
- Step 1 (Phase 4): Custom dashboard widget accepts raw HTML in React frontend (low, CWE-79)
- Step 2 (Phase 5): Feature flag metadata endpoint returns unsanitized descriptions rendered in admin console (low, CWE-79)
- Combined Impact: `db_exfiltration` — attacker chains XSS in custom widget → reads session token → accesses admin console with privileged session → feature flag metadata XSS executes in admin context → exfiltrates audit logs containing all supplier report data

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `services/reporting-service/src/services/cache_service.py` → `save_cache_to_disk` | Uses `json.dump()` near the vulnerable `pickle.load()` call | JSON serialization, not pickle; safe even with attacker-controlled data |
| 2 | `services/reporting-service/src/controllers/feature_flags_controller.py` → `validate_flag_key` | Flag key validation near the unsanitized metadata endpoint | Uses regex `[a-z][a-z0-9_-]*` whitelist and rejects everything else |
| 3 | `services/reporting-service/src/scheduler.py` → `validate_cron_expression` | Schedule input validation | Properly parses and validates cron syntax; rejects invalid expressions |
| 4 | `services/reporting-service/src/services/webhook_retry.py` → `sign_webhook_payload` | HMAC signature on webhook payloads | Uses `hmac.compare_digest` for timing-safe comparison |

## New Models & Services

### Caching
- `CacheEntry` — key, value, ttl, created_at, access_count
- `cache_service.py` — `get(key)`, `set(key, value, ttl)`, `invalidate(pattern)`
- **VULNERABILITY A08**: `load_cache_from_disk(path)` — uses `pickle.load()`

### Scheduler
- `ScheduledJob` — job_id, report_type, cron_expression, supplier_id, next_run, is_active
- `scheduler.py` — register/unregister/list scheduled jobs, background timer loop
- Decoy: `validate_cron_expression(expr)`

### Feature Flags
- `FeatureFlag` — flag_key, description, enabled, rollout_pct, target_supplier_ids
- `feature_flags_controller.py`
  - `list_flags()` — ADMIN+ — includes flag metadata
  - `toggle_flag(key)` — ADMIN+ — enable/disable
  - **CHAIN LINK 2 (chain-03)**: `get_flag_metadata(key)` — returns unsanitized description

### Webhook Retry
- `WebhookDeliveryAttempt` — subscription_id, attempt_number, status, error, timestamp
- `webhook_retry.py` — `retry_failed_deliveries()`, exponential backoff (1s, 4s, 16s)
- Decoy: `sign_webhook_payload(payload, secret)` — proper HMAC

## API Contracts

### Reporting Service (additions)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/v1/admin/cache/stats` | ADMIN+ | Cache hit/miss ratio, size, TTL distribution |
| DELETE | `/v1/admin/cache` | ADMIN+ | Invalidate cache entries by pattern |
| GET | `/v1/admin/scheduler` | ADMIN+ | List scheduled report jobs |
| POST | `/v1/admin/scheduler` | ADMIN+ | Create scheduled report job |
| DELETE | `/v1/admin/scheduler/{jobId}` | ADMIN+ | Remove scheduled job |
| GET | `/v1/admin/feature-flags` | ADMIN+ | List all feature flags |
| POST | `/v1/admin/feature-flags` | ADMIN+ | Create/update feature flag |
| PUT | `/v1/admin/feature-flags/{key}/toggle` | ADMIN+ | Enable/disable flag |
| GET | `/v1/admin/feature-flags/{key}/metadata` | ADMIN+ | **CHAIN LINK 2 (chain-03)** — returns unsanitized description |
| GET | `/v1/admin/webhook-deliveries` | ADMIN+ | List webhook delivery attempts |
| POST | `/v1/admin/webhook-deliveries/retry` | ADMIN+ | Trigger retry for failed deliveries |

### Supplier Portal API (additions)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/portal/feature-flags` | ANY | Return enabled flags for current user/supplier |

## Admin Console Pages (React)
| Route | Component | Description |
|-------|-----------|-------------|
| `/admin/flags` | `AdminFlagsPage` | Feature flag list, toggle, metadata view |
| `/admin/flags/:key` | `FlagDetailPage` | Flag detail — renders metadata.description, **chain-03 step 2 trigger** |
| `/admin/scheduler` | `AdminSchedulerPage` | Scheduled jobs list, CRUD |
| `/admin/cache` | `AdminCachePage` | Cache stats dashboard, invalidation |

## Artifact Updates
- `.vulns`: Add VULN-08 (A08 Deserialization), complete chain-03 step 2, add admin page decoys
- `README.md`: Caching layer, scheduler, feature flags, webhook retry, admin console sections
- `scenarios.md`: Complete chain-03 narrative with both steps; add A08 attack narrative

## Dependencies
- **Depends on Phase 04** — React admin console pages extend the existing frontend
- **This is the final phase** — no further phases depend on this

## Testing Focus
- [ ] Cache returns cached KPI data within TTL; re-fetches after TTL expiry
- [ ] Cache invalidation by pattern clears matching entries only
- [ ] Schedule a daily sales report; verify it auto-generates after timer fires
- [ ] Feature flag toggle enables/disables feature in frontend
- [ ] Feature flag rollout_pct correctly gates percentage of requests
- [ ] A08: pickle.load cache file with attacker-crafted payload executes arbitrary code
- [ ] A08 decoy: save_cache_to_disk uses json.dump, not pickle
- [ ] chain-03 step 2: flag metadata returns `<script>` in description field
- [ ] chain-03 step 2 + step 1: attacker navigates from widget XSS to admin flag detail, metadata XSS fires in admin context, exfiltrates audit data
- [ ] Webhook retry: failed delivery retries with 1s→4s→16s backoff
- [ ] Webhook retry decoy: HMAC signature uses timing-safe comparison
- [ ] Existing vulnerabilities from all previous phases remain exploitable