# Chained Vulnerability Scenario — Manufacturing Quality Control

## Chain: "Privilege Escalation → Silent Defect Closure → Undetected Quality Fraud"

An attacker with a low-privilege account uses mass assignment to escalate privileges, then exploits missing approval workflows and audit logging to silently alter quality records.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|----------------------|-------|----------|
| 1 | Mass assignment allows escalating privilege from WORKER to QA_MANAGER. | Medium | A01 | `AuthController.java` → `updateProfile()` |
| 2 | Lack of defect closure approval allows self-resolution of major defects. | Medium | A04 | `DefectController.java` → `resolveDefect()` |
| 3 | No logging on inspection modifications allows silent data tampering. | Low | A09 | `InspectionService.java` → `updateInspectionResult()` |

**Attack narrative**: The attacker registers as a WORKER and updates their profile using mass assignment to escalate their role to QA_MANAGER. With elevated privileges, the attacker marks critical defects as resolved without requiring manager approval. Finally, the attacker modifies inspection results to show passed for failed components, covering all traces since no audit logging is in place.

**Combined Impact**: Data modification — attacker silently alters quality control records to pass defective products through the manufacturing pipeline.