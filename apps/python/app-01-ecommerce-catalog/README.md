# App 01 — E-Commerce Product Catalog API

## Overview

A full-stack product catalog and order fulfillment portal built with **Flask** (Python) and a decoupled client-side Single Page Application (**HTML5 + vanilla JS + CSS SPA**) served under `static/`. The system is modularized into API controllers, repositories, services, search, MQ, and consumer layers.

This application is built for security-agent benchmarking and evaluation purposes.

---

## Business Domain

**Retail / E-Commerce** — Used by customers to search/browse items, add them to a cart, and place orders. Used by catalog managers (Admins) to register inventory products.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.x, Flask |
| Frontend | Decoupled client-side Single Page Application (HTML5, JavaScript, CSS) |
| Database | SQLite fallback with PostgreSQL/MongoDB integration surfaces |
| Search / MQ | Elasticsearch query client, Kafka-style event publisher/consumers |
| Containerisation | Docker, Docker Compose |

---

## Features

### Product Catalog
- Browse items catalog, SKU records, pricing, and descriptions
- Filter products dynamically using instant catalog search boxes
- Add items to custom baskets

### Order Processing
- Perform checkouts and submit orders
- View historical purchase summaries

## Security Benchmarking

This app intentionally contains benchmark vulnerabilities. Machine-readable ground truth is in [.vulns](.vulns).

---

## Chained Vulnerability Scenario

### Chain: "User Enumeration -> Session Forgery -> Catalog Modification"

An attacker confirms the admin account, forges an admin session, and writes unauthorized catalog changes.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Username existence endpoint confirms privileged account names without authentication | Low | A01 | `src/controllers/user_controller.py` -> `user_exists()` |
| 2 | Hardcoded Flask signing secret enables forged admin session cookies | Medium | A02 | `src/config/settings.py` -> `SECRET_KEY` |
| 3 | Product mutation trusts the forged admin session role | Medium | A01 | `src/controllers/product_controller.py` -> `create_product()` |

**Attack narrative**: The attacker probes `/api/users/exists?username=admin` to confirm the admin account exists. They use the hardcoded Flask `SECRET_KEY` in source to craft a valid signed session cookie with admin claims, then call `POST /api/products` to add or overwrite catalog data without knowing any password.

**Combined Impact**: Unauthorized catalog data modification through forged administrator access.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Serves the client-side SPA portal |
| POST | `/api/auth/login` | — | Authenticates and establishes session |
| POST | `/api/auth/logout` | — | Terminates active portal session |
| GET | `/api/auth/me` | ANY | Retrieves authenticated user profile |
| GET | `/api/users/exists` | — | Checks if a username is registered (chain link) |
| GET | `/api/user/profile` | ANY | Retrieves the current user's own profile |
| GET | `/api/health` | — | Health and integration surface check |
| GET | `/api/products` | — | Lists product items (supports search queries) |
| POST | `/api/products` | ADMIN+ | Add a new product to the catalog |
| GET | `/api/orders` | ANY | Lists user checkouts history |
| POST | `/api/orders` | ANY | Processes basket checkout and creates order |
| GET | `/api/orders/{id}` | ANY | View individual order detail fields |

---

## Running Locally

```bash
cd apps/python/app-01-ecommerce-catalog
pip install -r requirements.txt
python app.py
# Frontend served at http://localhost:8081
```

## Running via Docker

```bash
docker compose up --build
```
