# Chained Vulnerability Scenarios — Telemedicine

## Chain: "Weak JWT Signatures → IDOR Records Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | JWT signature signed with a weak secret key | High | A02 | `src/index.ts` → `generateJWT()` |
| 2 | IDOR on appointments retrieves private patient records | High | A01 | `src/index.ts` → `GET /api/appointments/:id` |


**Attack narrative**: 1. The attacker discovers that the application uses a weak JWT secret `healthcare123` to sign its tokens.
2. The attacker uses offline tools to sign a forged JWT with claims `{"userId": 3, "username": "dr_house", "role": "DOCTOR"}`.
3. The attacker sets this forged token in the session cookie.
4. Using doctor authority, the attacker enumerates the appointment endpoint `/api/appointments/<id>`. Because the endpoint suffers from IDOR, they fetch all consultation notes and details of every patient.

**Combined Impact**: `db_exfiltration` — Attacker steals confidential patient records and physician notes.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
