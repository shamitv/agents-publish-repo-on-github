# Implementation Plan — App 27: Hotel Reservation System

## 1. Overview

A Spring Boot hotel reservation system that manages room inventory, guest bookings, check-in/check-out, and rate management. Exposes REST APIs for the front desk, guests, and hotel administrators.

**Target OWASP vulnerabilities:** A03 (Injection), A05 (Security Misconfiguration), A07 (Identification & Auth Failures)

---

## 2. Business Domain

**Hospitality** — Used by hotel front-desk staff, reservation managers, and guests making online bookings.

## 3. Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security |
| Database | H2 (embedded, in-memory) |
| Build | Maven |
| Containerisation | Docker |

---

## 4. Project Scaffold

### 4.1 Package Layout
```
src/main/java/com/hotel/reservation/
├── App27Application.java
├── config/
│   └── SecurityConfig.java
├── controller/
│   ├── AuthController.java
│   ├── RoomController.java
│   ├── ReservationController.java
│   ├── GuestController.java
│   └── AdminController.java
├── model/
│   ├── Room.java
│   ├── Reservation.java
│   ├── Guest.java
│   ├── RoomRate.java
│   └── User.java
├── repository/
│   ├── RoomRepository.java
│   ├── ReservationRepository.java
│   ├── GuestRepository.java
│   └── RoomRateRepository.java
├── service/
│   ├── RoomService.java
│   ├── ReservationService.java
│   ├── GuestService.java
│   └── RateService.java
└── dto/
    ├── RoomDTO.java
    ├── ReservationDTO.java
    └── GuestDTO.java
```

---

## 5. Database Schema

### Tables
- **rooms** — id, room_number, floor, type (SINGLE/DOUBLE/SUITE/PENTHOUSE), status (AVAILABLE/OCCUPIED/MAINTENANCE), amenities
- **guests** — id, first_name, last_name, email, phone, id_document_number, loyalty_tier
- **reservations** — id, guest_id, room_id, check_in, check_out, status (CONFIRMED/CHECKED_IN/CHECKED_OUT/CANCELLED), total_amount
- **room_rates** — id, room_type, season, nightly_rate, effective_from, effective_to
- **users** — id, username, password, role (GUEST/FRONT_DESK/ADMIN), guest_id

### Seed Data
- 50 rooms across 4 types
- 20 guests with varying loyalty tiers
- 30+ reservations in various statuses
- Seasonal room rates
- Users across all 3 roles

---

## 6. Planned Vulnerabilities

### 6.1 VULNERABILITY A03 — JPQL Injection in Room Search
- **Location:** `RoomController.java` → `searchRooms()`
- **Mechanism:** Builds a JPQL query by concatenating user-supplied `roomType` and `amenities` parameters directly into the query string via `entityManager.createQuery()`
- **CWE:** CWE-89

### 6.2 VULNERABILITY A05 — Debug Endpoint Exposed in Production
- **Location:** `AdminController.java` → `getSystemInfo()`
- **Mechanism:** `GET /api/admin/debug` endpoint returns full system properties, environment variables (including DB credentials), and Spring bean details. Endpoint is mapped but has no authentication requirement due to a misconfigured security filter chain that permits `/api/admin/**`
- **CWE:** CWE-215

### 6.3 VULNERABILITY A07 — Session Fixation
- **Location:** `SecurityConfig.java`
- **Mechanism:** Session management is explicitly configured with `.sessionFixation().none()`, meaning the session ID is not regenerated after successful authentication — allows session fixation attacks
- **CWE:** CWE-384

---

## 7. Chained Vulnerability Scenario

### Chain: "Debug Info Leak → Session Fixation → Account Takeover"

An attacker discovers credentials from the debug endpoint, exploits session fixation to hijack an admin session, and gains full control of the reservation system.

| Step | Issue | Severity | OWASP |
|------|-------|----------|-------|
| 1 | Debug endpoint leaks environment variables including default admin credentials | Medium | A05 |
| 2 | Session fixation allows attacker to set a known session ID before admin logs in | Medium | A07 |

**Impact:** `account_takeover` — Attacker takes over the admin account and can modify reservations, rates, and guest data.

---

## 8. Decoy Safe Patterns

- `ReservationRepository` uses parameterised Spring Data JPA queries (safe — contrasts with the raw JPQL injection in `RoomController`)
- `GuestController` properly validates guest email format with `@Valid` annotation before processing
- Password reset endpoint correctly invalidates old tokens after use

---

## 9. Checklist

- [ ] Spring Boot project compiles and starts
- [ ] H2 database schema initialises correctly
- [ ] All REST endpoints functional
- [ ] JPQL injection in room search is exploitable
- [ ] Debug endpoint is accessible without auth
- [ ] Session fixation is exploitable
- [ ] Chain scenario is end-to-end exploitable
- [ ] Decoy patterns are in place
- [ ] `.vulns` manifest is complete and accurate
- [ ] README follows project template
- [ ] Dockerfile builds and runs
