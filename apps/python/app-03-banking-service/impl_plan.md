# Implementation Plan — App 03: Banking Transaction Service

## 1. Project Scaffold

### 1.1 Scaffold layout:
```
apps/python/app-03-banking-service/
├── README.md
├── impl_plan.md
├── .vulns
├── Dockerfile
├── requirements.txt
├── app.py
└── static/
    ├── index.html
    ├── css/
    │   └── main.css
    └── js/
        └── app.js
```

### 1.2 Dependencies (`requirements.txt`)
- `fastapi`
- `uvicorn`
- `mongomock`
- `pydantic`

---

## 2. Database Schema

The database runs on PyMongo/mongomock in-memory collections:
- `users`: accounts credentials (username, full_name, routing_number, account_number, password_hash, role).
- `accounts`: balance records mapping account keys to current ledger balances.
- `transactions`: ledger transactions tracking sender, receiver, amount, category, and timestamps.

---

## 3. Backend REST API Endpoints

- `GET /`: Serves static SPA dashboard template.
- `POST /api/auth/login`: Process authentication parameters.
- `POST /api/auth/logout`: Clears authentication details.
- `GET /api/auth/me`: Retrieves currently authenticated user session.
- `GET /api/accounts/balance`: Returns ledger balance.
- `POST /api/transfers`: Dispatches a new wire transfer.
- `GET /api/transactions`: Lists historical ledger logs.

---

## 4. Frontend SPA Portal

Modern client-side Single Page Application (SPA) served under static routes. Contains:
- Auth portal login panel.
- Account Ledger showing routing lists and available balances.
- Wire Transfer Dispatcher form sending funds to target accounts.
- NoSQL filter explorer with a telemetry console showing Mongo queries.

---

## 5. Testing

Standard Python testing verifying:
- Safe, standard user authentication mechanisms.
- Transfers balances deductions.
- Ledger listings retrievals.
