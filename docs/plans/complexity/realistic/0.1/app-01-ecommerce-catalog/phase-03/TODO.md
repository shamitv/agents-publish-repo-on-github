# Phase 03 TODO — Async Reporting + Exports + Audit

## Async Job Queue
- [x] Create `services/reporting-service/src/services/job_queue.py`
  - [x] In-memory job store via existing report_job.py model
  - [x] Thread-per-job background processing (daemon threads)
  - [x] Status transitions: pending → running → completed | failed
- [x] Create `services/reporting-service/src/controllers/job_controller.py`
  - [x] `enqueue_job()` — POST `/v1/reports/jobs`
  - [x] `get_job_status(job_id)` — GET `/v1/reports/jobs/{jobId}`
- [x] Add routes (`routes/job_routes.py`)
- [x] Extend `ReportJob` model with `error_message`, `progress_pct`, `output_format`, `output_path` fields

## Export Service
- [x] Create `services/reporting-service/src/services/export_service.py`
  - [x] `export_to_csv(data)` — writes CSV with flattened dict
  - [x] `export_to_xlsx(data)` — writes XLSX via openpyxl
  - [x] Decoy: `sanitize_filename(name)` — whitelist-based sanitization
- [x] Create `services/reporting-service/src/controllers/download_controller.py`
  - [x] `download_report(job_id)` — GET `/v1/reports/{jobId}/download`
- [x] Add route (`routes/download_routes.py`)
- [x] Create `services/reporting-service/exports/` directory (auto-created)
- [x] Add `openpyxl==3.1.5` to requirements.txt

## Audit Logging
- [x] Create `services/reporting-service/src/services/audit_service.py`
  - [x] `log_view_event(job_id, supplier_id)` — JSONL append
  - [x] `log_download_event(job_id, supplier_id)` — JSONL append
  - [x] `query_audit_log(supplier_id, event_type)` — filter by params
  - [x] Decoy: atomic write-then-rename (simulated via lock + append)
- [x] Create `services/reporting-service/src/controllers/audit_controller.py`
  - [x] `query_audit()` — GET `/v1/reports/audit`
- [x] Add route (`routes/audit_routes.py`)

## Webhook System (A10 SSRF)
- [x] Create `services/reporting-service/src/models/webhook_subscription.py`
- [x] Subscription CRUD via model helpers (no separate service needed — create/list/get/delete built into model)
- [x] A10 SSRF vulnerability already exists in `webhook_retry.py` (implanted in earlier work) — subscription endpoint feeds user URLs into the existing SSRF delivery system
- [x] Create `services/reporting-service/src/controllers/webhook_controller.py`
  - [x] `register()` — POST `/v1/reports/webhooks` (accepts unvalidated callback_url)
  - [x] `list_webhooks()` — GET `/v1/reports/webhooks`
  - [x] `unregister()` — DELETE `/v1/reports/webhooks/{id}`
- [x] Add routes (`routes/webhook_routes.py`)

## Supplier Portal API — Async Proxies
- [x] Add to existing `controllers/portal_controller.py`:
  - [x] `request_report()` — POST `/portal/reports/request`
  - [x] `get_job_status()` — GET `/portal/reports/{jobId}/status`
  - [x] `download_report()` — GET `/portal/reports/{jobId}/download`
- [x] Add routes to `routes/portal_routes.py`

## Artifact Updates
- [x] Update `.vulns` — add VULN-06 (A10 SSRF), add export/audit decoys
- [x] Update `README.md` — async jobs, exports, audit, webhooks endpoints
- [x] Update `scenarios.md` — A10 SSRF attack narrative

## Verification
- [x] Job enqueue → status polling → completed → download works end-to-end
- [x] CSV download returns valid CSV with correct headers and rows
- [x] XLSX download returns valid .xlsx file (via openpyxl)
- [x] Download for non-completed job returns 404
- [x] A10: webhook registered with `http://169.254.169.254/latest/meta-data/` — registration succeeds
- [x] A10: webhook delivery system attempts HTTP request to that URL
- [x] Decoy `sanitize_filename` rejects path traversal characters
- [x] Audit log records download events with correct supplier_id
- [x] Audit query filters work correctly (supplier, event type)
- [x] Existing vulnerabilities from all previous phases remain exploitable
