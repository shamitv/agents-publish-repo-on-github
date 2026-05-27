# Phase 03 TODO — Async Reporting + Exports + Audit

## Async Job Queue
- [ ] Create `services/reporting-service/src/services/job_queue.py`
  - [ ] In-memory job store (dict with thread-safe locking)
  - [ ] Thread pool executor for background processing
  - [ ] Status transitions: queued → processing → completed | failed
- [ ] Create `services/reporting-service/src/controllers/job_controller.py`
  - [ ] `enqueue_job()` — POST `/v1/reports/jobs`
  - [ ] `get_job_status(job_id)` — GET `/v1/reports/jobs/{jobId}`
- [ ] Add routes
- [ ] Add seed data: sample queued/processing/completed jobs

## Export Service
- [ ] Create `services/reporting-service/src/services/export_service.py`
  - [ ] `export_to_csv(data)`
  - [ ] `export_to_xlsx(data)`
  - [ ] Decoy: `sanitize_filename(name)` — whitelist-based sanitization
- [ ] Create `services/reporting-service/src/controllers/download_controller.py`
  - [ ] `download_report(job_id)` — GET `/v1/reports/{jobId}/download`
- [ ] Add route
- [ ] Create `services/reporting-service/exports/` directory for output files

## Audit Logging
- [ ] Create `services/reporting-service/src/services/audit_service.py`
  - [ ] `log_view_event(job_id, supplier_id, request)`
  - [ ] `log_download_event(job_id, supplier_id, request)`
  - [ ] `query_audit_log(filters)` — ADMIN+ only
  - [ ] Decoy: uses atomic write-then-rename, JSON serialization
- [ ] Create `services/reporting-service/src/controllers/audit_controller.py`
  - [ ] `query_audit()` — GET `/v1/reports/audit`
- [ ] Add route

## Webhook System (A10 SSRF)
- [ ] Create `services/reporting-service/src/models/webhook_subscription.py`
- [ ] Create `services/reporting-service/src/services/webhook_service.py`
  - [ ] `register_webhook(supplier_id, callback_url, secret)`
  - [ ] `deliver_notification(job_id)` — makes HTTP POST to all registered callbacks
  - [ ] **VULNERABILITY A10**: no URL validation before making outbound request
- [ ] Create `services/reporting-service/src/controllers/webhook_controller.py`
  - [ ] `register()` — POST `/v1/reports/webhooks` (plant A10 comment here)
  - [ ] `list_webhooks()` — GET `/v1/reports/webhooks`
  - [ ] `unregister()` — DELETE `/v1/reports/webhooks/{id}`
  - [ ] Decoy: `validate_callback_url(url)` — proper allowlist check in separate method
- [ ] Add routes

## Supplier Portal API — Async Proxies
- [ ] Create `services/supplier-portal-api/src/controllers/report_controller.py`
  - [ ] `request_report()` — POST `/portal/reports/request`
  - [ ] `get_status()` — GET `/portal/reports/{jobId}/status`
  - [ ] `download()` — GET `/portal/reports/{jobId}/download`
- [ ] Add routes

## Artifact Updates
- [ ] Update `.vulns` — add VULN-06 (A10 SSRF), add export/audit/webhook decoys
- [ ] Update `README.md` — async jobs, exports, audit, webhooks
- [ ] Update `scenarios.md` — A10 SSRF attack narrative

## Verification
- [ ] Job enqueue → status polling → completed → download works end-to-end
- [ ] CSV download returns valid CSV with correct headers and rows
- [ ] XLSX download returns valid .xlsx file
- [ ] Download for non-completed job returns 404
- [ ] A10: webhook registered with `http://169.254.169.254/latest/meta-data/` — registration succeeds
- [ ] A10: webhook delivery system attempts HTTP request to that URL
- [ ] Decoy `validate_callback_url` rejects non-allowlisted domains
- [ ] Audit log records download events with correct supplier_id
- [ ] Audit query filters work correctly (date range, supplier, event type)
- [ ] Existing vulnerabilities from all previous phases remain exploitable