# Implementation Plan — App 29: Vehicle Fleet Management

## 1. Overview

A Spring Boot fleet management system for tracking company vehicles, driver assignments, maintenance schedules, GPS locations, and fuel consumption. Includes an integration endpoint that fetches external vehicle data.

**Target OWASP vulnerabilities:** A03 (Injection), A06 (Vulnerable & Outdated Components), A10 (SSRF)

---

## 2. Business Domain

**Transportation / Fleet Operations** — Used by fleet managers, dispatchers, drivers, and maintenance technicians.

## 3. Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security |
| Database | H2 (embedded, in-memory) |
| Logging | Log4j 2.14.1 (intentionally vulnerable) |
| Build | Maven |
| Containerisation | Docker |

---

## 4. Project Scaffold

### 4.1 Package Layout
```
src/main/java/com/fleet/mgmt/
├── App29Application.java
├── config/
│   └── SecurityConfig.java
├── controller/
│   ├── AuthController.java
│   ├── VehicleController.java
│   ├── DriverController.java
│   ├── MaintenanceController.java
│   ├── LocationController.java
│   └── IntegrationController.java
├── model/
│   ├── Vehicle.java
│   ├── Driver.java
│   ├── MaintenanceRecord.java
│   ├── LocationPing.java
│   ├── FuelLog.java
│   └── User.java
├── repository/
│   ├── VehicleRepository.java
│   ├── DriverRepository.java
│   ├── MaintenanceRecordRepository.java
│   ├── LocationPingRepository.java
│   └── FuelLogRepository.java
├── service/
│   ├── VehicleService.java
│   ├── DriverService.java
│   ├── MaintenanceService.java
│   ├── LocationService.java
│   └── ExternalVehicleService.java
└── dto/
    ├── VehicleDTO.java
    ├── DriverDTO.java
    └── MaintenanceDTO.java
```

---

## 5. Database Schema

### Tables
- **vehicles** — id, vin, make, model, year, license_plate, status (ACTIVE/MAINTENANCE/DECOMMISSIONED), mileage
- **drivers** — id, employee_id, name, license_number, license_expiry, assigned_vehicle_id
- **maintenance_records** — id, vehicle_id, service_type, description, cost, service_date, next_service_date
- **location_pings** — id, vehicle_id, latitude, longitude, speed, recorded_at
- **fuel_logs** — id, vehicle_id, gallons, cost_per_gallon, total_cost, station, logged_at
- **users** — id, username, password_hash, role (DRIVER/DISPATCHER/FLEET_MANAGER/ADMIN)

### Seed Data
- 25 vehicles across various makes/models
- 20 drivers with assignments
- 50+ maintenance records
- GPS ping data for last 7 days
- Fuel logs for last month

---

## 6. Planned Vulnerabilities

### 6.1 VULNERABILITY A03 — LDAP Injection in Driver Lookup
- **Location:** `DriverService.java` → `lookupDriverByLicense()`
- **Mechanism:** Builds an LDAP filter string by concatenating user-supplied `licenseNumber` directly into the filter — `"(licenseNumber=" + licenseNumber + ")"` — allowing LDAP injection
- **CWE:** CWE-90

### 6.2 VULNERABILITY A06 — Vulnerable Log4j 2.14.1
- **Location:** `pom.xml` → Log4j dependency pinned to `2.14.1`
- **Mechanism:** Application uses Log4j 2.14.1 which is vulnerable to Log4Shell (CVE-2021-44228). User-controlled input (vehicle search queries) is logged directly via `logger.info("Searching for vehicle: " + userInput)`
- **CWE:** CWE-502 (via JNDI lookup)

### 6.3 VULNERABILITY A10 — SSRF in External Vehicle Data Fetch
- **Location:** `IntegrationController.java` → `fetchExternalVehicleData()`
- **Mechanism:** `GET /api/integrations/vehicle-data?url={url}` takes a user-supplied URL and fetches it server-side using `RestTemplate.getForObject(url, String.class)` with no URL validation or allowlist — allows SSRF to internal services and cloud metadata endpoints
- **CWE:** CWE-918

---

## 7. Chained Vulnerability Scenario

### Chain: "Log4Shell → SSRF → Lateral Movement"

An attacker triggers Log4Shell via a crafted vehicle search query to achieve initial code execution, then uses the SSRF endpoint to pivot to internal cloud metadata services and extract credentials for lateral movement.

| Step | Issue | Severity | OWASP |
|------|-------|----------|-------|
| 1 | Log4Shell triggered via user-controlled search input logged by Log4j 2.14.1 | Medium | A06 |
| 2 | SSRF endpoint used to reach cloud metadata (169.254.169.254) and extract IAM credentials | Medium | A10 |

**Impact:** `lateral_movement` — Attacker pivots from the application to cloud infrastructure using stolen IAM credentials.

---

## 8. Decoy Safe Patterns

- `VehicleRepository` uses parameterised Spring Data JPA queries for all vehicle lookups (safe)
- `MaintenanceController` properly validates service dates and cost inputs with `@Valid` and `@Positive` annotations
- `LocationService` sanitises latitude/longitude inputs to valid numeric ranges before storing

---

## 9. Checklist

- [ ] Spring Boot project compiles and starts
- [ ] Log4j 2.14.1 is explicitly pinned in `pom.xml`
- [ ] H2 database schema initialises correctly
- [ ] All REST endpoints functional
- [ ] LDAP injection in driver lookup is exploitable
- [ ] Log4Shell is triggerable via search input
- [ ] SSRF endpoint fetches arbitrary URLs
- [ ] Chain scenario is end-to-end exploitable
- [ ] Decoy patterns are in place
- [ ] `.vulns` manifest is complete and accurate
- [ ] README follows project template
- [ ] Dockerfile builds and runs
