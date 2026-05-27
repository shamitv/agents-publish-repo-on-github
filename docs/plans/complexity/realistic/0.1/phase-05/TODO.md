# Phase 05 TODO — Caching, Scheduled Reports, Feature Flags, Webhook Retry

## Cache Service (A08)
- [ ] Create `services/reporting-service/src/services/cache_service.py`
  - [ ] `get(key)` — check TTL, return cached value or None
  - [ ] `set(key, value, ttl)` — store with expiration
  - [ ] `invalidate(pattern)` — delete entries matching glob pattern
  - [ ] `save_cache_to_disk(path)` — decoy: uses `json.dump()`
  - [ ] **VULNERABILITY A08**: `load_cache_from_disk(path)` — uses `pickle.load()`
- [ ] Create `services/reporting-service/src/controllers/admin_controller.py` (or extend existing)
  - [ ] `cache_stats()` — GET `/v1/admin/cache/stats`
  - [ ] `invalidate_cache()` — DELETE `/v1/admin/cache`
- [ ] Add routes
- [ ] Integrate cache with dashboard KPI endpoint and report definitions endpoint

## Scheduler
- [ ] Create `services/reporting-service/src/scheduler.py`
  - [ ] `register_job(job)` — add to schedule
  - [ ] `unregister_job(job_id)` — remove from schedule
  - [ ] `list_jobs()` — return all active schedules
  - [ ] `_run_loop()` — background Thread with Timer-based execution
  - [ ] Decoy: `validate_cron_expression(expr)` — proper cron parsing
- [ ] Create `services/reporting-service/src/controllers/scheduler_controller.py`
  - [ ] `list_schedules()` — GET `/v1/admin/scheduler`
  - [ ] `create_schedule()` — POST `/v1/admin/scheduler`
  - [ ] `delete_schedule()` — DELETE `/v1/admin/scheduler/{jobId}`
- [ ] Add routes
- [ ] Add seed data: 2-3 sample scheduled reports (daily sales, weekly inventory)

## Feature Flags (chain-03 step 2)
- [ ] Create `services/reporting-service/src/models/feature_flag.py` — FeatureFlag model
- [ ] Create `services/reporting-service/src/services/feature_flag_service.py`
  - [ ] `get_enabled_flags(supplier_id)` — returns flags active for this user
  - [ ] `list_all_flags()` — ADMIN+ — all flags with metadata
  - [ ] `toggle_flag(key, enabled)` — ADMIN+ — enable/disable
  - [ ] `create_or_update_flag(data)` — ADMIN+
- [ ] Create `services/reporting-service/src/controllers/feature_flags_controller.py`
  - [ ] `list_flags()` — GET `/v1/admin/feature-flags`
  - [ ] `create_flag()` — POST `/v1/admin/feature-flags`
  - [ ] `toggle_flag()` — PUT `/v1/admin/feature-flags/{key}/toggle`
  - [ ] **CHAIN LINK 2 (chain-03)**: `get_flag_metadata(key)` — GET `/v1/admin/feature-flags/{key}/metadata` — returns unsanitized description
  - [ ] Decoy: `validate_flag_key(key)` — regex whitelist validation
- [ ] Add routes
- [ ] Add seed data: 5+ feature flags with various rollout states
- [ ] Add `GET /portal/feature-flags` to supplier-portal-api

## Webhook Retry
- [ ] Create `services/reporting-service/src/services/webhook_retry.py`
  - [ ] `deliver_with_retry(subscription_id, payload)` — exponential backoff 1s→4s→16s (max 3)
  - [ ] `list_attempts(filters)` — ADMIN+ — delivery history
  - [ ] `trigger_retry()` — ADMIN+ — manual retry trigger
  - [ ] Decoy: `sign_webhook_payload(payload, secret)` — HMAC with `hmac.compare_digest`
- [ ] Create `services/reporting-service/src/models/delivery_attempt.py`
- [ ] Create `services/reporting-service/src/controllers/webhook_controller.py` (extend)
  - [ ] `list_deliveries()` — GET `/v1/admin/webhook-deliveries`
  - [ ] `retry_deliveries()` — POST `/v1/admin/webhook-deliveries/retry`
- [ ] Add routes

## Admin Console Pages (React)
- [ ] Create `src/pages/admin/Flags.tsx` — feature flag list with toggle switches
- [ ] Create `src/pages/admin/FlagDetail.tsx` — flag detail view
  - [ ] Renders flag metadata description — **chain-03 step 2 trigger point**
  - [ ] MUST use `dangerouslySetInnerHTML` or raw injection to render description
- [ ] Create `src/pages/admin/Scheduler.tsx` — scheduled jobs list with CRUD
- [ ] Create `src/pages/admin/Cache.tsx` — cache stats dashboard, invalidation form
- [ ] Add routes to App.tsx: `/admin/flags`, `/admin/flags/:key`, `/admin/scheduler`, `/admin/cache`

## Artifact Updates
- [ ] Update `.vulns` — add VULN-08 (A08 Deserialization), complete chain-03 step 2, add decoys
- [ ] Update `README.md` — caching, scheduler, feature flags, webhook retry, admin console
- [ ] Update `scenarios.md` — complete chain-03 narrative (steps 1 + 2), add A08 attack narrative

## Verification
- [ ] Cache returns KPI data within TTL; re-fetches after expiry
- [ ] Cache invalidation clears matching entries
- [ ] Scheduled job fires and generates report at configured interval
- [ ] Feature flag toggle enables/disables feature in frontend view
- [ ] Feature flag rollout_pct correctly gates ~pct% of requests over sample size
- [ ] A08: crafting a malicious pickle and writing to cache file, then loading triggers code execution
- [ ] A08 decoy: save_cache_to_disk uses json.dump, NOT pickle
- [ ] chain-03 step 2: flag.description contains `<img src=x onerror=alert(1)>` and renders as HTML in admin flag detail page
- [ ] chain-03 full attack: widget XSS → session token theft → admin console access → flag detail XSS → audit log exfiltration
- [ ] Webhook retry: failed delivery retries 3 times with increasing backoff
- [ ] Webhook retry decoy: HMAC uses timing-safe comparison
- [ ] Existing vulnerabilities from all previous phases remain exploitable