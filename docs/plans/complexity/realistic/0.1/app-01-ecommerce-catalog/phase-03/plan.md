# Phase 03: Async Reporting + Exports + Audit

## Goal

Convert synchronous report endpoints to an async job-based model with CSV/XLSX export support, job status polling, download endpoints, and structured audit logging for report access events. Plant A10 (SSRF) vulnerability in the webhook callback handler.

## Scope

### Included
- Async report job queue (in-memory, simulated threading pool)
- Job lifecycle: `POST /v1/reports/jobs` → `GET /v1/reports/jobs/{id}` → `GET /v1/reports/{jobId}/download`
- CSV export with proper Content-Disposition headers
- XLSX export via `openpyxl` (without multi-sheet complexity)
- Report audit log: every report access/download recorded with timestamp, user, IP, job ID
- Audit log query API (GET /v1/reports/audit — ADMIN+)
- Webhook callback endpoint for job completion notifications (SSRF plant site)
- Supplier portal API: job status and download proxy endpoints

### Excluded
- React UI (Phase 4)
- i18n (Phase 4)
- Caching, scheduled reports, feature flags (Phase 5)
- Real external webhook delivery (simulated only)

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| In-memory job queue with `threading.Thread` pool | Avoids Celery/Redis dependency; realistic enough for benchmarking |
| Job status poll is synchronous (`GET /jobs/{id}`) | Real-world pattern found in many reporting APIs |
| Export files written to a `exports/` directory per service | Simulates eventual S3/Blob storage without external deps |
| Webhook callback is an internal endpoint with no destination validation | Creates SSRF surface for benchmarking |
| Audit log uses JSONL format on disk | Simulates structured logging without ELK/Splunk; cleanly diffable |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone | A10 | CWE-918 | `services/reporting-service/src/controllers/webhook_controller.py` → `register_webhook` | Webhook registration endpoint accepts a user-supplied `callback_url` without validation; the internal webhook delivery system then makes HTTP requests to this URL, enabling SSRF to internal/cloud-metadata endpoints | High |

**Source comment**: `# VULNERABILITY A10: SSRF via unvalidated webhook callback_url — accepts any URL and makes outbound HTTP request`

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `services/reporting-service/src/services/export_service.py` → `sanitize_filename` | Sanitizes user-supplied export filenames; looks like it could be bypassed | Uses regex whitelist `[a-zA-Z0-9_.-]` and rejects path traversal characters |
| 2 | `services/reporting-service/src/controllers/webhook_controller.py` → `validate_callback_url` (different method) | URL validation function near SSRF endpoint | Properly resolves hostname, checks against allowlist of known-safe domains before making requests |
| 3 | `services/reporting-service/src/services/audit_service.py` → `log_access_event` | Writes to disk from user-triggered events | JSON-serializes all fields, uses atomic write-then-rename pattern |

## Data Model Changes

### Reporting Service
- `ReportJob` extended: `output_format` (csv/xlsx), `output_path`, `progress_pct`, `error_message`
- `ReportAuditEvent` — new entity: `event_id`, `job_id`, `supplier_id`, `event_type` (VIEW/DOWNLOAD/SHARE), `ip_address`, `timestamp`, `user_agent`
- `WebhookSubscription` — new entity: `subscription_id`, `supplier_id`, `callback_url`, `secret_token`, `is_active`

## API Contracts

### Reporting Service (additions)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/v1/reports/jobs` | SUPPLIER+ | Enqueue async report generation; returns `job_id` |
| GET | `/v1/reports/jobs/{jobId}` | SUPPLIER+ | Poll job status (queued/processing/completed/failed) |
| GET | `/v1/reports/{jobId}/download` | SUPPLIER+ | Download CSV or XLSX export |
| GET | `/v1/reports/audit` | ADMIN+ | Query audit log by date range, supplier, event type |
| POST | `/v1/reports/webhooks` | SUPPLIER+ | **VULNERABILITY A10** — register webhook with unvalidated `callback_url` |
| GET | `/v1/reports/webhooks` | SUPPLIER+ | List registered webhooks |
| DELETE | `/v1/reports/webhooks/{subscriptionId}` | SUPPLIER+ | Unregister webhook |

### Supplier Portal API (additions)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/portal/reports/request` | SUPPLIER+ | Proxy to reporting-service job enqueue |
| GET | `/portal/reports/{jobId}/status` | SUPPLIER+ | Proxy to job status |
| GET | `/portal/reports/{jobId}/download` | SUPPLIER+ | Proxy to download endpoint |

## Artifact Updates
- `.vulns`: Add VULN-06 (A10), add decoys
- `README.md`: Add async job lifecycle, export formats, audit logging, webhook endpoints
- `scenarios.md`: Add A10 SSRF attack narrative

## Dependencies
- **Depends on Phase 02** — sync report endpoints exist; this phase wraps them in async job model
- **Phase 04 depends on this** — React UI download and webhook management consume these endpoints
- **Phase 05 depends on this** — caching and webhook retry build on webhook infrastructure

## Testing Focus
- [ ] Enqueue job returns `job_id` and initial status "queued"
- [ ] Polling shows status transition: queued → processing → completed
- [ ] CSV export downloads with correct `Content-Type: text/csv`
- [ ] XLSX export downloads with correct `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- [ ] Download only works for completed jobs (404 for queued/processing)
- [ ] A10: registering webhook with `http://169.254.169.254/latest/meta-data/` is accepted
- [ ] A10: webhook delivery system makes outbound request to the unvalidated URL
- [ ] Decoy `validate_callback_url` rejects non-allowlisted domains
- [ ] Audit log records every download with correct supplier_id and timestamp
- [ ] Audit log query filters by date range and supplier work correctly
- [ ] Existing vulnerabilities from all previous phases remain exploitable