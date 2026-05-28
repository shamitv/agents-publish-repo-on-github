# Chained Vulnerability Scenarios — HR Management

Supplemental notes only. Ground truth vulnerability data is maintained in [.vulns](.vulns), and the required human-readable chain is in [README.md](README.md).

## Chain: "Payroll IDOR → Weak SSN Encryption → DB Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/payroll/{employeeId}` has no ownership or role check and returns another employee's encrypted SSN | Medium | A01 | `PayrollController.java` → `getPayroll()` |
| 2 | SSN encryption uses reversible XOR with hardcoded key `0xDEADBEEF` | Medium | A02 | `Employee.java` → `getRawSsn()` |

**Attack narrative**: A low-privilege employee iterates payroll IDs, collects salary records and `ssnEncrypted` values, then decrypts those SSNs offline using the hardcoded XOR key from the employee model.

**Combined Impact**: Full workforce PII exfiltration including salaries and SSNs.

---

## Chain: "State Bypass → Missing Audit → Data Modification"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | State machine allows Draft→Active skip without intermediate checks | Low | A04 | `OnboardingWorkflowService.java` → `transition()` |
| 2 | State transitions persist without writing audit log entries | Low | A09 | `OnboardingWorkflowService.java` → `transition()` |

**Attack narrative**: An HR_ADMIN creates an onboarding request, then transitions directly to ACTIVE from DRAFT bypassing the Background Check. No audit log entry is created, so the unauthorized transition leaves no forensic trace.

**Combined Impact**: Unauthorized employee activation without proper vetting; the data modification cannot be attributed.

---

## Chain: "Password Hash Leak → Weak Session → Account Takeover"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Audit endpoint returns passwordHash for any employee ID without authorization | Low | A01 | `EmployeeController.java` → `getEmployeeAudit()` |
| 2 | Dashboard session idle timeout is set to 24 hours | Low | A07 | `WebController.java` → `dashboard()` |

**Attack narrative**: An authenticated attacker reads `GET /api/employees/{id}/audit` for any employee to obtain their BCrypt passwordHash, cracks it offline, then exploits the 24-hour dashboard session idle timeout window to brute-force login as that user.

**Combined Impact**: Account takeover via leaked credential hash and prolonged session window.
