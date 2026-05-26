# Chained Vulnerability Scenarios — HR Management

Supplemental notes only. Ground truth vulnerability data is maintained in [.vulns](.vulns), and the required human-readable chain is in [README.md](README.md).

## Chain: "Payroll IDOR → Weak SSN Encryption → DB Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/payroll/{employeeId}` has no ownership or role check and returns another employee's encrypted SSN | Medium | A01 | `PayrollController.java` → `getPayroll()` |
| 2 | SSN encryption uses reversible XOR with hardcoded key `0xDEADBEEF` | Medium | A02 | `Employee.java` → `getRawSsn()` |

**Attack narrative**: A low-privilege employee iterates payroll IDs, collects salary records and `ssnEncrypted` values, then decrypts those SSNs offline using the hardcoded XOR key from the employee model.

**Combined Impact**: Full workforce PII exfiltration including salaries and SSNs.
