# Phase 04: Integration Verification & Metadata Sync

## Goal

Verify chain-02 is fully exploitable end-to-end. Add metadata integrity tests to the test suite. Update the master complexity index to reflect the completed implementation. Run full Docker smoke test and tear down.

## Scope

### Included
- [ ] Add `testChain02MetadataMatchesManifest()` to `App10ApplicationTests.java`
- [ ] Add `testHealthEndpointExposesInfraUrls()` to `App10ApplicationTests.java`
- [ ] Run `mvn test` — all tests pass (existing 5 + new 2 = 7)
- [ ] Docker smoke test — build, health-check, chain exploitation, tear-down
- [ ] Update `docs/plans/complexity/README.md` — app-10 row from "Pending" to "Implemented"
- [ ] Grep verification — confirm all annotations present, none missing, none corrupted

### Excluded
- No source logic changes
- No new vulnerabilities or decoys

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Two new test methods | One validates chain-02 metadata integrity (mirrors existing `benchmarkMetadataMatchesCanonicalChain`), one validates A05 annotation presence. Tests enforce that future changes don't accidentally remove annotations. |
| Master index: "Implemented" | The app code was fully implemented at commit `67c55f3` (2026-05-24). The complexity plan artifacts are now complete. Status should reflect reality. |
| Phase count: 5 | Aligns with existing phase-count conventions for app-01 and app-05 |

## Vulnerability Planting

None — verification phase only.

## Decoy Patterns

None new — existing decoys verified alongside new annotations.

## Data Model Changes

None.

## API Contracts

None.

## Artifact Updates

| File | Change | Details |
|------|--------|---------|
| `App10ApplicationTests.java` | +2 test methods | `testChain02MetadataMatchesManifest()`, `testHealthEndpointExposesInfraUrls()` |
| `docs/plans/complexity/README.md` | Modify app-10 row | Phase structure: Pending → linked; Status: Pending → Implemented |
| `phase-04/status-report.md` | Create | Post-implementation summary |

## Dependencies

- **Depends on**: Phase 3 — chain-02 annotations and all metadata must be in place
- **Required by**: Phase 5 — evaluation runs against verified and tested codebase
