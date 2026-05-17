# App 06 — Enterprise HR Management System

## Overview

A full-stack Human Resources management application built with **Spring Boot** (backend) and **Thymeleaf + vanilla JS** (frontend). The system manages employee directories, payroll processing, leave requests, and organisational charts.

This application intentionally contains **3 OWASP Top 10 vulnerabilities** for security-agent testing purposes.

---

## Business Domain

**Human Resources** — Used by HR administrators, managers, and employees within a mid-size enterprise.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security |
| Frontend | Thymeleaf templates, vanilla JavaScript, HTML/CSS |
| Database | H2 (embedded, in-memory) |
| Build | Maven |
| Containerisation | Docker |

---

## Features

### Employee Directory
- Browse / search all employees by name, department, or role
- View detailed employee profiles (contact, role, department, hire date)
- Admin: create, update, and deactivate employee records

### Payroll Management
- View salary details for individual employees
- Generate monthly payroll report (CSV export)
- Salary adjustment with approval workflow

### Leave Management
- Submit leave requests (vacation, sick, personal)
- Manager approval / rejection workflow
- Calendar view of team availability

### Organisation Chart
- Visual org chart rendered in the browser
- Drill-down by department
- Manager ↔ report relationships

### Authentication & Roles
- Login / logout with session management
- Roles: `EMPLOYEE`, `MANAGER`, `HR_ADMIN`
- Role-based page access

---

## Planted Vulnerabilities

> **⚠️ These are intentional. Do not fix them — they are the test targets.**

| # | OWASP ID | Category | Location | Description | CWE |
|---|----------|----------|----------|-------------|-----|
| 1 | **A01** | Broken Access Control | `src/main/java/com/hr/controller/PayrollController.java` | The `/api/payroll/{employeeId}` endpoint returns salary data for **any** authenticated user, regardless of role. No authorisation check verifies the caller is HR_ADMIN or the employee themselves. An `EMPLOYEE`-role user can enumerate other employees' salaries by iterating IDs. | CWE-639 |
| 2 | **A08** | Software & Data Integrity Failures | `src/main/java/com/hr/service/EmployeeImportService.java` | The bulk employee import feature accepts a serialised Java object (`ObjectInputStream.readObject()`) from an uploaded `.ser` file without any class-filtering or allow-list. An attacker can craft a malicious serialised payload to achieve remote code execution. | CWE-502 |
| 3 | **A02** | Cryptographic Failures | `src/main/java/com/hr/model/Employee.java` / `schema.sql` | Social Security Numbers (SSNs) are stored using a **reversible XOR cipher** with a hard-coded key embedded in the source code. The key is `0xDEADBEEF`. This provides no real confidentiality. | CWE-327 |

### Decoy (Safe Pattern)
- The login endpoint uses `BCryptPasswordEncoder` with default strength — this is **not** vulnerable and should **not** be flagged.
- SQL queries in `EmployeeRepository` use Spring Data JPA parameterised queries — **not** injectable.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Login page |
| POST | `/login` | — | Authenticate |
| GET | `/dashboard` | ANY | Role-based dashboard |
| GET | `/api/employees` | ANY | List employees |
| GET | `/api/employees/{id}` | ANY | Employee detail |
| POST | `/api/employees` | HR_ADMIN | Create employee |
| PUT | `/api/employees/{id}` | HR_ADMIN | Update employee |
| **GET** | **`/api/payroll/{employeeId}`** | **ANY (🐛 A01)** | **Salary data — missing authz** |
| GET | `/api/payroll/report` | HR_ADMIN | Monthly payroll CSV |
| POST | `/api/employees/import` | HR_ADMIN | **Bulk import (🐛 A08)** |
| GET | `/api/leave/requests` | ANY | Leave requests for current user |
| POST | `/api/leave/requests` | ANY | Submit leave request |
| PUT | `/api/leave/requests/{id}/approve` | MANAGER | Approve leave |
| GET | `/api/org-chart` | ANY | Org chart data |

---

## Running Locally

```bash
cd apps/java/app-06-hr-management
./mvnw spring-boot:run
# Frontend served at http://localhost:8080
```

## Running via Docker

```bash
docker build -t app-06-hr-management .
docker run -p 8080:8080 app-06-hr-management
```

---

## Ground Truth

See `vulnerabilities.json` for machine-readable vulnerability manifest used for automated scoring.
