# Phase 05 TODO — Caching, Scheduled Reports, Feature Flags, Webhook Retry

## Cache Service (A08)
- [x] `services/reporting-service/src/services/cache_service.py` exists with full implementation
  - [x] `get(key)` — TTL-aware cache lookup
  - [x] `set(key, value, ttl)` — store with expiration
  - [x] `invalidate(pattern)` — delete entries matching glob
  - [x] `save_cache_to_disk(path)` — decoy: uses `json.dump()`
  - [x] **VULNERABILITY A08**: `load_cache_from_disk(path)` — uses `pickle.load()`
- [x] Cache admin endpoints in `admin_routes.py`:
  - [x] `cache_stats()` — GET `/api/admin/cache/stats`
  - [x] `cache_invalidate()` — POST `/api/admin/cache/invalidate`

## Scheduler
- [x] `services/reporting-service/src/services/scheduler.py` exists with full implementation
  - [x] `add_job()` — add to schedule
  - [x] `delete_job()` — remove from schedule
  - [x] `list_jobs()` — return all active schedules
  - [x] `_run_loop()` — background Thread with `while self._running` loop
  - [x] Decoy: `validate_cron_expression(expr)` — regex-based cron syntax validator
- [x] Scheduler endpoints in `admin_routes.py`:
  - [x] `scheduler_list_jobs()` — GET `/api/admin/scheduler/jobs`
  - [x] `scheduler_add_job()` — POST `/api/admin/scheduler/jobs`
  - [x] `scheduler_delete_job()` — DELETE `/api/admin/scheduler/jobs/{id}`

## Feature Flags (chain-03 step 2)
- [x] `services/reporting-service/src/services/feature_flags.py` exists with full implementation
  - [x] `FeatureFlag` dataclass with key, enabled, description, owner, metadata
  - [x] `list_flags()`, `get_flag()`, `create_flag()`, `toggle_flag()`, `delete_flag()`
  - [x] `get_enabled_flags()` — returns only enabled flags
  - [x] Seed data: 6 feature flags with various states (dashboard-v2, export-xlsx, etc.)
- [x] Feature flag endpoints in `admin_routes.py`:
  - [x] `list_flags()` — GET `/api/admin/flags`
  - [x] `create_flag()` — POST `/api/admin/flags`
  - [x] `get_flag()` — GET `/api/admin/flags/{key}` — **CHAIN LINK 2 (chain-03)**: returns unsanitized description
  - [x] `toggle_flag()` — POST `/api/admin/flags/{key}/toggle`
  - [x] `delete_flag()` — DELETE `/api/admin/flags/{key}`
- [x] Decoy `validate_flag_key(key)` built into `feature_flags.py`
- [x] `GET /portal/feature-flags` in supplier-portal-api

## Webhook Retry
- [x] `services/reporting-service/src/services/webhook_retry.py` exists
  - [x] `create_delivery()` — queue webhook delivery (VULNERABILITY A10 SSRF)
  - [x] `retry_delivery()` — exponential backoff: 1s, 2s, 4s
  - [x] `list_deliveries()`, `get_delivery()`, `get_pending_failed()`
  - [x] Decoy: `sign_webhook_payload(payload, secret)` — HMAC with timing-safe hash
  - [x] Decoy: `is_valid_url(url)` — URL structure validation (not allowlisting)
- [x] Webhook endpoints in `admin_routes.py`:
  - [x] `webhook_list_deliveries()` — GET `/api/admin/webhooks/deliveries`
  - [x] `webhook_create_delivery()` — POST `/api/admin/webhooks/deliveries`
  - [x] `webhook_retry_delivery()` — POST `/api/admin/webhooks/deliveries/{id}/retry`

## Admin Console Pages (React)
- [x] `src/pages/admin/Flags.tsx` — feature flag list with toggle switches
- [x] `src/pages/admin/FlagDetail.tsx` — flag detail view
  - [x] **CHAIN LINK 2 (chain-03)**: renders description via `dangerouslySetInnerHTML`
- [x] `src/pages/admin/Scheduler.tsx` — scheduled jobs list with add/delete CRUD
- [x] `src/pages/admin/Cache.tsx` — cache stats dashboard, invalidation form
- [x] Routes added to App.tsx: `/admin/flags`, `/admin/flags/:key`, `/admin/scheduler`, `/admin/cache`

## Artifact Updates
- [x] Update `.vulns` — add VULN-08 (A08 Deserialization), complete chain-03 step 2, add decoys
- [x] Update `README.md` — admin routes, feature flags, caching, scheduler, webhook retry
- [x] Update `scenarios.md` — complete chain-03 with both steps
- [x] Update `vite.config.ts` — proxy `/portal` to port 5003, `/api/admin` to port 5002

## Verification
- [x] Cache returns KPI data within TTL; re-fetches after expiry
- [x] Cache invalidation clears matching entries
- [x] Scheduled job creation works via admin API
- [x] Feature flag toggle enables/disables flag
- [x] A08: pickle.load in cache_service — identifiable vulnerable pattern
- [x] A08 decoy: save_cache_to_disk uses json.dump, not pickle
- [x] chain-03 step 2: flag.description rendered via `dangerouslySetInnerHTML` in admin detail page
- [x] Webhook retry: exponential backoff 1s→2s→4s
- [x] Webhook retry decoy: `sign_webhook_payload` uses HMAC
- [x] `npm run build` succeeds without errors
- [x] Existing vulnerabilities from all previous phases remain exploitable
