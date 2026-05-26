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
- **Chain-01 (EASY to Find & Exploit)**: *JWT Forgery → IDOR Patient Notes*
  - *Narrative*: Attacker creates a forged JWT configured with the `none` algorithm and doctor permissions. They submit this token to authenticate and call `/api/patients/notes/:id` to retrieve another patient's medical details from MongoDB.
  - *Subtlety*: Low. Accept-none JWT vulnerabilities are easily flagged by security scanners.
- **Chain-02 (HARD to Find & Exploit)**: *Session Hijack → Kafka State Race → Prescription Injection*
  - *Narrative*: Attacker exploits the missing `httpOnly` cookie flag via a cross-site script to extract the patient's session token. They then hijack the session. To inject a prescription, they trigger multiple rapid booking requests to the appointment API via Kafka. Due to race conditions in the `ScheduleValidator` that processes booking logs asynchronously, the server updates state variables in Redis in an incorrect sequence. This state mismatch is read by the `PrescriptionConsumer` thread, allowing the attacker to issue unauthorized prescriptions under a different patient's account.
  - *Subtlety*: High. It requires exploiting out-of-order execution states in the Kafka consumer thread to overwrite Redis state variables, bypassing prescription authorization checks.

---

## 5. Code Comment Constraints (Agent Tipping Prevention)
- **No Code-Level Tips**: Source code files (`src/`) must not contain any explicit comments, annotations, or markers (e.g. `// VULNERABILITY`, `// CHAIN LINK`, etc.) that could tip off security-detection agents.
- **Metadata Localization**: All details regarding standalone vulnerabilities, exploit chains, and locations are strictly restricted to the ground-truth metadata files (`.vulns` JSON manifest) and internal reference files (`scenarios.md`).
