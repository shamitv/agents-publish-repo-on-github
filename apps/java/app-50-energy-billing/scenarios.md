# Chained Vulnerability Scenario — Energy Utility Billing

## Chain: "SSRF → H2 Console Access → Database Exfiltration"

An external attacker exploits an SSRF vulnerability in the smart meter endpoint to reach an unauthenticated H2 database console on localhost, enabling arbitrary SQL execution and data theft.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|----------------------|-------|----------|
| 1 | SSRF allows sending requests to internal endpoints. | Medium | A10 | `IntegrationController.java` → `fetchSmartMeterData()` |
| 2 | H2 database console is enabled without security check. | Medium | A05 | `SecurityConfig.java` → `filterChain()` |

**Attack narrative**: The attacker triggers the SSRF vulnerability via the smart meter data endpoint, supplying a URL pointing to the H2 database console running on localhost (http://127.0.0.1:8080/h2-console). Since the H2 console is enabled without authentication, the attacker executes arbitrary SQL queries through it, bypassing network-level restrictions. This allows the attacker to dump all customer billing and personal data from the database.

**Combined Impact**: Database exfiltration — attacker steals all customer billing records, PII, and usage data from the database.