# Implementation Plan — App 08: Warehouse Management System

## 1. Project Scaffold

### 1.1 Initialise Spring Boot Project
- Spring Initializr settings:
  - **Group:** `com.warehouse`
  - **Artifact:** `app-08-warehouse-mgmt`
  - **Java:** 17
  - **Dependencies:** Spring Web, Spring Security, Spring Data JPA, H2 Database, Lombok, Validation, Spring Boot Actuator, UnboundID LDAP SDK
- Directory layout:
  ```
  src/main/java/com/warehouse/
  ├── App08Application.java
  ├── config/
  │   ├── SecurityConfig.java
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
  │   ├── InventoryRepository.java
  │   ├── OrderRepository.java
  │   └── OrderItemRepository.java
  ├── service/
  │   ├── InventoryService.java
  │   ├── OrderService.java
  │   ├── EmployeeLdapService.java
  │   ├── ShippingService.java
  │   └── PickListService.java
  └── dto/
      ├── InventoryDTO.java
      ├── OrderDTO.java
      ├── EmployeeSearchResult.java
      ├── ShippingLabelRequest.java
      └── PickListDTO.java
  src/main/resources/
  ├── static/                         # Single Page Application Frontend
  │   ├── index.html
  │   ├── css/
  │   │   └── main.css
  │   └── js/
  │       └── app.js
  ├── application.properties
  └── ldap/
      └── warehouse.ldif              # Seed LDAP data
  ```

### 1.2 `application.properties`
Configures application ports, DB connection to H2, and Actuator metrics endpoints.

---

## 2. Database Schema & Seed Data

Database entities are initialized directly via Hibernate auto-ddl generation to ensure smooth running. The data seeding is carried out by Spring Boot command line initializers on application start.

- 25 inventory items across 5 aisles with realistic quantities
- 8 orders in various states (PENDING through SHIPPED)
- 3 users (one per role), passwords BCrypt-hashed
- Sample shipping labels for shipped orders

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
| `ShippingLabelRequest` | Request body with carrier info and label URL |

### 3.2 Repositories (Spring Data JPA)
- `InventoryRepository` — standard JPA repository for inventory operations.
- `OrderRepository` — standard JPA repository for order operations.
- `OrderItemRepository` — standard JPA repository for order items operations.

### 3.3 Services
- `InventoryService` — processes items and logs threshold quantities.
- `OrderService` — moves orders through standard statuses (PENDING -> PICKING -> PACKED -> SHIPPED).
- `PickListService` — sorts and batches pick lists by aisle groupings.
- `EmployeeLdapService` — communicates with embedded directory for personnel listings.
- `ShippingService` — downloads label files from carriers.

### 3.4 Controllers
- `DashboardController` — handles landing KPIs and stock summary.
- `InventoryController` — items CRUD operations.
- `OrderController` — orders list and packing/shipping status updates.
- `EmployeeController` — personnel searches.
- `ShippingController` — fetches carrier label files.

### 3.5 Security Configuration
Forms authentications, configures endpoints authorization rules, security beans, and secure standard Bcrypt encodings.

---

## 4. Frontend SPA Implementation

Driven by a Single Page Application (SPA) stack built in client-side HTML, CSS, and modular JS, decoupled completely from the server-side templates.

---

## 5. Testing

Comprehensive unit and integration test suites checking:
- CRUD actions
- Actuator accessibility
- LDAP query parameters behavior
- URL downloader handlers
