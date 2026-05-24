# Chained Vulnerability Scenario — Pharmaceutical Drug Tracking

## Chain: "IDOR Batch Enumeration → Forged Custody Signature → Supply Chain Tampering"

An authenticated attacker leverages an IDOR vulnerability to enumerate batch data and exploits weak cryptographic signatures to falsify custody chain entries.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|----------------------|-------|----------|
| 1 | IDOR batch endpoint leaks details of batches not belonging to the current user's organization. | Medium | A01 | `BatchController.java` → `getBatchDetails()` |
| 2 | Weak custody signature algorithm allows generating valid transfer signatures off-platform. | Medium | A02 | `CustodyService.java` → `generateCustodySignature()` |

**Attack narrative**: The attacker logs in as a low-privilege user and exploits the IDOR in the batch lookup endpoint to enumerate shipment details for batches owned by other organizations. With access to batch identifiers and custody metadata, the attacker then uses the weak MD5 signature algorithm to generate valid custody transfer signatures, injecting falsified chain-of-custody entries to divert shipments.

**Combined Impact**: Data modification — attacker tampers with pharmaceutical supply chain records to divert or mislabel drug shipments.