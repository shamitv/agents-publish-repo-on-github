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
  │   ├── SecurityConfig.java          # 🐛 A07: session fixation
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
  │   ├── Passenger.java
  │   └── BoardingPass.java
  ├── repository/
  │   ├── FlightRepository.java        # Spring Data (safe)
  │   ├── FlightSearchDao.java         # 🐛 A03: raw SQL
  │   ├── BookingRepository.java
  │   └── PassengerRepository.java
  ├── service/
  │   ├── FlightService.java
  │   ├── BookingService.java          # 🐛 A04: no rate limit
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
  ├── application.yml
  ├── schema.sql
  └── data.sql
  ```

### 1.2 `application.yml`
```yaml
server:
  port: 8081
spring:
  datasource:
    url: jdbc:h2:mem:airlinedb
    driver-class-name: org.h2.Driver
  h2:
    console:
      enabled: false   # Disabled in this app (not an A05 issue here)
  jpa:
    hibernate:
      ddl-auto: none
    show-sql: true
```

---

## 2. Database Schema & Seed Data

### 2.1 Schema (`schema.sql`)
```sql
CREATE TABLE passengers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    passport_number VARCHAR(20),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'PASSENGER'  -- PASSENGER, AIRLINE_STAFF
);

CREATE TABLE flights (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    flight_number VARCHAR(10) NOT NULL,
    airline VARCHAR(100) NOT NULL,
    origin VARCHAR(3) NOT NULL,           -- IATA code
    destination VARCHAR(3) NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    total_seats INT NOT NULL,
    available_seats INT NOT NULL
);

CREATE TABLE seats (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    flight_id BIGINT REFERENCES flights(id),
    seat_number VARCHAR(4) NOT NULL,      -- e.g., "12A"
    seat_class VARCHAR(20) NOT NULL,      -- ECONOMY, BUSINESS, FIRST
    is_available BOOLEAN DEFAULT TRUE
);

CREATE TABLE bookings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pnr VARCHAR(6) UNIQUE NOT NULL,
    passenger_id BIGINT REFERENCES passengers(id),
    flight_id BIGINT REFERENCES flights(id),
    seat_id BIGINT REFERENCES seats(id),
    status VARCHAR(20) DEFAULT 'CONFIRMED', -- CONFIRMED, CANCELLED, CHECKED_IN
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_status VARCHAR(20) DEFAULT 'UNPAID'  -- 🐛 A04: no payment deadline enforced
);
```

### 2.2 Seed Data (`data.sql`)
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

#### `FlightSearchDao` — **🐛 A03: SQL Injection**
This is a custom DAO (not Spring Data) that builds search queries via string concatenation:

```java
@Repository
public class FlightSearchDao {
    @Autowired
    private JdbcTemplate jdbcTemplate;

    // VULNERABILITY: SQL injection via string concatenation
    public List<Flight> searchFlights(String origin, String destination, String date) {
        String sql = "SELECT * FROM flights WHERE origin = '" + origin
                   + "' AND destination = '" + destination
                   + "' AND CAST(departure_time AS DATE) = '" + date + "'";
        return jdbcTemplate.query(sql, new FlightRowMapper());
    }
}
```

#### Other Repositories (safe — decoy)
- `FlightRepository` — extends `JpaRepository`, uses `@Query` with named parameters
- `BookingRepository` — extends `JpaRepository`, includes `findByPnr()`, `findByPassengerId()`
- `PassengerRepository` — extends `JpaRepository`

### 3.3 Services

#### `FlightService`
- Delegates search to `FlightSearchDao` (carries the injection vuln through)
- `getFlightSeats(Long flightId)` — returns seat map
- Standard CRUD for AIRLINE_STAFF

#### `BookingService` — **🐛 A04: Insecure Design**
```java
@Service
public class BookingService {
    // VULNERABILITY: No rate limiting, no payment timeout, no concurrency control
    // A bot can call this repeatedly to reserve all seats without paying
    @Transactional
    public BookingResponse createBooking(BookingRequest request, Long passengerId) {
        Seat seat = seatRepository.findById(request.getSeatId())
            .orElseThrow(() -> new RuntimeException("Seat not found"));

        if (!seat.getIsAvailable()) {
            throw new RuntimeException("Seat already taken");
        }

        seat.setIsAvailable(false);  // Reserved immediately, no hold timeout
        seatRepository.save(seat);

        Booking booking = new Booking();
        booking.setPnr(pnrGenerator.generate());
        booking.setPassengerId(passengerId);
        booking.setFlightId(request.getFlightId());
        booking.setSeatId(seat.getId());
        booking.setPaymentStatus("UNPAID");  // No deadline to pay
        bookingRepository.save(booking);

        return new BookingResponse(booking.getPnr(), "CONFIRMED");
    }
}
```

#### `CheckInService`
- Validates 24h window before departure
- Updates booking status to CHECKED_IN
- Generates boarding pass data

#### `PnrGenerator`
- Generates 6-character alphanumeric PNR codes

### 3.4 Controllers

#### `HomeController`
- `GET /` → search page
- `POST /register` → passenger registration
- Thymeleaf rendering

#### `FlightController`
- `GET /api/flights/search?origin=X&destination=Y&date=Z` — **🐛 A03 — delegates to FlightSearchDao**
- `GET /api/flights/{id}/seats` — seat map JSON
- `GET /api/flights` — all flights (AIRLINE_STAFF)
- `PUT /api/flights/{id}` — update flight (AIRLINE_STAFF)

#### `BookingController`
- `POST /api/bookings` — **🐛 A04 — no rate limiting**
- `GET /api/bookings/{pnr}` — view booking (verifies ownership — safe)
- `PUT /api/bookings/{pnr}/cancel` — cancel booking
- `GET /api/bookings/history` — current user's bookings

#### `CheckInController`
- `POST /api/checkin/{pnr}` — perform check-in
- `GET /api/checkin/{pnr}/boardingpass` — HTML boarding pass

### 3.5 Security Configuration — **🐛 A07: Session Fixation**

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/register", "/api/flights/search",
                                 "/css/**", "/js/**").permitAll()
                .requestMatchers("/api/flights").hasRole("AIRLINE_STAFF")
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/")
                .loginProcessingUrl("/login")
                .defaultSuccessUrl("/dashboard")
            )
            // VULNERABILITY: Session fixation — session is NOT invalidated on login
            .sessionManagement(session -> session
                .sessionFixation().none()  // Disables session fixation protection!
            )
            .logout(LogoutConfigurer::permitAll);
        return http.build();
    }
}
```

