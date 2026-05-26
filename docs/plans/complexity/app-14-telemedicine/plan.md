# Complexity Upgrade Plan: app-14-telemedicine (Enterprise Architecture)

This document details the architectural plan to upgrade the Telemedicine Appointment System to an event-driven, multi-database TypeScript application.

## 1. Overview
The application will be restructured into a modular TypeScript MVC framework:
- **Polyglot Storage**: PostgreSQL for users (patients, doctors), appointments, and invoices; MongoDB for unstructured patient clinical progress notes.
- **Event Streaming**: Apache Kafka for background appointment notifications, billing workflows, and prescription log dispatching.
- **Complex Business Logic**: Overlap checks for doctor schedules, doctor availability rules, and billing refund policies.
- **Modular Codebase**: Split code into folders: `routes/`, `controllers/`, `services/`, `models/`, `consumers/`.
- **Enterprise UI**: An interactive clinic portal displaying appointment calendars, real-time consultation logs, and medical history documents.

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

## 4. Impact on Planted Vulnerabilities
- **VULN-01 (A01 - IDOR)**: The patient records/details lookup service (`ConsultationService`) retrieves notes from MongoDB. The controller (`controllers/patientController.ts`) fails to perform user validation checking, allowing any patient to pull clinical notes belonging to other patients.
- **VULN-02 (A02 - Cryptographic Failures)**: The JWT signing mechanism uses a weak secret or accepts the `none` algorithm. This weak validation remains active in the authentication service, allowing attackers to forge patient/doctor privileges and query PostgreSQL.
- **VULN-03 (A07 - Identification and Authentication Failures)**: The session validation logic relies on predictable session values stored in the Redis session cache. Session hijacking remains easily exploitable.
- **Chain-01 (Weak JWT Signatures → IDOR)**: Attacker signs a custom JWT with doctor privilege, submits it to endpoints, and accesses patient notes in MongoDB using IDOR.
- **Chain-02 (State Confusion Pivot to IDOR)**: Attacker exploits out-of-order execution states in Kafka scheduling topics to alter appointment details and view doctor reports.
