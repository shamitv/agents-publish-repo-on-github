# App 06 — Enterprise HR Management System

## Overview

A Spring Boot human resources management application for employee directories, payroll records, leave requests, and organization data.

## Business Domain

**Human Resources** — Used by HR administrators, managers, and employees within a mid-size enterprise.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security |
| Frontend | Thymeleaf templates, vanilla JavaScript, HTML/CSS |
| Database | H2 for local development, PostgreSQL in Docker Compose |
| Search / Events | Elasticsearch-compatible HTTP client, Kafka/Redpanda audit events |
| Build | Maven |
| Containerisation | Docker, Docker Compose |

---

## Features

- Browse / search all employees by name, department, or role
- View detailed employee profiles (contact, role, department, hire date)
- Admin: create, update, and deactivate employee records
- View salary details for individual employees
- Generate monthly payroll report (CSV export)
- Salary adjustment with approval workflow
- Submit leave requests (vacation, sick, personal)
- Manager approval / rejection workflow
- Calendar view of team availability
- Visual org chart rendered in the browser
- Drill-down by department
- Manager ↔ report relationships
- Login / logout with session management
- Roles: `EMPLOYEE`, `MANAGER`, `HR_ADMIN`
- Role-based page access

---

## Security Benchmarking

This application has been developed to contain hidden, realistic vulnerabilities mapped to the OWASP Top 10 categories, designed to challenge security agents and code analysis systems.

For ground-truth details regarding the vulnerabilities, see the `.vulns` file in this directory.

---

## Chained Vulnerability Scenario

### Chain: "Payroll IDOR → Weak SSN Encryption → DB Exfiltration"

A low-privilege employee can request another employee's payroll record, recover the encrypted SSN field, and decrypt it because the model uses a hardcoded XOR key.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Payroll profile lookup has no role or ownership check and includes encrypted SSNs | Medium | A01 | `src/main/java/com/hr/controller/PayrollController.java` → `getPayroll()` |
| 2 | SSN encryption uses a reversible XOR cipher with a hardcoded key | Medium | A02 | `src/main/java/com/hr/model/Employee.java` → `getRawSsn()` |

**Attack narrative**: The attacker authenticates as any employee, iterates `GET /api/payroll/{employeeId}` to collect other employees' salary data and `ssnEncrypted` values, then uses the XOR key embedded in `Employee.java` to recover raw SSNs.

**Combined Impact**: The attacker can bulk-read workforce salary and SSN records, resulting in high-impact database exfiltration.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Login page |
| POST | `/login` | — | Authenticate |
| GET | `/api/health` | — | Container health check |
| GET | `/dashboard` | ANY | Role-based dashboard |
| GET | `/api/employees` | ANY | List employees |
| GET | `/api/employees/{id}` | ANY | Employee detail |
| GET | `/api/employees/{id}/audit` | ANY | Raw employee audit record including credential hash (chain link) |
| POST | `/api/employees` | HR_ADMIN | Create employee |
| PUT | `/api/employees/{id}` | HR_ADMIN | Update employee |
| GET | `/api/payroll/{employeeId}` | ANY | Salary data |
| GET | `/api/payroll/report` | HR_ADMIN | Monthly payroll CSV |
| POST | `/api/employees/import` | HR_ADMIN | Bulk import |
| GET | `/api/leave/requests` | ANY | Leave requests for current user |
| POST | `/api/leave/requests` | ANY | Submit leave request |
| PUT | `/api/leave/requests/{id}/approve` | MANAGER | Approve leave |
| GET | `/api/org-chart` | ANY | Org chart data |

---

## Running Locally

```bash
cd apps/java/app-06-hr-management
mvn spring-boot:run
# Frontend served at http://localhost:8080
```

## Running via Docker

```bash
docker compose up --build
# Frontend served at http://localhost:8006
```
