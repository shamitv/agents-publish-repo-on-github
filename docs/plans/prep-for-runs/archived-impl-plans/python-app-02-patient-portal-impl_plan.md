# Implementation Plan — App 02: Healthcare Patient Portal

## 1. Project Scaffold

### 1.1 Scaffold layout:
```
apps/python/app-02-patient-portal/
├── README.md
├── impl_plan.md
├── .vulns
├── Dockerfile
├── requirements.txt
├── manage.py
├── patient_portal/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── portal/
    ├── __init__.py
    ├── apps.py
    ├── models.py
    ├── views.py
    ├── urls.py
    └── static/
        ├── index.html
        ├── css/
        │   └── main.css
        └── js/
            └── app.js
```

---

## 2. Database Schema

The database runs on standard SQLite:
- `PatientProfile`: User accounts details including patient metadata (name, blood_type, date_of_birth, patient_role, password_hash).
- `Appointment`: Medical consultations records mapping patient keys, scheduled dates, reason for visit, and target department.
- `Prescription`: Privileged prescription entries listing medical formulas, dosages, and prescribing physician.

---

## 3. Backend REST API Endpoints

- `GET /`: Serves static SPA dashboard template.
- `POST /api/auth/login`: Process authentication parameters.
- `POST /api/auth/logout`: Clears authentication details.
- `GET /api/auth/me`: Retrieves currently authenticated user session.
- `GET /api/patients/<id>/records`: Retreives medical profiles details.
- `POST /api/appointments`: Schedules a new clinic consultation.
- `GET /api/appointments`: Retrieves appointment list histories.

---

## 4. Frontend SPA Portal

Modern client-side Single Page Application (SPA) served under static routes. Contains:
- Auth portal login panel.
- Vital Signs Monitor simulator displaying a live animated heartbeat pulse.
- Medical Record Vault browsing patient prescriptions and historical diagnostics.
- Scheduler Panel booking clinic consults.

---

## 5. Testing

Standard Django testing verifying:
- Parameterized account profiles establishment.
- Appointment schedules listings.
- Session authorization handlers.
