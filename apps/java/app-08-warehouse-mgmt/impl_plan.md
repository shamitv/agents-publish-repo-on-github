# Implementation Plan — App 08: Warehouse Management System

## 1. Project Scaffold

### 1.1 Initialise Spring Boot Project
- Spring Initializr settings:
  - **Group:** `com.warehouse`
  - **Artifact:** `app-08-warehouse-mgmt`
  - **Java:** 17
  - **Dependencies:** Spring Web, Spring Security, Spring Data JPA, H2 Database, Thymeleaf, Lombok, Validation, **Spring Boot Actuator**, **UnboundID LDAP SDK**
- Directory layout:
  ```
  src/main/java/com/warehouse/
  ├── App08Application.java
  ├── config/
  │   ├── SecurityConfig.java
  │   ├── ActuatorConfig.java          # 🐛 A05: exposes all actuator endpoints
  │   ├── LdapConfig.java             # Embedded LDAP setup
  │   └── WebConfig.java
  ├── controller/
  │   ├── DashboardController.java
  │   ├── InventoryController.java
  │   ├── OrderController.java
  │   ├── EmployeeController.java
  │   └── ShippingController.java
  ├── model/
  │   ├── InventoryItem.java
  │   ├── WarehouseOrder.java
  │   ├── OrderItem.java
  │   ├── Employee.java               # LDAP-mapped
  │   └── ShippingLabel.java
  ├── repository/
  │   ├── InventoryRepository.java    # Spring Data JPA (safe — decoy)
  │   ├── OrderRepository.java
  │   └── OrderItemRepository.java
  ├── service/
  │   ├── InventoryService.java
  │   ├── OrderService.java
  │   ├── EmployeeLdapService.java    # 🐛 A03: LDAP injection
  │   ├── ShippingService.java        # 🐛 A10: SSRF
  │   └── PickListService.java
  └── dto/
      ├── InventoryDTO.java
      ├── OrderDTO.java
      ├── EmployeeSearchResult.java
      ├── ShippingLabelRequest.java
      └── PickListDTO.java
  src/main/resources/
  ├── templates/
  ├── static/
  ├── application.yml                 # 🐛 A05: actuator exposure
  ├── schema.sql
  ├── data.sql
  └── ldap/
      └── warehouse.ldif              # Seed LDAP data
  ```

### 1.2 `application.yml` — **🐛 A05: Security Misconfiguration**
```yaml
server:
  port: 8082

spring:
  datasource:
    url: jdbc:h2:mem:warehousedb
    driver-class-name: org.h2.Driver
  h2:
    console:
      enabled: false
  jpa:
    hibernate:
      ddl-auto: none

# VULNERABILITY: All actuator endpoints exposed without authentication
management:
  endpoints:
    web:
      exposure:
        include: "*"          # Exposes ALL actuator endpoints
  endpoint:
    env:
      show-values: ALWAYS     # Shows actual env variable values
    health:
      show-details: always
    heapdump:
      enabled: true           # Allows downloading JVM heap dump
```

---

## 2. Database Schema & Seed Data

### 2.1 Schema (`schema.sql`)
```sql
CREATE TABLE inventory_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    quantity INT NOT NULL DEFAULT 0,
    min_quantity INT NOT NULL DEFAULT 10,  -- low-stock threshold
    aisle VARCHAR(5),
    shelf VARCHAR(5),
    bin VARCHAR(5),
    weight_kg DECIMAL(8,2),
    unit_price DECIMAL(10,2),
    last_restocked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE warehouse_orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_name VARCHAR(200),
    customer_address TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, PICKING, PACKED, SHIPPED
    assigned_operator VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_at TIMESTAMP
);

CREATE TABLE order_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT REFERENCES warehouse_orders(id),
    inventory_item_id BIGINT REFERENCES inventory_items(id),
    quantity INT NOT NULL,
    picked BOOLEAN DEFAULT FALSE
);

CREATE TABLE shipping_labels (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT REFERENCES warehouse_orders(id),
    carrier VARCHAR(50),
    tracking_number VARCHAR(50),
    label_url VARCHAR(500),             -- 🐛 A10: user-supplied URL fetched by server
    label_data BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL           -- OPERATOR, SUPERVISOR, ADMIN
);
```

### 2.2 Seed Data (`data.sql`)
- 25 inventory items across 5 aisles with realistic quantities
- 8 orders in various states (PENDING through SHIPPED)
- 3 users (one per role), passwords BCrypt-hashed
- Sample shipping labels for shipped orders

