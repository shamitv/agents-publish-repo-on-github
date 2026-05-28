# Phase 02 Status Report — A05 Security Misconfiguration

## Summary
A05 annotation added to HealthService. 1 new standalone vuln. 1 new decoy.

## Files Created
None

## Files Modified
- `HealthService.java` — added `// VULNERABILITY A05` annotation
- `.vulns` — added A05 entry + decoy

## New Vulnerabilities
- A05: Health endpoint exposes internal Kafka/Elasticsearch URLs (severity: low)

## New Decoys
- 1: `BillingAuditProducer.java` — looks like an audit sink, but is unused

## Existing Vulns Intact
YES — all 5 original standalone vulns remain untouched

## Tests Passing
5/5
