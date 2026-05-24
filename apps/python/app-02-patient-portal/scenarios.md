# Chained Vulnerability Scenarios — Patient Portal

## Chain: "User Enumeration → Offline MD5 Crack → Medical Records Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Login returns distinct messages: *"Account not found"* vs *"Incorrect password"* — allows enumeration of valid usernames without authentication | Low | A07 | `portal/views.py` → `login_view()` |
| 2 | Passwords stored as unsalted MD5 hashes — crackable offline in seconds with rainbow tables or hashcat | High | A02 | `portal/models.py` → `set_password_md5()` |
| 3 | `GET /api/patients/search?name=X` returns patient IDs for any authenticated user — feeds the IDOR on `GET /api/patients/{id}/records` | Low | A01 | `portal/views.py` → `search_patients()` |


**Attack narrative**: The attacker calls `POST /api/auth/login` with candidate usernames; the distinct error text confirms which accounts exist. They then attempt login with a common password (`alice123`) or crack the MD5 hash offline. Once authenticated, they query `GET /api/patients/search?name=` (blank name returns all patients) to collect every patient ID. Finally, they loop through IDs calling `GET /api/patients/{id}/records`, reading prescriptions and diagnostic notes for every patient.

**Combined Impact**: Full medical records exfiltration across all patients.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