### 2.3 LDAP Seed Data (`ldap/warehouse.ldif`)
```ldif
dn: dc=warehouse,dc=local
objectClass: top
objectClass: domain
dc: warehouse

dn: ou=employees,dc=warehouse,dc=local
objectClass: organizationalUnit
ou: employees

dn: uid=jsmith,ou=employees,dc=warehouse,dc=local
objectClass: inetOrgPerson
uid: jsmith
cn: John Smith
sn: Smith
mail: jsmith@warehouse.local
title: Warehouse Operator
departmentNumber: Operations

dn: uid=mjones,ou=employees,dc=warehouse,dc=local
objectClass: inetOrgPerson
uid: mjones
cn: Maria Jones
sn: Jones
mail: mjones@warehouse.local
title: Shift Supervisor
departmentNumber: Operations

# ... 8 more employees across departments
```

---

## 3. Backend Implementation

### 3.1 Models & DTOs
| Class | Purpose |
|-------|---------|
| `InventoryItem` | JPA entity — warehouse item with location and quantity |
| `WarehouseOrder` | JPA entity — customer order with status lifecycle |
| `OrderItem` | JPA entity — line item in an order |
| `ShippingLabel` | JPA entity — generated label with tracking info |
| `Employee` | POJO mapped from LDAP attributes |
| `InventoryDTO` | API response DTO |
| `ShippingLabelRequest` | Request body with `carrierLabelUrl` field (🐛 A10) |

### 3.2 Repositories (Spring Data JPA — all safe)
- `InventoryRepository` — `findBySku()`, `findByQuantityLessThan()`, search by name (using `@Query` with params — **decoy**)
- `OrderRepository` — `findByStatus()`, `findByOrderNumber()`
- `OrderItemRepository` — `findByOrderId()`

### 3.3 Services

#### `InventoryService`
- CRUD for inventory items
- Low-stock alert calculation (`quantity < minQuantity`)
- All queries via Spring Data JPA parameterised methods — **safe**

