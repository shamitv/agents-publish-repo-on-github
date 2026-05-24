# Implementation Plan — App 09: Legal Document Management System

## 1. Project Scaffold

### 1.1 Initialise Spring Boot Project
- Spring Initializr settings:
  - **Group:** `com.legal`
  - **Artifact:** `app-09-legal-documents`
  - **Java:** 17
  - **Dependencies:** Spring Web, Spring Security, Spring Data JPA, H2 Database, Lombok, Validation, Apache Log4j 2 Core
- Directory layout:
  ```
  src/main/java/com/legal/
  ├── App09Application.java
  ├── config/
  │   ├── SecurityConfig.java
  │   └── DataInitializer.java
  ├── controller/
  │   ├── UserController.java
  │   ├── CaseController.java
  │   └── DocumentController.java
  ├── model/
  │   ├── LegalCase.java
  │   ├── Document.java
  │   └── User.java
  ├── repository/
  │   ├── CaseRepository.java
  │   ├── DocumentRepository.java
  │   └── UserRepository.java
  ├── dto/
  │   ├── CaseDTO.java
  │   └── DocumentRequest.java
  └── service/
      ├── CaseService.java
      └── DocumentService.java
  src/main/resources/
  ├── static/                         # Portal Single Page Application Frontend
  │   ├── index.html
  │   ├── css/
  │   │   └── main.css
  │   └── js/
  │       └── app.js
  └── application.properties
  ```

### 1.2 `application.properties`
Configures server port 8083, DB connection to H2, and standard hibernate DDL generation.

---

## 2. Database Schema & Seed Data

Entities are constructed with direct Hibernate mappings and seeded programmatically on application start:
- 4 active legal cases (corporate lawsuits, tax audit briefs, mergers).
- 10 sensitive legal documents (NDA agreements, brief sheets, depositions) containing realistic corporate counsel transcripts.
- 4 users:
  - `attorney` / `attorney123` (Attorney role)
  - `client_acme` / `client123` (Client role, owns Case 1)
  - `client_zenith` / `client123` (Client role, owns Case 2)
  - `admin` / `admin123` (Administrator role)

---

## 3. Backend Implementation

### 3.1 Models & DTOs
*   `LegalCase`: Case files catalog tracking title, description, client owner, and status (ACTIVE, CLOSED).
*   `Document`: Represents uploaded court filings, briefs, and client NDA documentation.
*   `User`: System logins mapped to role assignments.

### 3.2 Repositories
Standard JPA repositories for users, cases, and documents.

### 3.3 Services
*   `CaseService`: Fetches legal cases and validates active statuses.
*   `DocumentService`: Manages file submissions and catalog storage.

### 3.4 Controllers
*   `UserController`: Endpoint validating active profiles.
*   `CaseController`: Access controls restricted via standard roles.
*   `DocumentController`: Document query and upload endpoints.

---

## 4. Frontend SPA Portal

Decoupled Single Page Application interface served directly from static resources using HTML5, dynamic JavaScript routing, and custom CSS elements matching legal court boardrooms.

---

## 5. Testing

Standard JUnit test suites verifying:
- Safe authentication and BCrypt password encryption checks.
- Document storage validation rules.
- Case listing and metadata retrieval workflows.
