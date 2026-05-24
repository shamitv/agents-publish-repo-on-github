# Implementation Plan — App 01: E-Commerce Product Catalog

## 1. Project Scaffold

### 1.1 Scaffold layout:
```
apps/python/app-01-ecommerce-catalog/
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
- `Flask`
- `pysqlite3` or Python standard library `sqlite3`

---

## 2. Database Schema

The database runs on SQLite3 in-memory:
- `users` (id, username, password_hash, role)
- `products` (id, sku, name, description, category, price, quantity)
- `orders` (id, user_id, order_number, total_amount, status, created_at)
- `order_items` (id, order_id, product_id, quantity, price)

---

## 3. Backend REST API Endpoints

- `GET /`: Serves SPA portal dashboard.
- `POST /api/auth/login`: Process login parameters.
- `POST /api/auth/logout`: Clears authentication details.
- `GET /api/auth/me`: Retrieves currently authenticated user profile.
- `GET /api/products`: Retrieve product lists (supports query search parameters).
- `POST /api/products`: Creates catalog items (admin-only).
- `GET /api/orders`: Retrieves authenticated orders lists.
- `POST /api/orders`: Processes checkouts and places new orders.
- `GET /api/orders/<id>`: Returns single order details.

---

## 4. Frontend SPA Portal

Modern client-side Single Page Application (SPA) served under `static/`. Contains:
- Auth portal login panel.
- Product Catalog list with live SQL Injection payload visualizers.
- Order queue explorer showing customer purchases.
- Privileged order inspector displaying lines items in clean layouts.

---

## 5. Testing

Standard Python testing verifying:
- Safe, standard user authentication mechanisms.
- Product listings and pagination.
- Order placements and state maps.
