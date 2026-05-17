# App 08 — Warehouse Management System

## Overview

A full-stack warehouse management application built with **Spring Boot** (backend) and **Thymeleaf + vanilla JS** (frontend). The system handles inventory tracking, order fulfilment, employee management, and shipping label generation.

This application intentionally contains **3 OWASP Top 10 vulnerabilities** for security-agent testing purposes.

---

## Business Domain

**Logistics / Warehousing** — Used by warehouse operators, supervisors, and dispatch staff to manage inventory, process orders, and coordinate shipments.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security, Spring Actuator |
| Frontend | Thymeleaf templates, vanilla JavaScript, HTML/CSS |
| Database | H2 (embedded, in-memory) |
| LDAP | Embedded UnboundID LDAP (for employee directory) |
| Build | Maven |
| Containerisation | Docker |

---

## Features

### Inventory Management
- View all warehouse items with quantities, locations (aisle/shelf/bin)
- Add / update / remove inventory items
- Low-stock alerts dashboard
- Barcode lookup (simulated)

### Order Fulfilment
- View incoming orders from external system (seeded data)
- Pick list generation for warehouse workers
- Order status tracking (PENDING → PICKING → PACKED → SHIPPED)
- Partial fulfilment support

### Employee Directory (LDAP)
- Search warehouse employees by name or role
- View employee details, shift assignments
- LDAP-backed directory for employee lookups

### Shipping
- Generate shipping labels (fetch carrier-provided label via URL)
- Track shipments with carrier integration (simulated external URL)
- Shipping cost calculator

### Authentication & Roles
- Login / logout with session management
- Roles: `OPERATOR`, `SUPERVISOR`, `ADMIN`
- Role-based access to management functions

---

## Planted Vulnerabilities

> **⚠️ These are intentional. Do not fix them — they are the test targets.**

| # | OWASP ID | Category | Location | Description | CWE |
|---|----------|----------|----------|-------------|-----|
| 1 | **A05** | Security Misconfiguration | `src/main/resources/application.yml` + Spring Actuator config | **Spring Boot Actuator endpoints are publicly exposed** without authentication. Endpoints like `/actuator/env`, `/actuator/beans`, `/actuator/heapdump`, and `/actuator/mappings` are accessible to unauthenticated users, leaking environment variables, internal bean details, JVM heap contents, and full API route maps. | CWE-16 |
| 2 | **A03** | Injection | `src/main/java/com/warehouse/service/EmployeeLdapService.java` | The employee directory search constructs an **LDAP filter by string concatenation** using user-supplied search input. An attacker can inject LDAP filter operators (e.g., `*)(uid=*))(|(uid=*`) to bypass search restrictions and enumerate all employees, or extract attributes not normally returned. | CWE-90 |
| 3 | **A10** | Server-Side Request Forgery (SSRF) | `src/main/java/com/warehouse/service/ShippingService.java` | The shipping label generation feature accepts a **user-supplied URL** pointing to the carrier's label endpoint. The server fetches this URL directly using `HttpURLConnection` with no URL validation or allow-listing. An attacker can supply `http://169.254.169.254/latest/meta-data/` (AWS metadata) or internal network URLs to probe internal services. | CWE-918 |

### Decoys (Safe Patterns)
- Inventory search uses Spring Data JPA with parameterised queries — **NOT injectable**.
- Password storage uses BCrypt — **safe**.
- Order status updates check the caller's role via `@PreAuthorize` — **properly authorised**.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Login page |
| POST | `/login` | — | Authenticate |
| GET | `/dashboard` | ANY | Role-based dashboard |
| GET | `/api/inventory` | ANY | List all inventory items |
| GET | `/api/inventory/{id}` | ANY | Single item detail |
| POST | `/api/inventory` | SUPERVISOR+ | Add item |
| PUT | `/api/inventory/{id}` | SUPERVISOR+ | Update item |
| DELETE | `/api/inventory/{id}` | ADMIN | Remove item |
| GET | `/api/inventory/low-stock` | ANY | Low-stock alerts |
| GET | `/api/orders` | ANY | List orders |
| GET | `/api/orders/{id}` | ANY | Order detail |
| PUT | `/api/orders/{id}/status` | OPERATOR+ | Update order status |
| GET | `/api/orders/{id}/picklist` | OPERATOR+ | Generate pick list |
| **GET** | **`/api/employees/search?q=`** | **ANY** | **Employee search (🐛 A03 — LDAP injection)** |
| **POST** | **`/api/shipping/label`** | **OPERATOR+** | **Generate label (🐛 A10 — SSRF)** |
| **GET** | **`/actuator/**`** | **NONE (🐛 A05)** | **Actuator endpoints — publicly exposed** |

---

## Running Locally

```bash
cd apps/java/app-08-warehouse-mgmt
./mvnw spring-boot:run
# Frontend served at http://localhost:8082
```

## Running via Docker

```bash
docker build -t app-08-warehouse-mgmt .
docker run -p 8082:8082 app-08-warehouse-mgmt
```

---

## Ground Truth

See `vulnerabilities.json` for machine-readable vulnerability manifest used for automated scoring.
