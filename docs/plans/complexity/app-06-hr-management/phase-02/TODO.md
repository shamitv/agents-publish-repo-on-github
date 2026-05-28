# Phase 02 TODO — Onboarding State Machine

## Pre-requisites
- [ ] Phase 1 complete: PostgreSQL running, app connected
- [ ] Read vuln-inventory.md — confirm no-touch files

## Onboarding State Enum
- [ ] Create `src/main/java/com/hr/model/OnboardingState.java`:
  - Enum values: `DRAFT`, `VERIFIED`, `BACKGROUND_CHECKED`, `ACTIVE`, `REJECTED`
  - Include `nextValidStates()` helper method for decoy validation use

## OnboardingRequest Entity
- [ ] Create `src/main/java/com/hr/model/OnboardingRequest.java`:
  - `@Entity`, table `onboarding_requests`
  - Fields: id (Long, auto-generated), employeeId, currentState (OnboardingState), requestedBy, reviewedBy, createdAt, updatedAt

## Onboarding Repository
- [ ] Create `src/main/java/com/hr/repository/OnboardingRepository.java`:
  - `extends JpaRepository<OnboardingRequest, Long>`
  - `findByRequestedBy(String requestedBy)` — for decoy scoped list

## OnboardingWorkflowService (A04 Vulnerability)
- [ ] Create `src/main/java/com/hr/service/OnboardingWorkflowService.java`:
  - `transition(Long onboardingId, OnboardingState targetState)`:
    - Accepts ANY targetState without validating prerequisite sequence
    - Does NOT check: is currentState valid predecessor? Is background check done?
    - Adds comment: `// VULNERABILITY A04: Onboarding state machine accepts any targetState without validating prerequisite steps.`
    - Adds comment: `// CHAIN LINK 1 (chain-02): State machine allows bypassing Background Check by requesting Active directly.`
  - `getOnboarding(Long id)` — safe read method

## OnboardingController
- [ ] Create `src/main/java/com/hr/controller/OnboardingController.java`:
  - `POST /api/onboarding` → `createOnboarding()` — create new request
  - `GET /api/onboarding/{id}` → `getOnboarding()` — single request
  - `PUT /api/onboarding/{id}/transition` → `transitionState()` — calls vulnerable workflow service
  - `GET /api/onboarding` → `listOnboarding()` — **decoy**: scoped to `requestedBy == currentUser`

## Formalize Audit Endpoint (VULN-08)
- [ ] Edit `src/main/java/com/hr/controller/EmployeeController.java`:
  - In `getEmployeeAudit()` method:
    - Add comment: `// VULNERABILITY A01: Employee audit endpoint returns passwordHash for any employee by ID without authorization.`
    - Add comment: `// CHAIN LINK 1 (chain-03): Employee audit endpoint returns passwordHash for any employee by ID without authorization.`
  - In `getEmployee()` method (nearby safe endpoint):
    - Verify `@PreAuthorize` annotation is present (decoy was already there per inventory)

## Verification
- [ ] Restart app with Docker Compose
- [ ] Verify A04 vulnerability:
  - Create onboarding request → state is DRAFT
  - `PUT /api/onboarding/1/transition` with targetState=ACTIVE → should succeed (vulnerable!)
  - Verify that BACKGROUND_CHECKED was skipped
- [ ] Verify VULN-08:
  - `GET /api/employees/1/audit` → returns passwordHash field
  - Switch to different user → still returns hash
- [ ] Verify decoys:
  - `GET /api/onboarding` → only returns requests created by current user
  - `GET /api/employees/1` → requires proper role or ownership
- [ ] Verify existing vulnerabilities still exploitable:
  - A01 IDOR on payroll
  - A02 XOR decrypt SSN
  - A08 deserialization import
  - A08 Log4j via Kafka
  - chain-01: IDOR → XOR → exfiltration
- [ ] Run `mvn test` — all tests pass
- [ ] Run `./mvnw verify` if available

## Regular Commits
- [ ] Commit after onboarding entity + service + controller are created
- [ ] Commit after audit endpoint formalized
- [ ] Commit after full verification passes

## Phase Status Report
- [ ] Create `phase-02/status-report.md` after completion
