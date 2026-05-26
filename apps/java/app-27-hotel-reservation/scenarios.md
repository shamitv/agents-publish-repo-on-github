# Chained Vulnerability Scenario — Hotel Reservation System

## Chain: "Debug Info Leak → Session Fixation → Account Takeover"

An unauthenticated attacker exploits an exposed debug endpoint to discover default credentials and uses session fixation to take over an admin session.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|----------------------|-------|----------|
| 1 | Unauthenticated debug configuration endpoint exposes system info and credentials. | Medium | A05 | `AdminController.java` → `getSystemInfo()` |
| 2 | Security config session management lacks session rotation, allowing session fixation. | Medium | A07 | `SecurityConfig.java` → `filterChain()` |

**Attack narrative**: The attacker accesses the unauthenticated debug endpoint to discover default admin credentials and environment details. The attacker then uses session fixation by injecting a known session ID into the system and waits for an admin to log in. Because session IDs are not rotated upon login, the attacker hijacks the admin's session and gains full administrative access to the hotel reservation system.

**Combined Impact**: Account takeover — attacker gains full administrative control over the hotel reservation system.