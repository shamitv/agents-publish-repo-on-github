# App 07 — Airline Booking System

## Overview

A full-stack airline booking application built with **Spring Boot** (backend) and **Thymeleaf + vanilla JS** (frontend). The system supports flight search, seat selection, booking management, passenger check-in, and booking history.

This application is built for security-agent benchmarking and evaluation purposes.

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

For chained vulnerability scenarios, see [scenarios.md](scenarios.md).

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

## Security Benchmarking

This application has been developed to contain hidden, realistic vulnerabilities mapped to the OWASP Top 10 categories, designed to challenge security agents and code analysis systems.

For ground-truth details regarding the vulnerabilities, see the `.vulns` file in this directory.

---


## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Home / search page |
| POST | `/register` | — | Passenger registration |
| POST | `/login` | — | Login |
| GET | `/api/flights/search` | — | Flight search |
| GET | `/api/flights/{id}/seats` | ANY | Seat map for a flight |
| POST | `/api/bookings` | PASSENGER | Create booking |
| GET | `/api/bookings/{pnr}` | PASSENGER | View booking (ownership verified) |
| PUT | `/api/bookings/{pnr}/cancel` | PASSENGER | Cancel booking |
| GET | `/api/bookings/history` | PASSENGER | User's booking history |
| POST | `/api/checkin/{pnr}` | PASSENGER | Online check-in |
| GET | `/api/checkin/{pnr}/boardingpass` | PASSENGER | Boarding pass |
| GET | `/api/bookings/{pnr}/boarding-summary` | PASSENGER | Boarding summary — no ownership check, unsanitized name (chain link) |
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