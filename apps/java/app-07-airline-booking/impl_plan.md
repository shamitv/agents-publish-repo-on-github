# Implementation Plan — App 07: Airline Booking System

## 1. Project Scaffold

### 1.1 Initialise Spring Boot Project
- Spring Initializr settings:
  - **Group:** `com.airline`
  - **Artifact:** `app-07-airline-booking`
  - **Java:** 17
  - **Dependencies:** Spring Web, Spring Security, Spring Data JPA, H2 Database, Thymeleaf, Lombok, Validation
- Directory layout:
  ```
  src/main/java/com/airline/
  ├── App07Application.java
  ├── config/
  │   ├── SecurityConfig.java
  │   └── WebConfig.java
  ├── controller/
  │   ├── HomeController.java
  │   ├── FlightController.java
  │   ├── BookingController.java
  │   └── CheckInController.java
  ├── model/
  │   ├── Flight.java
  │   ├── Seat.java
  │   ├── Booking.java
  │   └── Passenger.java
  ├── repository/
  │   ├── FlightRepository.java
  │   ├── FlightSearchDao.java
  │   ├── BookingRepository.java
  │   └── PassengerRepository.java
  ├── service/
  │   ├── FlightService.java
  │   ├── BookingService.java
  │   ├── CheckInService.java
  │   └── PnrGenerator.java
  └── dto/
      ├── FlightSearchRequest.java
      ├── FlightSearchResult.java
      ├── BookingRequest.java
      └── BookingResponse.java
  src/main/resources/
  ├── templates/
  ├── static/
  ├── application.properties
  └── data.sql
  ```

### 1.2 `application.properties`
Let's use `application.properties` for maximum standard configuration ease.

---

## 2. Database Schema & Seed Data

Database entities are initialized directly via Hibernate auto-ddl generation to ensure smooth running. The data seeding is carried out by Spring Boot command line initializers on application start.

- 5 flights across various routes (JFK→LAX, LHR→CDG, etc.)
- 30 seats per flight (6 rows × 5 seats)
- 3 passengers (1 AIRLINE_STAFF, 2 PASSENGER)
- 2 existing bookings
- Passwords hashed with BCrypt (safe — decoy pattern)

---

## 3. Backend Implementation

### 3.1 Models
| Class | Purpose |
|-------|---------|
| `Passenger` | JPA entity — user account |
| `Flight` | JPA entity — flight details |
| `Seat` | JPA entity — individual seat on a flight |
| `Booking` | JPA entity — reservation linking passenger, flight, and seat |

### 3.2 Repositories
- `FlightSearchDao` — handles custom flight queries.
- `FlightRepository` — JpaRepository for Flight operations.
- `BookingRepository` — JpaRepository for Booking operations.
- `PassengerRepository` — JpaRepository for Passenger operations.

### 3.3 Services
- `FlightService` — manages flight retrieval and searching.
- `BookingService` — handles seat reservations and booking.
- `CheckInService` — updates check-in status and issues boarding passes.
- `PnrGenerator` — generates 6-character alphanumeric booking reference codes.

### 3.4 Controllers
- `HomeController` — UI rendering of search and landing pages.
- `FlightController` — flight querying and seat status JSON API.
- `BookingController` — reservation actions and customer booking history.
- `CheckInController` — handles check-in submissions and boarding pass views.

### 3.5 Security Configuration
Configures Spring Security filter chains, BCrypt encoders, custom auth providers, and standard login/logout form processing.

---

## 4. Frontend Implementation

### 4.1 Page Templates (Thymeleaf)
- `home.html` — Flight search form + login
- `register.html` — Passenger registration form
- `search-results.html` — Flight search results list
- `seat-map.html` — Interactive seat selection
- `booking-confirm.html` — Booking confirmation with PNR
- `my-bookings.html` — User's booking history
- `boarding-pass.html` — Printable boarding pass

---

## 5. Testing

### 5.1 Unit & Integration Tests
- `FlightServiceTest` — searches, seat mappings
- `BookingServiceTest` — booking creations, seat status alterations
- `CheckInServiceTest` — check-in workflows
- Comprehensive controllers tests checking routes accessibility and behavior

---

## 6. Vulnerability Manifest

Vulnerability manifest and metadata are stored in `.vulns` inside the application directory.

---

## 7. Dockerfile
A multi-stage build containerizing the Java application.
