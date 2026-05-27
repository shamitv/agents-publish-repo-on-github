# Phase 04 TODO — Supplier Portal Frontend (React)

## Project Setup (completed in earlier work)
- [x] `package.json` with react, react-dom, react-router-dom, axios, vite, TypeScript dev deps
- [x] `vite.config.ts` with proxy to port 5002
- [x] `tsconfig.json`
- [x] `npm install` done, `npm run build` succeeds

## Core Infrastructure
- [x] `src/main.tsx` — ReactDOM.createRoot
- [x] `src/App.tsx` — route definitions with auth guard
- [x] `src/context/AuthContext.tsx` — auth state, login/logout, token management
- [x] `src/components/Layout.tsx` — header + Outlet for nested routes
- [x] `src/components/SessionProvider.tsx` — decoy: short-lived token with auto-refresh
- [x] `src/services/api.ts` — Axios instance (existed), hooks updated to correct API paths
- [x] `src/i18n/I18nContext.tsx` — existed, locale switcher

## Pages
- [x] `src/pages/Login.tsx` — supplier ID + password form, calls `/portal/auth/login`
- [x] `src/pages/Dashboard.tsx` — KPI cards, recent reports, custom widgets section
- [x] `src/pages/Reports.tsx` — report job history table, enqueue form
  - [x] **VULNERABILITY A06**: `dangerouslySetInnerHTML` via `<ReportNotesCell>` component
- [x] `src/pages/ReportDetail.tsx` — job status timeline, parameters display, download button
- [x] `src/pages/Webhooks.tsx` — register form, webhook list with delete buttons
  - [x] Decoy: `validateUrlInput(url)` — client-side URL validation
- [x] `src/pages/test/Widgets.tsx` — custom dashboard widget builder
  - [x] **CHAIN LINK 1 (chain-03)**: `CustomWidgetRenderer` accepts raw HTML with no CSP
- [x] `src/pages/test/Notifications.tsx` — notification preference mock UI
- [x] `src/pages/test/Console.tsx` — admin diagnostic console placeholder

## Components
- [x] `src/components/DashboardWidgets.tsx`
  - [x] `KPICard` — metric display
  - [x] `RecentReports` — recent jobs list
  - [x] `CustomWidgetRenderer` — **CHAIN LINK 1 (chain-03)** raw HTML rendering
- [x] `src/components/ReportNotes.tsx` — decoy: safe notes renderer using `textContent`
- [x] `src/components/JobStatusBadge.tsx` — colored badge for job status
- [x] `src/components/DownloadButton.tsx` — disabled state for non-completed jobs
- [x] `src/components/LoadingSpinner.tsx`

## Styles
- [x] `src/App.css` — all styles consolidated (220+ lines): login, dashboard, reports, webhooks, test pages, detail, status badges, loading spinner, responsive

## Artifact Updates
- [x] Update `.vulns` — add VULN-07 (A06 XSS), add chain-03 step 1, add decoys (ReportNotes, validateUrlInput, SessionProvider)
- [x] Update `README.md` — frontend architecture section, React tech stack, page routes table
- [x] Update `scenarios.md` — chain-03 step 1 narrative

## Verification
- [x] `npm run build` succeeds without errors
- [x] Login page renders, accepts supplier credentials, redirects to dashboard
- [x] Dashboard fetches KPI data from supplier-portal-api
- [x] Reports page lists jobs for current supplier
- [x] Report detail shows status, download link works for completed jobs
- [x] A06: report notes rendered via `dangerouslySetInnerHTML` without DOMPurify
- [x] Decoy `ReportNotes` renders via `textContent` — XSS payload shown as text
- [x] chain-03 step 1: `CustomWidgetRenderer` accepts raw HTML with no CSP
- [x] Webhook CRUD works: create, list, delete
- [x] Existing vulnerabilities from all previous phases remain exploitable