By setting `.sessionFixation().none()`, Spring Security will **not** create a new session after authentication. If an attacker sets `JSESSIONID` cookie before the victim logs in, that same session becomes authenticated.

---

## 4. Frontend Implementation

### 4.1 Page Templates (Thymeleaf)

| Template | Route | Description |
|----------|-------|-------------|
| `home.html` | `/` | Flight search form + login |
| `register.html` | `/register` | Passenger registration form |
| `search-results.html` | `/flights/results` | Flight search results list |
| `seat-map.html` | `/flights/{id}/seats` | Interactive seat selection |
| `booking-confirm.html` | `/bookings/confirm` | Booking confirmation with PNR |
| `my-bookings.html` | `/bookings/history` | User's booking history |
| `checkin.html` | `/checkin/{pnr}` | Check-in flow |
| `boarding-pass.html` | `/checkin/{pnr}/pass` | Printable boarding pass |

### 4.2 JavaScript (vanilla)

#### `static/js/flight-search.js`
- Submits search form via `fetch()` to `/api/flights/search`
- Renders results dynamically
- **This is where the A03 injection flows from the UI** — user input goes directly to the vulnerable DAO

#### `static/js/seat-map.js`
- Fetches seat data from `/api/flights/{id}/seats`
- Renders a visual seat grid (table-based)
- Click-to-select with visual feedback
- Submits selected seat ID with booking request

#### `static/js/booking.js`
- Handles booking form submission
- Displays PNR confirmation
- **No client-side rate limiting either** — complementing the A04 backend flaw

### 4.3 CSS
- `static/css/main.css` — Airline-themed design (sky blue, white, clean sans-serif)
- Seat map styles (available = green, taken = red, selected = blue)
- Responsive layout for mobile check-in

---

## 5. Testing

### 5.1 Unit Tests
- `FlightServiceTest` — search, seat retrieval
- `BookingServiceTest` — booking creation, cancellation, PNR generation
- `CheckInServiceTest` — 24h window validation, status update

### 5.2 Integration Tests
- `FlightSearchInjectionTest` — **verify A03:** send `origin=' OR 1=1 --` and confirm all flights returned
- `SessionFixationTest` — **verify A07:** set JSESSIONID before login, verify session persists after auth
- `BookingRateLimitTest` — **verify A04:** rapidly create 50 bookings and confirm all succeed with UNPAID status

---

## 6. Vulnerability Manifest

Create `vulnerabilities.json`:
```json
{
  "app_id": "app-07",
  "app_name": "Airline Booking System",
  "language": "java",
  "framework": "spring-boot",
  "vulnerabilities": [
    {
      "owasp_id": "A03",
      "category": "Injection",
      "location": "src/main/java/com/airline/repository/FlightSearchDao.java",
      "method": "searchFlights",
      "line_range": "15-22",
      "description": "Flight search SQL query built via string concatenation with user-supplied origin, destination, and date values",
      "severity": "critical",
      "cwe": "CWE-89"
    },
    {
      "owasp_id": "A07",
      "category": "Identification and Authentication Failures",
      "location": "src/main/java/com/airline/config/SecurityConfig.java",
      "method": "filterChain",
      "line_range": "28-30",
      "description": "Session fixation protection disabled via sessionFixation().none() — session ID not rotated on login",
      "severity": "high",
      "cwe": "CWE-384"
    },
    {
      "owasp_id": "A04",
      "category": "Insecure Design",
      "location": "src/main/java/com/airline/service/BookingService.java",
      "method": "createBooking",
      "line_range": "20-42",
      "description": "No rate limiting, no payment timeout, no concurrency control on booking creation — allows inventory hoarding",
      "severity": "high",
      "cwe": "CWE-799"
    }
  ],
  "decoys": [
    {
      "location": "src/main/java/com/airline/config/SecurityConfig.java",
      "description": "BCryptPasswordEncoder — password hashing is SAFE"
    },
    {
      "location": "src/main/java/com/airline/repository/FlightRepository.java",
      "description": "Spring Data JPA with @Query and named params — NOT injectable"
    },
    {
      "location": "src/main/java/com/airline/controller/BookingController.java",
      "description": "PNR lookup validates ownership — access control is correct here"
    }
  ]
}
```

---

## 7. Dockerfile

```dockerfile
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## 8. Checklist

- [ ] Spring Boot project compiles and starts on port 8081
- [ ] All 13 API endpoints functional
- [ ] Flight search returns correct results for valid inputs
- [ ] Seat map renders and booking flow works end-to-end
- [ ] Check-in and boarding pass generation works
- [ ] **A03 verifiable:** `origin=' OR 1=1 --` in search returns all flights
- [ ] **A07 verifiable:** pre-set JSESSIONID survives login
- [ ] **A04 verifiable:** 50 rapid bookings all succeed with UNPAID status, exhausting seats
- [ ] Decoy patterns are genuinely safe
- [ ] `vulnerabilities.json` matches actual code
- [ ] Docker image builds and runs
