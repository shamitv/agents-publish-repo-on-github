# Phase 02: New Standalone A05 — Health Endpoint Info Leak

## Goal

Annotate the existing infrastructure-info leak in `HealthService.currentHealth()` as a standalone A05 (Security Misconfiguration) vulnerability. This endpoint, accessible without authentication at `GET /api/health`, returns the Kafka bootstrap server URL and Elasticsearch URL — internal infrastructure addresses that should not be exposed to unauthenticated callers. The annotation-only change adds a new standalone vulnerability to the benchmark while filling the documented A05 OWASP gap.

## Scope

### Included
- [ ] Add `// VULNERABILITY A05` annotation to `HealthService.java` → `currentHealth()`
- [ ] Update `.vulns` — add standalone A05 vulnerability entry
- [ ] Update `vuln-inventory.md` — mark A05 as covered
- [ ] Confirm decoy: same method's DB health check (`jdbcTemplate.queryForObject("select 1", …)`) is parameterized and safe

### Excluded
- No logic changes — behavior of `currentHealth()` stays identical
- No new endpoints or API contract changes
- No README changes (covered in Phase 3)

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Annotate only — no removal of fields | Removing `kafka`/`search` from response would fix the real vulnerability, violating AGENTS.md. Annotation preserves exploitability. |
| HealthService not HealthController | The vulnerability is in the service layer where the URL injection happens; controller is a thin pass-through |
| Low severity | The leaked URLs are internal service names (not external IPs); requires network access to the Docker network to exploit further |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone | A05 | CWE-200 | `service/HealthService.java` → `currentHealth()` (lines 26-31) | Health endpoint exposes internal Kafka bootstrap URL (`PLAINTEXT://kafka:9092`) and Elasticsearch URL (`http://elasticsearch:9200`) to unauthenticated callers via `GET /api/health` | Low |

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `service/HealthService.java` → `currentHealth()` (line 25) | Same method that exposes infra URLs — agents may flag the entire method | Database health check: `jdbcTemplate.queryForObject("select 1", Integer.class)` — fully parameterized, no injection risk, no sensitive data exposed |

## Data Model Changes

None.

## API Contracts

None changed — `GET /api/health` response format unchanged.

## Artifact Updates

| File | Change | Content |
|------|--------|---------|
| `src/main/java/com/telecom/billing/service/HealthService.java` | +2 annotation lines (above line 26) | `// VULNERABILITY A05: Health endpoint exposes internal Kafka and Elasticsearch infrastructure URLs to unauthenticated callers.` |
| `.vulns` | +1 entry in `vulnerabilities` array | A05 standalone — see TODO for JSON |
| `vuln-inventory.md` | Update OWASP gap table | A05 → ✅ covered |

## Dependencies

- **Depends on**: Phase 1 — inventory must document existing state and confirm no A05 annotation exists
- **Required by**: Phase 4 — verification phase validates A05 annotation presence
