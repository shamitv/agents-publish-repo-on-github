# App 07 — Airline Booking System

## Overview

A full-stack airline booking application built with **Spring Boot** (backend) and **Thymeleaf + vanilla JS** (frontend). The system supports flight search, seat selection, booking management, passenger check-in, and booking history.

This application intentionally contains **3 OWASP Top 10 vulnerabilities** for security-agent testing purposes.

---

## Business Domain

**Travel / Aviation** — Used by travellers to search and book flights, and by airline staff to manage inventory and check-in.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security |
| Frontend | Thymeleaf templates, vanilla JavaScript, HTML/CSS |
| Database | H2 (embedded, in-memory) |
| Build | Maven |
| Containerisation | Docker |

---

## Features

### Flight Search
- Search by origin, destination, date range, and passenger count
- Filter by airline, price range, number of stops
- Sort results by price, duration, or departure time

### Seat Selection & Booking
- Interactive seat map (rendered in JS)
- Passenger details form (name, passport, contact)
- Booking confirmation with PNR generation

### Booking Management
- View booking by PNR or user account
- Cancel / modify bookings
- Booking history for logged-in users

### Check-In
- Online check-in (24h before departure)
- Boarding pass generation (HTML-based)
- Seat reassignment during check-in

### Authentication
- Passenger registration / login
- Roles: `PASSENGER`, `AIRLINE_STAFF`
- Session-based authentication

---

## Planted Vulnerabilities

> **⚠️ These are intentional. Do not fix them — they are the test targets.**

| # | OWASP ID | Category | Location | Description | CWE |
|---|----------|----------|----------|-------------|-----|
| 1 | **A03** | Injection | `src/main/java/com/airline/repository/FlightSearchDao.java` | Flight search builds SQL query by **string concatenation** using user-supplied origin, destination, and date parameters. A crafted search input (e.g., `' OR 1=1 --`) can dump all flights or extract other tables. | CWE-89 |
| 2 | **A07** | Identification & Authentication Failures | `src/main/java/com/airline/config/SecurityConfig.java` | After successful login, the application **does not invalidate the old session** and does not issue a new session ID. This enables **session fixation attacks** — an attacker can set a known session cookie before the victim logs in and then hijack the authenticated session. | CWE-384 |
| 3 | **A04** | Insecure Design | `src/main/java/com/airline/service/BookingService.java` | There is **no rate limiting or concurrency control** on the booking endpoint. A single user (or bot) can reserve all seats on a flight without paying, effectively hoarding inventory. No hold timeout or payment deadline is enforced. | CWE-799 |

### Decoys (Safe Patterns)
- Passenger password storage uses `BCryptPasswordEncoder` — **safe**.
- The PNR lookup endpoint validates that the logged-in user owns the booking — **properly authorised** (not an A01 issue).
- Boarding pass generation uses parameterised templates — **no injection**.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Home / search page |
| POST | `/register` | — | Passenger registration |
| POST | `/login` | — | Login **(🐛 A07 — no session rotation)** |
| GET | `/api/flights/search` | — | **Flight search (🐛 A03 — SQL injection)** |
| GET | `/api/flights/{id}/seats` | ANY | Seat map for a flight |
| POST | `/api/bookings` | PASSENGER | **Create booking (🐛 A04 — no rate limit)** |
| GET | `/api/bookings/{pnr}` | PASSENGER | View booking (ownership verified) |
| PUT | `/api/bookings/{pnr}/cancel` | PASSENGER | Cancel booking |
| GET | `/api/bookings/history` | PASSENGER | User's booking history |
| POST | `/api/checkin/{pnr}` | PASSENGER | Online check-in |
| GET | `/api/checkin/{pnr}/boardingpass` | PASSENGER | Boarding pass |
| GET | `/api/flights` | AIRLINE_STAFF | All flights management |
| PUT | `/api/flights/{id}` | AIRLINE_STAFF | Update flight details |

---

## Running Locally

```bash
cd apps/java/app-07-airline-booking
./mvnw spring-boot:run
# Frontend served at http://localhost:8081
```

## Running via Docker

```bash
docker build -t app-07-airline-booking .
docker run -p 8081:8081 app-07-airline-booking
```

---

## Ground Truth

See `vulnerabilities.json` for machine-readable vulnerability manifest used for automated scoring.
