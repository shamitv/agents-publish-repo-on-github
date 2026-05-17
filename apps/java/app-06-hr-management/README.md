# App 06 — Enterprise HR Management System

## Overview

A full-stack Human Resources management application built with **Spring Boot** (backend) and **Thymeleaf + vanilla JS** (frontend). The system manages employee directories, payroll processing, leave requests, and organisational charts.

This application is built for security-agent benchmarking and evaluation purposes.

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

## Security Benchmarking

This application has been developed to contain hidden, realistic vulnerabilities mapped to the OWASP Top 10 categories, designed to challenge security agents and code analysis systems.

For ground-truth details regarding the vulnerabilities, see the `.vulns` file in this directory.

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
./mvnw spring-boot:run
# Frontend served at http://localhost:8080
```

## Running via Docker

```bash
docker build -t app-06-hr-management .
docker run -p 8080:8080 app-06-hr-management
```
