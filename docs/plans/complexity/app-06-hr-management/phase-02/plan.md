# Phase 02: Onboarding State Machine

## Goal

Build the employee onboarding workflow state machine (Draft → Verified → Background Checked → Active) as new JPA entity, service, repository, and controller. Formalize the unannotated `/audit` endpoint as VULN-08. Plant A04 insecure design vulnerability in the state validation logic.

## Scope

### Included
- [ ] Create `model/OnboardingRequest.java` JPA entity with state enum
- [ ] Create `repository/OnboardingRepository.java` Spring Data JPA interface
- [ ] Create `service/OnboardingWorkflowService.java` with state machine transitions
- [ ] Create `controller/OnboardingController.java` with 4 endpoints
- [ ] Plant A04: state machine allows Draft→Active skip without intermediate checks
- [ ] Formalize `getEmployeeAudit()` in `EmployeeController.java` as VULN-08 with annotation
- [ ] Add decoy: proper state validation on read-only onboarding list endpoint
- [ ] Add `@PreAuthorize("hasRole('HR_ADMIN') or #id == authentication.principal.id")` to `getEmployee()` in `EmployeeController.java` as decoy near the leaky audit endpoint

### Excluded
- No audit logging (Phase 3)
- No ES changes (Phase 3)
- No UI changes (Phase 4)

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| State machine uses simple enum + validator | No Spring State Machine dependency; keep it simple for benchmark |
| A04 planted in transition validation | The transition() method accepts `targetState` without checking sequential order or prerequisite steps |
| Formalized audit endpoint uses `@PreAuthorize` decoy nearby | Same controller has properly guarded endpoints |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone | A04 | CWE-602 | `service/OnboardingWorkflowService.java` → `transition()` | State machine accepts any target state without validating prerequisites — can skip from Draft directly to Active | Medium |

**Source comment**: `// VULNERABILITY A04: Onboarding state machine accepts any targetState without validating prerequisite steps.`

### Chain-02 Step 1

| Chain | Step | OWASP | CWE | Location | Description | Severity |
|-------|------|-------|-----|----------|-------------|----------|
| chain-02 | 1 | A04 | CWE-602 | `service/OnboardingWorkflowService.java` → `transition()` | Can bypass Background Check state by directly requesting Active | Low |

**Source comment**: `// CHAIN LINK 1 (chain-02): State machine allows bypassing Background Check by requesting Active directly.`

### Chain-03 Step 1 (formalized audit endpoint)

| Chain | Step | OWASP | CWE | Location | Description | Severity |
|-------|------|-------|-----|----------|-------------|----------|
| chain-03 | 1 | A01 | CWE-639 | `controller/EmployeeController.java` → `getEmployeeAudit()` | Returns passwordHash for any employee ID without authorization check | Low |

**Source comment**: `// CHAIN LINK 1 (chain-03): Employee audit endpoint returns passwordHash for any employee by ID without authorization.`

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `controller/OnboardingController.java` → `listOnboardingRequests()` | Same controller as vulnerable state transition; appears to expose all requests | Filters by `@AuthenticationPrincipal` — only returns requests the current user created |
| 2 | `controller/EmployeeController.java` → `getEmployee()` | Same controller as leaked audit endpoint; appears to leak PII | Added during Phase 2: uses `@PreAuthorize("hasRole('HR_ADMIN') or #id == authentication.principal.id")` |

## Data Model Changes

### New JPA Entity

| Entity | Table | Fields |
|--------|-------|--------|
| `OnboardingRequest` | `onboarding_requests` | `id (Long PK)`, `employeeId (Long)`, `currentState (enum: DRAFT/VERIFIED/BACKGROUND_CHECKED/ACTIVE/REJECTED)`, `requestedBy (String)`, `reviewedBy (String)`, `createdAt (LocalDateTime)`, `updatedAt (LocalDateTime)` |

## API Contracts

### New Endpoints

| Method | Path | Auth | Controller Method |
|--------|------|------|-------------------|
| POST | `/api/onboarding` | HR_ADMIN | `createOnboarding()` |
| GET | `/api/onboarding/{id}` | HR_ADMIN | `getOnboarding()` |
| PUT | `/api/onboarding/{id}/transition` | HR_ADMIN | `transitionState()` — **vulnerable A04 path** |
| GET | `/api/onboarding` | HR_ADMIN | `listOnboarding()` — **decoy, properly filtered** |

## Artifact Updates

- `src/main/java/com/hr/model/OnboardingRequest.java`: New file
- `src/main/java/com/hr/model/OnboardingState.java`: New enum
- `src/main/java/com/hr/repository/OnboardingRepository.java`: New file
- `src/main/java/com/hr/service/OnboardingWorkflowService.java`: New file (includes A04)
- `src/main/java/com/hr/controller/OnboardingController.java`: New file (includes decoy)
- `src/main/java/com/hr/controller/EmployeeController.java`: Add VULN-08 + CHAIN LINK 1 (chain-03) annotations to `getEmployeeAudit()`
- `.vulns`: Add VULN-05 (A04), VULN-08 (formalized A01), chain-02 step 1, chain-03 step 1
- `README.md`: Add onboarding endpoints to API table
- `scenarios.md`: Add chain-02 and chain-03 narratives (step 1 only)

## Dependencies on Other Phases

- **Depends on Phase 1**: PostgreSQL must be running for new `onboarding_requests` table
- **Phase 3** depends on Phase 2: Onboarding workflow must exist before adding audit gap
- **Phase 4** depends on Phase 2: UI dashboard needs onboarding state data
