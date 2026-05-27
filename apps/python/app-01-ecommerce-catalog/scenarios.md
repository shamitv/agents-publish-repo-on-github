# Chained Vulnerability Scenarios — E-Commerce Product Catalog API

## Chain: "User Enumeration -> Session Forgery -> Catalog Modification"

An attacker combines three individually low/medium-severity issues to modify catalog data as an administrator.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/users/exists` confirms valid usernames without authentication | Low | A01 | `services/catalog-service/src/controllers/user_controller.py` -> `user_exists()` |
| 2 | Hardcoded Flask `SECRET_KEY` allows forged signed session cookies | Medium | A02 | `services/catalog-service/src/config/settings.py` -> `SECRET_KEY` |
| 3 | Product creation trusts the session role without stronger authorization proof | Medium | A01 | `services/catalog-service/src/controllers/product_controller.py` -> `create_product()` |

**Attack narrative**: The attacker probes `/api/users/exists?username=admin`, signs a Flask session cookie with the hardcoded key, and posts attacker-controlled catalog records through `/api/products`.

**Combined Impact**: Unauthorized catalog data modification.

---

## Chain: "Weak Supplier ID Validation -> Catalog Poisoning"

An attacker exploits weak server-side supplier ID validation to inject forged supplier identities into catalog operations.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Supplier ID validator accepts zero, negative, and non-numeric values without error | Low | A04 | `packages/domain/validators.py` -> `validate_supplier_id_chain()` |

**Attack narrative**: The attacker submits a supplier ID of `0`, `-1`, or `"admin"` to an endpoint that relies on `validate_supplier_id_chain()` for identity checks. The weak validator passes these values through, allowing the attacker to impersonate other suppliers or bypass ownership checks.

**Combined Impact**: Unauthorized data modification through forged supplier identity.

---

_This file is supplemental internal narrative. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
