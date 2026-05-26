# Chained Vulnerability Scenarios — Vet Clinic

## Chain: "Weak JWT → SQL Injection → Prescription Tampering"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Weak JWT signature key allows offline forgery | Medium | A02 | `app.py` → `generate_token()` |
| 2 | SQL injection in pet search exposes database details | Medium | A03 | `app.py` → `search_pets()` |
| 3 | Prescription updates write no audit logs | Low | A09 | `app.py` → `update_prescription()` |


**Attack narrative**: 1. The attacker notes that the JWT tokens are signed using a weak secret key `secret123`.
2. The attacker crafts a custom JWT offline containing the claim `"role": "VET"`, giving them veterinarian-level access privileges.
3. Using the forged JWT, the attacker calls the search endpoint `/api/pets/search?q=1' OR '1'='1` to trigger SQL injection, obtaining all pet IDs and owner records from the database.
4. Armed with a target pet ID, the attacker sends a post request to `/api/prescriptions/<prescription_id>/update` to change a prescription (e.g., increasing a controlled substance dosage or introducing a dangerous drug interaction).
5. The application accepts the change but produces no logs, leaving clinic administration unaware of the unauthorized medication change.

**Combined Impact**: `data_modification` — Unauthorized dosage and drug alterations on patient prescriptions go entirely undetected.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
