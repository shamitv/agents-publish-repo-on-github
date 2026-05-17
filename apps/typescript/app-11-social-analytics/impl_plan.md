# Implementation Plan — App 11: Social Media Analytics Dashboard

## 1. Project Scaffold

### 1.1 Scaffold layout:
```
apps/typescript/app-11-social-analytics/
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
- `users`: User profiles (username, password, role).
- `widgets`: User-specific dashboard widgets for social media tracking.

---

## 3. Backend REST API Endpoints

- `GET /`: Serves static SPA dashboard template.
- `POST /api/auth/login`: Process authentication parameters.
- `POST /api/auth/logout`: Clears authentication details.
- `GET /api/auth/me`: Retrieves currently authenticated user session.
- `GET /api/widgets`: Lists the user's dashboard widgets.
- `POST /api/widgets`: Creates a new widget.
- `POST /api/preview`: Generates a URL preview for a social media link.

---

## 4. Frontend SPA Portal

Modern client-side Single Page Application (SPA) served under static routes. Contains:
- Analytics portal login panel.
- Dynamic Dashboard displaying custom widgets (Followers, Engagement, Reach).
- URL Preview generator for campaign links.
- Sleek, modern "Neon Analytics" theme using HTML5, CSS3, and vanilla JS.

---

## 5. Testing

Standard manual testing verifying:
- Login authentication flows.
- Creation of new analytics widgets.
- Loading remote URL previews.
