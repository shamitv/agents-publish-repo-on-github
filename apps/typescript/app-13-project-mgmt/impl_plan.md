# Implementation Plan — App 13: Project Management Tool

## 1. Project Scaffold

### 1.1 Scaffold layout:
```
apps/typescript/app-13-project-mgmt/
├── README.md
├── impl_plan.md
├── .vulns
├── Dockerfile
├── package.json
├── tsconfig.json
├── src/
│   └── index.ts
└── public/
    ├── index.html
    ├── css/
    │   └── main.css
    └── js/
        └── app.js
```

---

## 2. Mock Database

The database runs on an in-memory data structure:
- `users`: User profiles (username, password, organization_id, role).
- `boards`: Project tracking boards linked to specific organizations.
- `tasks`: Action items and user stories containing rich-text descriptions.

---

## 3. Backend REST API Endpoints

- `GET /`: Serves static SPA dashboard template.
- `POST /api/auth/login`: Process authentication parameters.
- `POST /api/auth/logout`: Clears authentication details.
- `GET /api/auth/me`: Retrieves currently authenticated user session.
- `GET /api/boards`: Retrieves all project boards for the user's organization.
- `GET /api/boards/:id`: Fetches specific board details and its associated tasks.
- `POST /api/boards/:id/tasks`: Create a new task within a specific board.
- `PUT /api/boards/:id/permissions`: Modify the privacy setting of a board.

---

## 4. Frontend SPA Portal

Modern client-side Single Page Application (SPA) served under static routes. Contains:
- Collaboration portal login panel.
- Dynamic Board List showing active projects.
- Task Management Kanban-style view showing task descriptions.
- Board Setting controls for adjusting board visibility.
- Clean, modern "SaaS Productivity" theme using HTML5, CSS3, and vanilla JS.

---

## 5. Testing

Standard manual testing verifying:
- Login authentication flows.
- Navigation through project boards.
- Creation of new tasks.
- Modifying board permissions.
