# Chained Vulnerability Scenarios — Parking Management

Supplemental notes only. Ground truth vulnerability data is maintained in [.vulns](.vulns), and the required human-readable chain is in [README.md](README.md).

## Chain: "Elasticsearch Query Injection → Client-Controlled Pricing → Missing Audit Logs"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Raw user input is embedded in Elasticsearch `query_string` syntax | Medium | A03 | `ParkingSearchClient.js` → `searchByQueryString()` |
| 2 | Client-supplied booking total is trusted | Medium | A04 | `BookingService.js` → `book()` |
| 3 | Booking cancellation is saved without an audit event | Low | A09 | `BookingService.js` → `cancel()` |

**Attack narrative**: The attacker broadens spot search with query-string syntax, creates a zero-cost booking, then cancels bookings without an audit event.

**Combined Impact**: Unauthorized data modification of parking bookings and cancellation state.
