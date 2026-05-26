# Implementation Plan — App 04: Real Estate Listing Platform

## 1. Project Scaffold

### 1.1 Scaffold layout:
```
apps/python/app-04-real-estate/
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

---

## 2. Database Schema

The database runs on in-memory SQLite tables:
- `users`: User profiles credentials (username, password, role).
- `properties`: Property directory metadata (title, category, price, location, description, image_path).
- `messages`: Agent contact logs containing prospective client name, phone, message content, and target property ID.

---

## 3. Backend REST API Endpoints

- `GET /`: Serves static SPA dashboard template.
- `POST /api/auth/login`: Process authentication parameters.
- `POST /api/auth/logout`: Clears authentication details.
- `GET /api/auth/me`: Retrieves currently authenticated user session.
- `GET /api/properties`: Lists registered real estate listings.
- `POST /api/properties`: Add a new listing entry.
- `POST /api/properties/import-image`: Fetch external image from URL.
- `POST /api/properties/analyze`: Trigger listing description analyzer subprocess.

---

## 4. Frontend SPA Portal

Modern client-side Single Page Application (SPA) served under static routes. Contains:
- Real Estate portal login panels.
- Property Board displaying home listings cards, price, and descriptions.
- Property Registrar form to add listings.
- URL image loader allowing remote imports.
- Subprocess trace monitor console showing analytical outputs.

---

## 5. Testing

Standard Python testing verifying:
- Parameterized real estate searches.
- New property catalog registers.
- Session handshake routines.
