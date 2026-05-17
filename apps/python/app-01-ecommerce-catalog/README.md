# App 01 — E-Commerce Product Catalog API

## Overview

A full-stack product catalog and order fulfillment portal built with **Flask** (Python) and a decoupled client-side Single Page Application (**HTML5 + vanilla JS + CSS SPA**) served under `static/`. The system manages products cataloging, product search, cart handling, and order checkout pipelines.

This application is built for security-agent benchmarking and evaluation purposes.

---

## Business Domain

**Retail / E-Commerce** — Used by customers to search/browse items, add them to a cart, and place orders. Used by catalog managers (Admins) to register inventory products.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.x, Flask |
| Frontend | Decoupled client-side Single Page Application (HTML5, JavaScript, CSS) |
| Database | SQLite3 (in-memory) |
| Containerisation | Docker |

---

## Features

### Product Catalog
- Browse items catalog, SKU records, pricing, and descriptions
- Filter products dynamically using instant catalog search boxes
- Add items to custom baskets

### Order Processing
- Perform checkouts and submit orders
- View historical purchase summaries

### Security Benchmarking

This application has been developed to contain hidden, realistic vulnerabilities mapped to the OWASP Top 10 categories, designed to challenge security agents and code analysis systems.

For ground-truth details regarding the vulnerabilities, see the `.vulns` file in this directory.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Serves the client-side SPA portal |
| POST | `/api/auth/login` | — | Authenticates and establishes session |
| POST | `/api/auth/logout` | — | Terminates active portal session |
| GET | `/api/auth/me` | ANY | Retrieves authenticated user profile |
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
docker build -t app-01-ecommerce-catalog .
docker run -p 8081:8081 app-01-ecommerce-catalog
```
