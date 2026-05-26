# Chained Vulnerability Scenarios — Telemedicine

Supplemental notes only. Ground truth vulnerability data is maintained in [.vulns](.vulns), and the required human-readable chain is in [README.md](README.md).

## Chain: "Weak JWT Validation → Patient Notes IDOR"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | JWT payload is decoded without validating the signature | Medium | A07 | `TokenService.ts` → `verify()` |
| 2 | Appointment details expose physician notes by ID without owner/doctor checks | Medium | A01 | `AppointmentService.ts` → `getAppointmentDetail()` |

**Attack narrative**: The attacker supplies a forged JWT payload, then enumerates `/api/appointments/:id` to retrieve appointment records and confidential doctor notes.

**Combined Impact**: Database exfiltration of patient appointment records and physician notes.
