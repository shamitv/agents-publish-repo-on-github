# Complexity Upgrade Plan: app-14-telemedicine (Enterprise Architecture)

This document details the architectural plan to upgrade the Telemedicine Appointment System to an event-driven, multi-database TypeScript application.

## 1. Overview
The application will be restructured into a modular TypeScript MVC framework:
- **Polyglot Storage**: PostgreSQL for users (patients, doctors), appointments, and invoices; MongoDB for unstructured patient clinical progress notes.
- **Event Streaming**: Apache Kafka for background appointment notifications, billing workflows, and prescription log dispatching.
- **Complex Business Logic**: Overlap checks for doctor schedules, doctor availability rules, and billing refund policies.
- **Modular Codebase**: Split code into folders: `routes/`, `controllers/`, `services/`, `models/`, `consumers/`.
- **Enterprise UI**: Patient/Doctor portal displaying appointment calendars, real-time consultation logs, and medical history documents.

---

## 2. Component Design

### A. Database Layer (PostgreSQL & MongoDB)
- **PostgreSQL**: Stores relational tables (`users`, `doctors`, `appointments`, `billing`).
- **MongoDB**: Stores unstructured patient consultation notes (contains flexible fields: symptoms, diagnosis, prescribed medicines, doctor comments).

### B. Event Streaming (Apache Kafka)
- **Engine**: Apache Kafka
- **Role**: Dispatches async notifications and processes prescription records.
- **Work Flow**:
  1. Patient books a new appointment or doctor logs a consultation note.
  2. The endpoint publishes an `appointment-created` or `consultation-completed` event to the Kafka topic.
  3. The `NotificationConsumer` reads the event, formats patient reminders, and writes logs to PostgreSQL.
  4. The `PrescriptionConsumer` reads completed consultations and sends details to local pharmacies.

---

## 3. Modular Code Structure
```
src/
├── config/             # DB client pool and Kafka configurations
├── controllers/        # REST controllers (AppointmentController, PatientController)
├── routes/             # Route mapping definitions
├── services/           # ScheduleValidator, BillingEngine, ConsultationService
├── models/             # Relational mapping models and MongoDB schemas
├── consumers/          # Kafka event listeners (NotificationConsumer, PrescriptionConsumer)
├── public/             # Patient/Doctor interactive clinic dashboard
└── server.ts           # Express setup and app initialization
```

---

## 4. Vulnerabilities & Exploit Chains Detail

### Standalone Vulnerabilities
- **VULN-01 (A01 - IDOR on Consultation Notes)**:
  - *Location*: `src/controllers/patientController.ts` → `getPatientNotes()`
  - *Description*: Patient consultation notes endpoint reads records from MongoDB by ID. It fails to check if the patient ID inside the session matches the patient ID of the requested note document.
  - *Decoy Safeguard*: The user registration validations require matching signature parameters.
- **VULN-02 (A02 - Weak JWT Token Validation)**:
  - *Location*: `src/services/AuthService.ts` → `verifyToken()`
  - *Description*: The JWT verification middleware accepts tokens signed with a weak secret or configured with the insecure `none` algorithm.
- **VULN-03 (A07 - Insecure Session Handling)**:
  - *Location*: `src/controllers/authController.ts`
  - *Description*: Session cookie definitions omit the `httpOnly` flag, permitting cookie reading via client-side scripts.

### Exploit Chains
#### chain-01: Weak JWT Validation -> Patient Notes IDOR
- **Impact**: `db_exfiltration`
- **Attack narrative**: An attacker forges a JWT accepted by the weak token verifier, assigns themselves doctor or patient privileges in the token claims, and calls the patient notes endpoint with another patient's note ID to retrieve MongoDB clinical records because ownership is not checked.

| Step | Issue | Severity (standalone) | OWASP | CWE | Location | Method |
|------|-------|-----------------------|-------|-----|----------|--------|
| 1 | JWT verifier accepts weakly signed or `none` algorithm tokens. | Medium | A02 | CWE-347 | `src/services/AuthService.ts` | `verifyToken()` |
| 2 | Patient notes endpoint retrieves documents by ID without verifying patient ownership. | Medium | A01 | CWE-639 | `src/controllers/patientController.ts` | `getPatientNotes()` |

---

## 5. Benchmark Metadata Requirements
- **Source Annotations Required**: Source code must retain the `AGENTS.md` benchmark comments: `// VULNERABILITY <OWASP_ID>: <brief description>` for each standalone vulnerability and `// CHAIN LINK <N> (chain-<ID>): <description>` for every chain step.
- **Metadata Synchronization**: `.vulns`, the README chain section, this plan's chain table, and source comments must agree on OWASP ID, severity, CWE, impact, location, and method.
- **README Chain Section Required**: The app README must keep the required `Chained Vulnerability Scenario` section. `scenarios.md` may provide supplemental narrative, but it must not replace README or `.vulns` content.
- **Decoys Required**: Preserve nearby safe decoy patterns and list them in `.vulns.decoys`.