#### `OrderService`
- Order lifecycle management
- Status transitions with validation (can't skip states)
- Quantity deduction on PACKED status
- `@PreAuthorize` on status changes — **correctly authorised (decoy)**

#### `PickListService`
- Generates pick lists grouped by aisle for efficient warehouse traversal
- Returns ordered list of items with locations

#### `EmployeeLdapService` — **🐛 A03: LDAP Injection**

```java
@Service
public class EmployeeLdapService {
    @Autowired
    private LdapTemplate ldapTemplate;

    // VULNERABILITY: LDAP filter injection via string concatenation
    public List<Employee> searchEmployees(String searchTerm) {
        // User input directly concatenated into LDAP filter
        String filter = "(&(objectClass=inetOrgPerson)(|(cn=*" + searchTerm + "*)(uid=*" + searchTerm + "*)))";

        return ldapTemplate.search(
            "ou=employees",
            filter,
            new EmployeeAttributesMapper()
        );
    }
}
```

**Attack vector:** A search input like `*)(uid=*))(|(uid=*` breaks out of the intended filter, allowing an attacker to:
- Enumerate all employees regardless of search scope
- Extract attributes not normally returned (e.g., `userPassword`)
- Determine valid usernames for credential-stuffing attacks

#### `ShippingService` — **🐛 A10: SSRF**

```java
@Service
public class ShippingService {
    // VULNERABILITY: Server-side request forgery — no URL validation
    public byte[] generateLabel(ShippingLabelRequest request) {
        try {
            // User-supplied URL fetched directly by the server
            URL url = new URL(request.getCarrierLabelUrl());
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(5000);
            conn.setReadTimeout(5000);

            // No validation of:
            // - URL scheme (allows file://, gopher://)
            // - Host (allows 169.254.169.254, localhost, internal IPs)
            // - Port (allows probing any internal port)

            InputStream is = conn.getInputStream();
            byte[] labelData = is.readAllBytes();
            is.close();

            // Store label data in DB
            ShippingLabel label = new ShippingLabel();
            label.setOrderId(request.getOrderId());
            label.setCarrier(request.getCarrier());
            label.setLabelUrl(request.getCarrierLabelUrl());
            label.setLabelData(labelData);
            shippingLabelRepository.save(label);

            return labelData;
        } catch (Exception e) {
            throw new RuntimeException("Failed to fetch shipping label", e);
        }
    }
}
```

**Attack vectors:**
- `http://169.254.169.254/latest/meta-data/` — AWS metadata exfiltration
- `http://localhost:8082/actuator/env` — chain with A05 to read internal config
- `http://192.168.1.0:6379/` — probe internal Redis/services
- `file:///etc/passwd` — local file read (if `file://` scheme allowed)

### 3.4 Controllers

#### `DashboardController`
- `GET /dashboard` — renders role-based dashboard with low-stock alerts, pending orders count

#### `InventoryController`
- Full CRUD endpoints for inventory
- Search/filter endpoint using parameterised queries (safe)
- `@PreAuthorize` for write operations

#### `OrderController`
- Order listing, detail, status updates
- Pick list generation
- `@PreAuthorize("hasAnyRole('OPERATOR','SUPERVISOR','ADMIN')")` on status changes

#### `EmployeeController`
- `GET /api/employees/search?q=` — **delegates to `EmployeeLdapService.searchEmployees()` (🐛 A03)**
- Returns list of matching employees

#### `ShippingController`
- `POST /api/shipping/label` — accepts `ShippingLabelRequest` with `carrierLabelUrl` field — **🐛 A10**
- Returns generated label as PDF/image bytes

### 3.5 Security Configuration

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/login", "/css/**", "/js/**").permitAll()
                // VULNERABILITY A05: Actuator endpoints NOT listed here — defaults to permitAll
                // because they are not explicitly secured
                .requestMatchers("/actuator/**").permitAll()
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/")
                .loginProcessingUrl("/login")
                .defaultSuccessUrl("/dashboard")
            )
            .sessionManagement(session -> session
                .sessionFixation().migrateSession()  // Session fixation properly handled (safe)
            )
            .logout(LogoutConfigurer::permitAll);
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();  // SAFE — decoy
    }
}
```

### 3.6 LDAP Configuration

```java
@Configuration
public class LdapConfig {
    @Bean
    public LdapContextSource contextSource() {
        LdapContextSource ctx = new LdapContextSource();
        ctx.setUrl("ldap://localhost:8389");
        ctx.setBase("dc=warehouse,dc=local");
        return ctx;
    }

    @Bean
    public LdapTemplate ldapTemplate(LdapContextSource contextSource) {
        return new LdapTemplate(contextSource);
    }
}
```

Use `spring-boot-starter-data-ldap` with embedded UnboundID server for self-contained testing.

---

## 4. Frontend Implementation

### 4.1 Page Templates (Thymeleaf)

| Template | Route | Description |
|----------|-------|-------------|
| `login.html` | `/` | Login page |
| `dashboard.html` | `/dashboard` | Overview: low-stock alerts, pending orders, quick actions |
| `inventory.html` | `/inventory` | Inventory list with search, add, edit |
| `inventory-detail.html` | `/inventory/{id}` | Single item view with location and stock history |
| `orders.html` | `/orders` | Order list with status filters |
| `order-detail.html` | `/orders/{id}` | Order items, pick list, status update |
| `employees.html` | `/employees` | Employee directory search (🐛 A03 flows from here) |
| `shipping.html` | `/shipping` | Label generation form (🐛 A10 flows from here) |

### 4.2 JavaScript (vanilla)

#### `static/js/inventory.js`
- Real-time search filtering with debounce
- Low-stock items highlighted in red
- Inline editing for quantity updates

#### `static/js/orders.js`
- Status filter tabs (PENDING / PICKING / PACKED / SHIPPED)
- Status update via PATCH request
- Pick list view with checkbox tracking

#### `static/js/employee-search.js`
- Submits search query to `/api/employees/search?q=`
- Renders results in a table
- **User input flows directly to LDAP filter** (🐛 A03)

#### `static/js/shipping.js`
- Form with fields: Order ID, Carrier, Carrier Label URL
- Submits to `/api/shipping/label`
- Displays returned label as embedded image
- **URL field value sent directly to server for fetching** (🐛 A10)

### 4.3 CSS
- `static/css/main.css` — Industrial/warehouse theme (dark grays, orange accents, monospace for codes)
- Inventory table with location codes
- Status badges with colour coding
- Responsive grid layout

---

## 5. Testing

### 5.1 Unit Tests
- `InventoryServiceTest` — CRUD, low-stock detection
- `OrderServiceTest` — lifecycle management, state validation
- `PickListServiceTest` — aisle grouping, ordering

### 5.2 Integration Tests

#### `ActuatorExposureTest` — **verify A05**
```java
@Test
void actuatorEnvShouldBePubliclyAccessible() {
    // Unauthenticated request to actuator/env should return 200
    ResponseEntity<String> response = restTemplate.getForEntity("/actuator/env", String.class);
    assertEquals(200, response.getStatusCodeValue());
    assertTrue(response.getBody().contains("spring.datasource"));
}

@Test
void actuatorHeapdumpShouldBeAccessible() {
    ResponseEntity<byte[]> response = restTemplate.getForEntity("/actuator/heapdump", byte[].class);
    assertEquals(200, response.getStatusCodeValue());
}
```

#### `LdapInjectionTest` — **verify A03**
```java
@Test
void ldapInjectionShouldReturnAllEmployees() {
    // Inject LDAP filter to bypass search restriction
    String maliciousInput = "*)(uid=*))(|(uid=*";
    ResponseEntity<List> response = authenticatedRequest()
        .getForEntity("/api/employees/search?q=" + maliciousInput, List.class);
    assertEquals(200, response.getStatusCodeValue());
    // Should return ALL employees, not just matching ones
    assertTrue(response.getBody().size() > 5);
}
```

#### `SsrfTest` — **verify A10**
```java
@Test
void ssrfShouldFetchInternalUrl() {
    ShippingLabelRequest request = new ShippingLabelRequest();
    request.setOrderId(1L);
    request.setCarrier("TestCarrier");
    // Attempt to fetch actuator env (internal endpoint)
    request.setCarrierLabelUrl("http://localhost:8082/actuator/env");

    ResponseEntity<byte[]> response = authenticatedRequest()
        .postForEntity("/api/shipping/label", request, byte[].class);
    assertEquals(200, response.getStatusCodeValue());
    // Response body contains actuator env data — SSRF successful
    String body = new String(response.getBody());
    assertTrue(body.contains("spring.datasource"));
}
```

---

## 6. Vulnerability Manifest

Create `vulnerabilities.json`:
```json
{
  "app_id": "app-08",
  "app_name": "Warehouse Management System",
  "language": "java",
  "framework": "spring-boot",
  "vulnerabilities": [
    {
      "owasp_id": "A05",
      "category": "Security Misconfiguration",
      "location": "src/main/resources/application.yml",
      "method": null,
      "line_range": "15-25",
      "description": "Spring Boot Actuator endpoints (env, heapdump, beans, mappings) exposed publicly without authentication via management.endpoints.web.exposure.include=*",
      "severity": "high",
      "cwe": "CWE-16",
      "secondary_location": "src/main/java/com/warehouse/config/SecurityConfig.java"
    },
    {
      "owasp_id": "A03",
      "category": "Injection",
      "location": "src/main/java/com/warehouse/service/EmployeeLdapService.java",
      "method": "searchEmployees",
      "line_range": "15-22",
      "description": "LDAP filter constructed via string concatenation with user-supplied search term, enabling LDAP injection to enumerate all employees or extract hidden attributes",
      "severity": "high",
      "cwe": "CWE-90"
    },
    {
      "owasp_id": "A10",
      "category": "Server-Side Request Forgery (SSRF)",
      "location": "src/main/java/com/warehouse/service/ShippingService.java",
      "method": "generateLabel",
      "line_range": "12-35",
      "description": "Shipping label URL fetched server-side via HttpURLConnection with no scheme, host, or port validation — allows access to cloud metadata, internal services, and local files",
      "severity": "critical",
      "cwe": "CWE-918"
    }
  ],
  "decoys": [
    {
      "location": "src/main/java/com/warehouse/repository/InventoryRepository.java",
      "description": "Spring Data JPA with parameterised @Query — NOT injectable"
    },
    {
      "location": "src/main/java/com/warehouse/config/SecurityConfig.java",
      "description": "BCryptPasswordEncoder — password hashing is SAFE"
    },
    {
      "location": "src/main/java/com/warehouse/controller/OrderController.java",
      "description": "@PreAuthorize on status change endpoints — access control is correct"
    },
    {
      "location": "src/main/java/com/warehouse/config/SecurityConfig.java",
      "description": "Session fixation protection set to migrateSession() — properly configured"
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
EXPOSE 8082
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## 8. Checklist

- [ ] Spring Boot project compiles and starts on port 8082
- [ ] Embedded LDAP server starts with seed data
- [ ] All 17 API endpoints functional
- [ ] Inventory CRUD works with search
- [ ] Order lifecycle (PENDING → SHIPPED) works
- [ ] Employee search returns LDAP results
- [ ] Shipping label generation fetches URL and stores label
- [ ] **A05 verifiable:** `curl http://localhost:8082/actuator/env` returns config (unauthenticated)
- [ ] **A05 verifiable:** `curl http://localhost:8082/actuator/heapdump` downloads heap dump
- [ ] **A03 verifiable:** LDAP injection input returns all employees
- [ ] **A10 verifiable:** SSRF fetches `http://localhost:8082/actuator/env` via label URL → returns config data
- [ ] **A10 + A05 chain verifiable:** SSRF can be used to exfiltrate actuator data
- [ ] Decoy patterns are genuinely safe
- [ ] `vulnerabilities.json` matches actual code
- [ ] Docker image builds and runs
