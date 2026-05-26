# Chained Vulnerability Scenarios — Hr Management

## Chain: "Credential Hash Harvest → Offline Crack → Payroll + SSN Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/employees/{id}/audit` returns the `passwordHash` field for any employee, accessible to any authenticated user (no role check) | Medium | A01 | `EmployeeController.java` → `getEmployeeAudit()` |
| 2 | Password hashes are BCrypt but employees use short dictionary passwords (seed data); offline GPU cracking with a wordlist recovers them in minutes | Low | A02 | `DataInitializer.java` → seed passwords |
| 3 | `GET /api/payroll/{employeeId}` has no ownership or role check — any authenticated session can read any employee's salary and encrypted SSN | High | A01 | `PayrollController.java` → `getPayroll()` |


**Attack narrative**: A low-privilege employee calls `GET /api/employees/{id}/audit` for each integer ID (1, 2, 3, ...) and collects the `passwordHash` of every HR Admin and Manager. They crack those hashes offline using a common wordlist. They log back in as the HR Admin, then iterate `GET /api/payroll/{id}` to dump every employee's salary record. The encrypted SSN field is reversed client-side using the known XOR key `0xDEADBEEF` embedded in `Employee.java`.

**Combined Impact**: Full workforce PII exfiltration including salaries and SSNs.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
