# Implementation Plan — App 06: Enterprise HR Management System

## 1. Project Scaffold

### 1.1 Initialise Spring Boot Project
- Use Spring Initializr (or `mvnw` archetype) with:
  - **Group:** `com.hr`
  - **Artifact:** `app-06-hr-management`
  - **Java:** 17
  - **Dependencies:** Spring Web, Spring Security, Spring Data JPA, H2 Database, Thymeleaf, Lombok, Validation
- Create standard Maven directory layout:
  ```
  src/main/java/com/hr/
  ├── App06Application.java
  ├── config/
  ├── controller/
  ├── model/
  ├── repository/
  ├── service/
  └── dto/
  src/main/resources/
  ├── templates/          # Thymeleaf HTML
  ├── static/             # JS, CSS
  ├── application.yml
  ├── schema.sql
  └── data.sql
  ```

### 1.2 Docker Setup
- Create `Dockerfile` (multi-stage: Maven build → JRE runtime)
- Create `.dockerignore`

---

## 2. Database Schema & Seed Data

### 2.1 Schema (`schema.sql`)
```sql
CREATE TABLE departments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_dept_id BIGINT REFERENCES departments(id)
);

CREATE TABLE employees (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,          -- EMPLOYEE, MANAGER, HR_ADMIN
    department_id BIGINT REFERENCES departments(id),
    manager_id BIGINT REFERENCES employees(id),
    hire_date DATE NOT NULL,
    ssn_encrypted VARCHAR(255),         -- 🐛 A02: XOR cipher with hard-coded key
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE salaries (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT REFERENCES employees(id),
    base_salary DECIMAL(12,2) NOT NULL,
    bonus DECIMAL(12,2) DEFAULT 0,
    effective_date DATE NOT NULL
);

CREATE TABLE leave_requests (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT REFERENCES employees(id),
    leave_type VARCHAR(20) NOT NULL,    -- VACATION, SICK, PERSONAL
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
    approver_id BIGINT REFERENCES employees(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 Seed Data (`data.sql`)
- 3 departments: Engineering, Sales, Human Resources
- 10+ employees across all 3 roles
- Salary records for each employee
- 5 sample leave requests in various states
- Passwords hashed with BCrypt (safe — decoy pattern)

---

## 3. Backend Implementation

### 3.1 Models & DTOs
| Class | Purpose |
|-------|---------|
| `Employee` | JPA entity — includes `ssnEncrypted` field with **XOR encryption helper** (🐛 A02) |
| `Department` | JPA entity with self-referencing parent |
| `Salary` | JPA entity linked to Employee |
| `LeaveRequest` | JPA entity with status workflow |
| `EmployeeDTO` | Response DTO (excludes password, includes masked SSN) |
| `PayrollDTO` | Salary + employee name for payroll responses |

### 3.2 Repositories (Spring Data JPA)
- `EmployeeRepository` — standard CRUD + `findByEmail()`, `findByDepartmentId()`, search by name
  - **All queries use parameterised Spring Data JPA** (decoy — NOT injectable)
- `SalaryRepository` — `findByEmployeeId()`, `findAllCurrentSalaries()`
- `LeaveRequestRepository` — `findByEmployeeId()`, `findByStatus()`
- `DepartmentRepository` — standard CRUD + tree query

### 3.3 Services

#### `EmployeeService`
- CRUD operations for employees
- `encryptSsn(String rawSsn)` / `decryptSsn(String encrypted)` — **🐛 A02: uses XOR with hard-coded key `0xDEADBEEF`**
  ```java
  // VULNERABILITY: Reversible XOR cipher with hard-coded key
  private static final int XOR_KEY = 0xDEADBEEF;
  public String encryptSsn(String ssn) {
      byte[] bytes = ssn.getBytes();
      byte[] keyBytes = ByteBuffer.allocate(4).putInt(XOR_KEY).array();
      for (int i = 0; i < bytes.length; i++) {
          bytes[i] ^= keyBytes[i % keyBytes.length];
      }
      return Base64.getEncoder().encodeToString(bytes);
  }
  ```

#### `PayrollService`
- `getSalaryByEmployeeId(Long employeeId)` — returns salary data
- `generateMonthlyReport()` — builds CSV of all salaries
- **No authorisation logic inside service** — relies (incorrectly) on controller

#### `EmployeeImportService`
- `importEmployees(InputStream fileStream)` — **🐛 A08: deserialises Java objects directly**
  ```java
  // VULNERABILITY: Insecure deserialization — no class filter
  public List<Employee> importEmployees(InputStream stream) throws Exception {
      ObjectInputStream ois = new ObjectInputStream(stream);
      List<Employee> employees = (List<Employee>) ois.readObject();
      ois.close();
      return employeeRepository.saveAll(employees);
  }
  ```

#### `LeaveService`
- Submit, approve/reject leave requests
- Validates date ranges, checks for overlapping requests
- Manager can only approve reports' requests (correctly implemented — decoy)

### 3.4 Controllers

#### `AuthController`
- `GET /` → login page
- `POST /login` → Spring Security form login
- `GET /dashboard` → redirect to role-appropriate dashboard view

#### `EmployeeController`
- `GET /api/employees` — list with search/filter (paginated)
- `GET /api/employees/{id}` — single employee detail
- `POST /api/employees` — create (HR_ADMIN only via `@PreAuthorize`)
- `PUT /api/employees/{id}` — update (HR_ADMIN only)
- `POST /api/employees/import` — **🐛 A08: accepts `.ser` file upload, passes to `EmployeeImportService`**

#### `PayrollController`  ← **🐛 A01 HERE**
- `GET /api/payroll/{employeeId}` — **Missing `@PreAuthorize` annotation. Any authenticated user can access any employee's salary.**
  ```java
  // VULNERABILITY: No authorization check — any authenticated user can view any salary
  @GetMapping("/api/payroll/{employeeId}")
  public ResponseEntity<PayrollDTO> getPayroll(@PathVariable Long employeeId) {
      return ResponseEntity.ok(payrollService.getSalaryByEmployeeId(employeeId));
  }
  ```
- `GET /api/payroll/report` — correctly restricted to HR_ADMIN

#### `LeaveController`
- Standard leave CRUD — correctly scoped to current user or manager's reports

#### `OrgChartController`
- `GET /api/org-chart` — returns hierarchical department/employee tree as JSON

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
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/")
                .defaultSuccessUrl("/dashboard")
            )
            .logout(LogoutConfigurer::permitAll);
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(); // SAFE — decoy pattern
    }
}
```
- Note: **CORS is not explicitly configured** — defaults to same-origin since frontend is served by same Spring Boot app via Thymeleaf. However, the REST API endpoints have no CORS headers, which becomes relevant if a separate frontend client is used.

