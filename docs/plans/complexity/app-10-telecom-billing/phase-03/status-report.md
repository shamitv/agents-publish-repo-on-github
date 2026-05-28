# Phase 03 Status Report — Chain-02 Implementation

## Summary
Chain-02 annotations added across 3 source files. 2 new standalone vulns. 1 new chain. 2 new decoys.

## Files Created
None (annotations only — no new files)

## Files Modified
- `UsageController.java` — CHAIN LINK 1 + VULNERABILITY A03 adjacents
- `BillingController.java` — CHAIN LINK 2 + VULNERABILITY A01 decoy
- `BillingService.java` — CHAIN LINK 3 + VULNERABILITY A09 decoy
- `.vulns` — added 2 vulns, 1 chain, 2 decoys
- `README.md` — added chain-02 table to Chained Vulnerability Scenario section
- `scenarios.md` — added chain-02 narrative

## New Vulnerabilities
- A01 IDOR: `BillingController.getCustomerInvoices()` (severity: medium)
- A09: `BillingService.getInvoicesByCustomer()` bypasses audit producer (severity: low)

## New Chains
- chain-02: SQLi → IDOR → Audit Bypass → db_exfiltration (3 steps, 4 files, difficulty: Hard)

## New Decoys
- 1: `CustomerController.java` — parameterized query (safe SQLi decoy near A03)
- 2: `BillingAuditProducer.java` — unused audit sink (decoy for A09)

## Existing Vulns Intact
YES

## Chains Functional
- chain-01: exploitable (single endpoint, 3 steps)
- chain-02: exploitable (cross-component, 4 files)

## Tests Passing
5/5
