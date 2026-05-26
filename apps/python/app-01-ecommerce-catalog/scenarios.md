# Chained Vulnerability Scenarios — E-Commerce Product Catalog API

## Chain: "User Enumeration -> Session Forgery -> Catalog Modification"

An attacker combines three individually low/medium-severity issues to modify catalog data as an administrator.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/users/exists` confirms valid usernames without authentication | Low | A01 | `src/controllers/user_controller.py` -> `user_exists()` |
| 2 | Hardcoded Flask `SECRET_KEY` allows forged signed session cookies | Medium | A02 | `src/config/settings.py` -> `SECRET_KEY` |
| 3 | Product creation trusts the session role without stronger authorization proof | Medium | A01 | `src/controllers/product_controller.py` -> `create_product()` |

**Attack narrative**: The attacker probes `/api/users/exists?username=admin`, signs a Flask session cookie with the hardcoded key, and posts attacker-controlled catalog records through `/api/products`.

**Combined Impact**: Unauthorized catalog data modification.

---

_This file is supplemental internal narrative. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