---

## 4. Frontend Implementation

### 4.1 Page Templates (Thymeleaf)

| Template | Route | Description |
|----------|-------|-------------|
| `login.html` | `/` | Login form |
| `dashboard.html` | `/dashboard` | Role-based landing page with nav |
| `employees.html` | `/employees` | Employee directory with search |
| `employee-detail.html` | `/employees/{id}` | Single employee profile |
| `payroll.html` | `/payroll` | Salary viewer (calls REST API via JS) |
| `leave.html` | `/leave` | Leave request form + calendar |
| `org-chart.html` | `/org-chart` | Interactive org chart |

### 4.2 JavaScript (vanilla)
- `static/js/payroll.js` — Fetches `/api/payroll/{id}` via `fetch()` — demonstrates the A01 vuln from the browser
- `static/js/org-chart.js` — Renders org chart using DOM manipulation
- `static/js/leave-calendar.js` — Simple calendar view for leave dates

### 4.3 CSS
- `static/css/main.css` — Basic responsive layout, table styles, form styles
- Uses a clean corporate design (blues/grays, sans-serif font)

---

## 5. Testing

### 5.1 Unit Tests
- `EmployeeServiceTest` — CRUD, SSN encryption round-trip
- `PayrollServiceTest` — salary lookup, CSV generation
- `LeaveServiceTest` — submission, approval, overlap detection

### 5.2 Integration Tests
- `PayrollControllerTest` — **verify that the A01 bug exists**: an EMPLOYEE-role user successfully fetches another employee's salary
- `EmployeeImportTest` — verify `.ser` upload path works (demonstrates A08)

---

## 6. Vulnerability Manifest

Create `vulnerabilities.json`:
```json
{
  "app_id": "app-06",
  "app_name": "Enterprise HR Management System",
  "language": "java",
  "framework": "spring-boot",
  "vulnerabilities": [
    {
      "owasp_id": "A01",
      "category": "Broken Access Control",
      "location": "src/main/java/com/hr/controller/PayrollController.java",
      "method": "getPayroll",
      "line_range": "25-30",
      "description": "Payroll endpoint returns salary data for any employee to any authenticated user without role or ownership check",
      "severity": "high",
      "cwe": "CWE-639"
    },
    {
      "owasp_id": "A08",
      "category": "Software and Data Integrity Failures",
      "location": "src/main/java/com/hr/service/EmployeeImportService.java",
      "method": "importEmployees",
      "line_range": "18-24",
      "description": "Bulk employee import uses ObjectInputStream.readObject() on untrusted upload without class filtering",
      "severity": "critical",
      "cwe": "CWE-502"
    },
    {
      "owasp_id": "A02",
      "category": "Cryptographic Failures",
      "location": "src/main/java/com/hr/service/EmployeeService.java",
      "method": "encryptSsn",
      "line_range": "45-55",
      "description": "SSN encryption uses reversible XOR cipher with hard-coded key 0xDEADBEEF",
      "severity": "high",
      "cwe": "CWE-327"
    }
  ],
  "decoys": [
    {
      "location": "src/main/java/com/hr/config/SecurityConfig.java",
      "description": "BCryptPasswordEncoder with default strength — this is SAFE and should NOT be flagged"
    },
    {
      "location": "src/main/java/com/hr/repository/EmployeeRepository.java",
      "description": "Spring Data JPA parameterised queries — NOT injectable"
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
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## 8. Checklist

- [ ] Spring Boot project compiles and starts
- [ ] H2 console accessible at `/h2-console` (dev only)
- [ ] All 14 API endpoints functional
- [ ] Login/logout works with 3 roles
- [ ] Thymeleaf pages render correctly
- [ ] **A01 vuln verifiable:** EMPLOYEE can GET `/api/payroll/2` and see another employee's salary
- [ ] **A08 vuln verifiable:** uploading a crafted `.ser` file triggers deserialization
- [ ] **A02 vuln verifiable:** SSN can be decrypted by anyone who reads the source code
- [ ] Decoy patterns are genuinely safe
- [ ] `vulnerabilities.json` is accurate
- [ ] Docker image builds and runs
