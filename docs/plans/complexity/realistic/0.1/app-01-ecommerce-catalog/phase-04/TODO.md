# Phase 04 TODO — Supplier Portal Frontend (React)

## Project Setup
- [ ] If not already scaffolded in Phase 01, create the React project:
  - [ ] `package.json` with react, react-dom, react-router-dom, axios, vite, TypeScript dev deps
  - [ ] `vite.config.ts` with proxy to `localhost:5003` (supplier-portal-api)
  - [ ] `tsconfig.json` / `tsconfig.node.json`
  - [ ] `.eslintrc.cjs` / `.prettierrc` (optional)
  - [ ] Run `npm install`
  - [ ] Verify `npm run dev` starts without errors

## Core Infrastructure
- [ ] Create `src/main.tsx` — ReactDOM.createRoot with BrowserRouter
- [ ] Create `src/App.tsx` — route definitions
- [ ] Create `src/context/AuthContext.tsx` — auth state, login/logout, token management
- [ ] Create `src/context/I18nContext.tsx` — mock i18n provider (English only, locale switcher structure)
- [ ] Create `src/services/api.ts` — Axios instance with base URL, interceptors
- [ ] Create `src/components/Layout.tsx` — header, nav, sidebar, outlet
- [ ] Create `src/components/SessionProvider.tsx` — decoy: short-lived token with auto-refresh

## Pages
- [ ] `src/pages/Login.tsx` — supplier ID + password form, calls `/portal/auth/login`
- [ ] `src/pages/Dashboard.tsx` — KPI cards grid, recent reports table, summary metrics
- [ ] `src/pages/Reports.tsx` — report job history table, enqueue form
  - [ ] **VULNERABILITY A06**: `displayReportNotes(notes)` — renders via `dangerouslySetInnerHTML`, no sanitization
- [ ] `src/pages/ReportDetail.tsx` — job status timeline, parameters display, download button
- [ ] `src/pages/Webhooks.tsx` — register form, webhook list with delete buttons
  - [ ] Decoy: `validateUrlInput(url)` — client-side URL validation
- [ ] `src/pages/test/Widgets.tsx` — custom dashboard widget builder (test page)
  - [ ] **CHAIN LINK 1 (chain-03)**: `CustomWidgetRenderer` accepts raw HTML with no CSP
- [ ] `src/pages/test/Notifications.tsx` — notification preference mock UI
- [ ] `src/pages/test/Console.tsx` — admin diagnostic console (placeholder for Phase 5)

## Components
- [ ] `src/components/DashboardWidgets.tsx`
  - [ ] `KPICard` — metric display
  - [ ] `RecentReports` — recent jobs list
  - [ ] `CustomWidgetRenderer` — **CHAIN LINK 1 (chain-03)** raw HTML rendering
- [ ] `src/components/ReportNotes.tsx` — decoy: safe notes renderer using `textContent`
- [ ] `src/components/JobStatusBadge.tsx` — colored badge for job status
- [ ] `src/components/DownloadButton.tsx` — disabled state for non-completed jobs
- [ ] `src/components/LoadingSpinner.tsx`

## Styles
- [ ] Create `src/styles/global.css` — base styles, responsive grid
- [ ] Create `src/styles/dashboard.css` — KPI card grid layout
- [ ] Create `src/styles/reports.css` — table and form styles

## Artifact Updates
- [ ] Update `.vulns` — add VULN-07 (A06 Client-Side XSS), add chain-03 step 1, add decoys
- [ ] Update `README.md` — frontend architecture section, React tech stack, page routes
- [ ] Update `scenarios.md` — chain-03 step 1 narrative

## Verification
- [ ] `npm run build` succeeds without errors
- [ ] Login page renders, accepts supplier credentials, redirects to dashboard
- [ ] Dashboard fetches KPI data from supplier-portal-api
- [ ] Reports page lists jobs for current supplier
- [ ] Report detail shows status, download link works for completed jobs
- [ ] A06: report notes containing `<img src=x onerror=alert(1)>` executes JavaScript in browser
- [ ] A06: `dangerouslySetInnerHTML` is used directly with no DOMPurify/sanitization wrapper
- [ ] Decoy `ReportNotes` renders XSS payload as plain text (via `textContent`)
- [ ] chain-03 step 1: custom widget with `<script>` tag executes in browser
- [ ] Webhook CRUD works: create, list, delete
- [ ] Existing vulnerabilities from all previous phases remain exploitable