# Chained Vulnerability Scenarios — Warehouse Mgmt

## Chain: "LDAP Injection → Directory Structure Disclosure → Inventory Tampering"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/employees/search?q=` accepts unsanitized input concatenated directly into an LDAP filter string, enabling LDAP injection to enumerate arbitrary accounts | Medium | A03 | `EmployeeLdapService.java` → `searchEmployees()` |
| 2 | LDAP exceptions are caught and returned verbatim in the HTTP response body including internal DN paths (e.g., `ou=employees,dc=warehouse,dc=local`), leaking the full directory structure | Low | A05 | `EmployeeController.java` → `search()` |
| 3 | `POST /api/inventory/{id}/adjust` has no role check; any authenticated user (including low-privilege warehouse worker accounts discovered via LDAP) can modify inventory quantities for any item | High | A01 | `InventoryController.java` → `adjustQuantity()` |


**Attack narrative**: An attacker injects a malformed LDAP filter (`*)(objectClass=*` suffix) which triggers an LDAP exception. The verbose error response reveals internal directory paths, confirming account naming conventions (`uid=worker01,ou=employees,...`). The attacker authenticates as any discovered worker account and calls `POST /api/inventory/{id}/adjust?delta=-9999` repeatedly to zero out stock counts, disrupting warehouse operations.

**Combined Impact**: Inventory data modification and operational disruption of warehouse stock management.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
