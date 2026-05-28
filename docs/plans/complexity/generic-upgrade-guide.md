# Generic Complexity Upgrade Guide

Apply this process to any benchmark app whose row in the [master complexity README](README.md) reads "Phase structure pending" or is not yet listed. Currently this covers the apps outside the 8 dedicated complexity-plan apps (01, 05, 06, 10, 11, 14, 17, 36). It produces the same artifact set -- `expansion-plan.md`, `vuln-inventory.md`, `eval-report.md`, and per-phase `plan.md` + `TODO.md` + `status-report.md` -- following the patterns validated on [app-01](realistic/0.1/app-01-ecommerce-catalog/expansion-plan.md) and [app-05](app-05-learning-mgmt/expansion-plan.md).

---

## Table of Contents

1. [Overview & Prerequisites](#1-overview--prerequisites)
2. [Step 1: App Inventory](#2-step-1-app-inventory)
3. [Step 2: Target Architecture Decision (Randomized)](#3-step-2-target-architecture-decision-randomized)
4. [Step 3: Vulnerability & Chain Design](#4-step-3-vulnerability--chain-design)
5. [Step 4: Phase Definition & Templates](#5-step-4-phase-definition--templates)
6. [Step 5: Implementation](#6-step-5-implementation)
7. [Step 6: Evaluation -- Difficulty + Hint Leakage](#7-step-6-evaluation--difficulty--hint-leakage)
8. [Step 7: Artifact Generation](#8-step-7-artifact-generation)
9. [Appendix A: Template Files](#appendix-a-template-files)
10. [Appendix B: Language-Specific Notes](#appendix-b-language-specific-notes)

---

## 1. Overview & Prerequisites

### What this guide produces

For each target app, you will generate:

| Artifact | Purpose | Created when |
|----------|---------|-------------|
| `expansion-plan.md` | Master plan: architecture, vulnerability strategy, phases | Before implementation |
| `vuln-inventory.md` | No-touch zone: every existing vuln, chain, decoy | Before implementation |
| `phase-NN/plan.md` | Per-phase scope, decisions, vuln planting table | Before implementation |
| `phase-NN/TODO.md` | Granular task checklist with commit/status-report items | Before implementation |
| `phase-NN/status-report.md` | Post-implementation summary for the phase | After implementation |
| `eval-report.md` | Difficulty ratings + hint leakage validation | After all phases |
| `README.md` | App-level plan index (`docs/plans/complexity/app-<NN>-<name>/README.md`) | Before implementation |

### Prerequisites -- Annotation Check

Before starting the inventory, verify the app has the required benchmark annotations. Search the source files:

```bash
rg -n "VULNERABILITY|CHAIN LINK" apps/<lang>/app-<NN> -g "*.{py,java,ts,js}"
```

**If annotations exist**: The app already meets AGENTS.md requirements. Proceed to [Step 1: App Inventory](#2-step-1-app-inventory).

**If zero annotations are found** (common for apps in the generic scope, e.g., `apps/java/app-08-warehouse-mgmt`, `apps/javascript/app-16-restaurant-reviews`): Run the **annotation baseline** below before continuing.

#### Annotation Baseline

1. **Scan for exploitable patterns** in the source code. Look for:
   - Raw string formatting into SQL/query strings (A03 injection targets)
   - Endpoints that look up records by user-supplied ID without ownership checks (A01 IDOR targets)
   - Hardcoded keys, secrets, or credentials in config or model files (A02 targets)
   - Unsafe deserialization calls (`pickle.loads`, `ObjectInputStream.readObject`, etc.) (A08 targets)
   - Unauthenticated routes returning env vars / config / debug info (A05 targets)
   - Logging calls with string concatenation and user-controlled data (A09 targets)
   - HTTP clients that fetch user-supplied URLs without validation (A10 targets)

2. **Plant 2-4 annotated standalone vulnerabilities**. For each exploitable pattern found, add a source comment:
   `// VULNERABILITY <OWASP_ID>: <brief description>`

3. **Plant 1 or more chained scenarios**. Identify 2-3 weaknesses that can be combined for high impact. Annotate each step:
   `// CHAIN LINK <N> (chain-<ID>): <description>`

4. **Create or rebuild `.vulns`** with the `vulnerabilities`, `chained_attacks`, and `decoys` arrays per the AGENTS.md JSON schema.

5. **Plant at least 2 decoy safe patterns** near vulnerable code. Document them in `.vulns.decoys`.

6. **Verify annotation presence** by re-running the search from step 0 -- all annotations must be found.

Then proceed to [Step 1: App Inventory](#2-step-1-app-inventory).

### Other Prerequisites

- The app already exists in `apps/<language>/app-<NN>-<name>/`
- You have read AGENTS.md and understand the benchmark annotation rules

### Constraints (never violated)

1. Never remove or fix an existing `// VULNERABILITY` or `// CHAIN LINK` annotation
2. Never remove or weaken an existing decoy pattern listed in `.vulns.decoys`
3. Every new vulnerability must have real, exploitable code -- not a comment
4. Every new chain step must have a `// CHAIN LINK N (chain-ID): description` source comment
5. Near every vulnerable code path, add at least one decoy safe pattern
6. Update the app's `.vulns`, `apps/<lang>/app-<NN>-<name>/README.md`, and `scenarios.md` after every phase

---

## 2. Step 1: App Inventory

Before designing anything, document the app's current state. Follow the pattern from [app-05's vuln-inventory.md](app-05-learning-mgmt/vuln-inventory.md).

### 2.1 Collect baseline data

```
App ID:      app-<NN>
Name:        <human readable name>
Language:    python | java | typescript | javascript
Framework:   flask | spring-boot | express | nestjs
File count:  <count source files (.py/.java/.ts/.js)>
Complexity:  <from APPLICATION_COMPLEXITY.md if available, else estimate 1-5>
Entry point: <app.py / Application.java / server.ts / server.js>
```

### 2.2 Catalog existing vulnerabilities

Search for `// VULNERABILITY` in all source files. For each one, record:

```yaml
id: VULN-01
owasp_id: A01
cwe: CWE-639
file: src/services/<file>.py
method: methodName
severity: high | medium | low | critical
annotation: // VULNERABILITY A01: <exact comment text>
```

### 2.3 Catalog existing chain links

Search for `// CHAIN LINK` in all source files. Group by chain ID:

```yaml
chain_id: chain-01
steps:
  - step: 1
    owasp_id: A01
    file: src/services/<file>.py
    method: methodName
    annotation: // CHAIN LINK 1 (chain-01): <exact text>
  - step: 2
    ...
```

### 2.4 Catalog existing decoys

Read `.vulns.decoys` array and verify each decoy still exists in source.

### 2.5 Map current architecture

```
src/
  controllers/     - <endpoints>
  services/        - <business logic>
  repositories/    - <data access>
  routes/          - <route definitions>
  config/          - <settings, connections>
  consumers/       - <async workers>
  models/          - <data models>
  workers/         - <background tasks>
```

### 2.6 Identify OWASP gaps

List which OWASP Top 10:2021 categories are NOT covered by existing standalone vulnerabilities or chain links. These gaps are the priority targets for new vulnerabilities.

---

## 3. Step 2: Target Architecture Decision (Randomized)

### 3.1 Component pool

Select 2--5 components from the pool below. Each adds concrete infrastructure and creates new vulnerability opportunities.

| # | Component | Domain Fit | Language Support | New Vuln Opportunities | Decoy Opportunity |
|---|-----------|-----------|-----------------|----------------------|-------------------|
| 1 | **Message Queue** (Kafka / RabbitMQ) | Async workflows, notifications, event pipelines | Python: `kafka-python` / `pika`; Java: `spring-kafka`; TS/JS: `kafkajs` / `amqplib` | A08 deserialization on consumer; A09 missing audit on event processing | Parameterized handler on a different topic |
| 2 | **Search Engine** (Elasticsearch / OpenSearch) | Product search, log search, full-text queries | Python: `elasticsearch-py`; Java: `spring-data-elasticsearch`; TS/JS: `@elastic/elasticsearch` | A03 query DSL injection; A05 exposed cluster config | Parameterized query on a different index |
| 3 | **Cache** (Redis / Memcached) | Session store, rate limiting, frequently-read data | Python: `redis-py`; Java: `spring-data-redis`; TS/JS: `redis` / `ioredis` | A02 cached sensitive data in plaintext; A05 exposed cache port | TTL-expired cache that safely discards secrets |
| 4 | **Second Database** (MongoDB / TimescaleDB / InfluxDB) | Polyglot persistence, document store, time-series | Python: `pymongo` / `psycopg2`; Java: `mongo-driver` / `timescaledb`; TS/JS: `mongoose` / `pg` | A01 IDOR across DB boundaries; A04 weak cross-DB validation | Session-scoped query in the primary DB |
| 5 | **File Storage** (local disk / MinIO / S3) | Uploads, attachments, report exports | All: `boto3` / `aws-sdk` / `multer` / `fs` | A01 unauthenticated file access by ID; A10 SSRF on upload URL | Signed-URL verification on a different endpoint |
| 6 | **Batch Scheduler** (APScheduler / Quartz / node-cron) | Scheduled tasks, digest emails, batch processing | Python: `APScheduler`; Java: `spring-boot-starter-quartz`; TS/JS: `node-cron` | A04 insecure scheduling parameters; A09 missing execution audit | Strict validation on a different schedule endpoint |
| 7 | **WebSocket** (Socket.IO / ws / flask-sock) | Live dashboards, real-time notifications | Python: `flask-socketio`; Java: `spring-websocket`; TS/JS: `ws` / `socket.io` | A07 weak WS authentication; A03 injection via WS messages | REST endpoint with proper auth in the same controller |
| 8 | **External API Proxy** (HTTP client / webhooks) | Third-party integrations, webhook callbacks | All: `requests` / `RestTemplate` / `axios` | A10 SSRF on webhook URL; A08 integrity failure on webhook payload | Hostname allowlist on a different endpoint |
| 9 | **Separate UI App** (React / Vue / SPA) | Admin dashboard, client portal, analytics | All serve via REST; UI in any framework | A05 CORS misconfiguration; A07 weak session tokens in SPA | Same-origin policy on a different route |
| 10 | **Second Service** (microservice split) | Reporting service, auth service, worker service | Any language; communicate via REST/gRPC | A01 cross-service IDOR; A10 SSRF between services | Internal-only endpoint with network policy |

### 3.2 Randomization procedure

1. **Determine count**: Roll 1d4+1 for 2--5 components
2. **Filter pool**: Remove components that make no sense for the app's domain
   - Example: a static CMS app doesn't need WebSockets
   - Example: a simple contact form doesn't need a second DB
   - Example: an app with no upload features doesn't need file storage
3. **Roll**: For each slot, roll on the filtered pool
4. **Re-roll on duplicate**: Each component should appear at most once
5. **Re-roll once on poor fit**: If a rolled component seems forced, roll again

### 3.3 Minimum viable complexity

Every upgrade must include at least:
- **1 infrastructure component** from pool items 1--8 (not just a UI app)
- **+1 new standalone vulnerability** beyond existing ones
- **+1 new chain step** (extend an existing chain or create a new one)

### 3.4 Record the decisions

Document the chosen components and rationale in `expansion-plan.md`:

```markdown
## Architecture Changes

### Selected Components

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Message Queue | Apache Kafka | App processes async order confirmations |
| Search Engine | Elasticsearch | Product catalog needs fuzzy search |
| Cache | Redis | Rate limiting on login endpoint |

### Rejected Components (with reason)

| Component | Reason |
|-----------|--------|
| WebSocket | App has no real-time dashboard |
| Second DB | Existing SQLite sufficient for data model |

### Randomization Roll

Roll: 1d4+1 = 3 components. Pool after domain filtering: 7 eligible.
Selected by roll: MQ (Kafka), Search (ES), Cache (Redis).
```

---

## 4. Step 3: Vulnerability & Chain Design

### 4.1 Map components to vulnerabilities

For each selected component, plant 1--2 new vulnerabilities. Use this mapping as a starting point:

| Component | Primary Vuln | Secondary Vuln | Decoy |
|-----------|-------------|----------------|-------|
| MQ | A08: unsafe deserialization from topic | A09: missing audit on event processing | Parameterized message handler on a different topic |
| Search | A03: raw string concatenation into query DSL | A05: search index exposes sensitive fields | Parameterized query on a different index |
| Cache | A02: plaintext secrets in cache | A05: cache admin port exposed | TTL-expiring cache that safely discards |
| Second DB | A01: IDOR across DB boundaries | A04: inconsistent validation between DBs | Session-scoped query in primary DB |
| File Storage | A01: unauthenticated file access by ID | A10: SSRF in upload URL fetch | Signed-URL verification on a different endpoint |
| Batch Scheduler | A04: insecure scheduling params | A09: no execution audit log | Strict param validation on a different schedule |
| WebSocket | A07: no auth on WS connection | A03: injection via WS messages | REST endpoint with proper auth in same controller |
| External API Proxy | A10: SSRF on webhook URL | A08: unsigned webhook payload accepted | Hostname allowlist on a different endpoint |
| Separate UI App | A05: CORS allows any origin | A07: session token in URL fragment | Same-origin policy on a different route |
| Second Service | A01: cross-service IDOR | A10: SSRF from one service to another | Internal-only endpoint with network restriction |

### 4.2 Chain design

**Rules** (from AGENTS.md, validated on app-01 and app-05):
- 2--3 distinct code-level issues per chain
- Each step individually low or medium severity
- Combined impact must be high or critical
- Must be real, exploitable code
- Each step annotated: `// CHAIN LINK N (chain-ID): description`
- Nearby decoy safe pattern for each step

**Common chain patterns** (adapt to your component choices):

| Pattern | Steps | Combined Impact |
|---------|-------|-----------------|
| Config Leak -> SSRF Pivot | A05 (expose internal topology) -> A10 (fetch internal URL) | `lateral_movement` |
| Weak Validation -> Missing Audit | A04 (accept bad input) -> A09 (apply without logging) | `data_modification` |
| IDOR -> Weak Crypto | A01 (read any record) -> A02 (decrypt with hardcoded key) | `db_exfiltration` |
| Weak Auth -> Session Forge -> IDOR | A07 (weak cookie) -> A02 (predictable session) -> A01 (read any user's data) | `account_takeover` |
| Debug Leak -> Deserialization RCE | A05 (expose classpath/internal info) -> A08 (unsafe deserialization) | `lateral_movement` |
| SSRF -> Cache Poisoning | A10 (internal HTTP request) -> A04 (write into cache without validation) | `data_modification` |

### 4.3 Decoy placement rules

For every new vulnerable code path:
1. Place a decoy safe pattern **in the same file** or **in an adjacent file in the same directory**
2. The decoy should accept similar inputs but apply proper validation, parameterization, or auth checks
3. Document the decoy in `plan.md` under "Decoy Patterns" with the table format:

```markdown
| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `src/services/import_service.py` -> `fetch_metadata()` | Same file as SSRF; also accepts a URL parameter | Validates hostname against an allowlist before fetching |
```

---

## 5. Step 4: Phase Definition & Templates

### 5.1 Determine phase count

| Components Selected | Recommended Phases | Phase Structure |
|-------------------|-------------------|-----------------|
| 2 | 3 | Infra + Comp1 -> Comp2 -> Verify |
| 3 | 4 | Infra -> DB -> MQ/Batch -> UI/Verify |
| 4 | 5 | Infra -> DB1 -> DB2 -> MQ -> UI/Verify |
| 5 | 6 | Infra -> DB -> Search -> MQ -> UI -> Verify |

### 5.2 Generic phase map

| Phase | Title | Content | Always? |
|-------|-------|---------|---------|
| 1 | **Infrastructure + Docker Compose** | `docker-compose.yml`, healthchecks, dependency injection, stub->real config swap | Yes |
| 2 | **Core Data Migration** | Additional DB schemas, seed data, repository port | If component includes a database |
| 3 | **Service Layer + Business Logic** | New service classes, algorithms, validators | If MQ, Batch, or Search selected |
| 4 | **Async Queue / Streaming** | Wire MQ or batch scheduler, implement consumers/workers | If MQ or Batch selected |
| 5 | **UI / Real-time / Polish** | Dashboards, WebSockets, final integrations | If UI or WS selected |
| Last | **Verification + Metadata** | Chains, decoys, `.vulns`/README/scenarios.md sync, eval | Yes |

### 5.3 Template: `expansion-plan.md`

```markdown
# App <NN> (<name>) -- Complexity Upgrade Expansion Plan

## Overview

<1-2 sentences about the upgrade. Example (from app-05):
Upgrade the LMS from stub-backed infrastructure (SQLite, in-memory Kafka mock) 
to a Docker-orchestrated system with real PostgreSQL, MongoDB, Apache Kafka, 
auto-grading logic, and portal dashboards.>

> **Non-goals / Constraints**
> - Do not remove or fix any planted vulnerability in [vuln-inventory.md](./vuln-inventory.md).
> - Add 1--2 new standalone vulnerabilities per phase.
> - Add decoy safe code near vulnerable-looking code.
> - Update `.vulns`, `README.md`, `scenarios.md` each phase.

## Current State

| Property | Value |
|----------|-------|
| App ID | `app-<NN>` |
| Language | <language> |
| Framework | <framework> |
| File count | <N> |
| Standalone vulns | <N> (<OWASP IDs>) |
| Chain scenarios | <N> (<chain-IDs>) |
| Decoys | <N> |
| OWASP gaps | <uncovered categories> |

## Architecture Changes

### Selected Components

| Component | Technology | Vulnerability Target |
|-----------|-----------|---------------------|
| <component> | <tech> | A0X, A0Y |
| <component> | <tech> | A0X |
...

## Vulnerability Planting Strategy

| Phase | New OWASP | Component Used | Decoy |
|-------|-----------|---------------|-------|
| 1 | -- | -- | -- |
| 2 | A0X | <component> | <description> |
...

## Phase Summary

| Phase | Title | Scope | New Vulns |
|-------|-------|-------|-----------|
| 1 | <title> | <summary> | -- |
| 2 | <title> | <summary> | A0X |
...

## Data Model Changes

<new tables, collections, or entities>

## API Endpoint Inventory

<existing + new endpoints>

## Security Benchmark Considerations

<decoy rules, annotation rules, metadata update rules>
```

### 5.4 Template: `vuln-inventory.md`

Follow the [app-05 vuln-inventory.md](app-05-learning-mgmt/vuln-inventory.md) exactly. Sections:

```markdown
# Vulnerability Inventory -- App <NN> (<name>)

## Purpose
## App Profile
## Standalone Vulnerabilities (table per vuln)
## Chained Vulnerability Scenarios (table per chain)
## Decoy Patterns (table per decoy)
## No-Touch Files (table)
## OWASP Coverage Gap Analysis
```

### 5.5 Template: `phase-NN/plan.md`

```markdown
# Phase <NN>: <Title>

## Goal

<single paragraph describing what this phase achieves>

## Scope

### Included
- [ ] <task>
- [ ] <task>

### Excluded
- <what is deliberately out of scope>

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| <choice> | <reasoning> |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone / Chain Link | A0X | CWE-XXX | <file> -> <method> | <description> | Medium |

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | <file> -> <method> | <reason> | <reason> |

## Data Model Changes

<new tables, entities, collections>

## API Contracts

<new endpoints or changes to existing ones>

## Artifact Updates

- `.vulns`: <additions>
- `README.md`: <sections to update>
- `scenarios.md`: <chains to add>
- `tests/`: <test updates>

## Dependencies on Other Phases

- **Depends on**: Phase <N> -- <reason>
- **Required by**: Phase <N> -- <reason>
```

### 5.6 Template: `phase-NN/TODO.md`

```markdown
# Phase <NN> TODO -- <Title>

## Pre-requisites
- [ ] Prior phase complete and verified
- [ ] Read vuln-inventory.md -- confirm no-touch files

## <Task Group 1>
- [ ] <granular task>
- [ ] <granular task>

## <Task Group 2>
- [ ] <granular task>
- [ ] <granular task>

## Regular Commits
- [ ] Commit after each major task:
  `git add -A && git commit -m "app-<NN> phase-<NN>: <descriptive message>"`
- [ ] Push to remote after each commit

## Phase Status Report
- [ ] Create `phase-<NN>/status-report.md` after completion:
  - What was implemented
  - Files created (count)
  - Files modified (count)
  - Vulnerabilities planted (type, location)
  - Decoys planted (location)
  - Existing vulns still intact? (yes/no)
  - Chains functional? (yes/no)
  - Tests passing? (yes/no)
  - Blockers

## Verification
- [ ] All existing vulnerabilities still exploitable
- [ ] All new vulnerabilities exploitable
- [ ] Decoys present near vulnerable code paths
- [ ] No regression in existing endpoint responses
- [ ] `.vulns` updated with new VULNERABILITY entries
- [ ] `README.md` chain section updated
- [ ] `scenarios.md` updated with new chain narratives
- [ ] Run any existing tests: `<test command>`
```

---

## 6. Step 5: Implementation

### 6.1 Execution order

Implement phases strictly in order. Each phase must be complete and verified before starting the next.

### 6.2 Commit cadence

| When | Commit message format |
|------|----------------------|
| After each major task | `app-<NN> phase-<NN>: <task> -- <brief detail>` |
| At phase completion | `app-<NN> phase-<NN>: <title> -- <N> files, <M> vulns, <D> decoys` |

### 6.3 Status report format

Create `phase-<NN>/status-report.md` at the end of each phase:

```markdown
# Phase <NN> Status Report -- app-<NN> <name>

## Summary
- **Phase**: <title>
- **Files created**: <N>
- **Files modified**: <M>
- **New vulnerabilities**: <V> (<OWASP IDs>)
- **New decoys**: <D>
- **Chains advanced**: <chain-ID> step <N>

## Verification
- Existing vulnerabilities intact: [PASS] / [FAIL]
- New vulnerabilities exploitable: [PASS] / [FAIL]
- Decoys present: [PASS] / [FAIL]
- `.vulns` updated: [PASS] / [FAIL]
- README updated: [PASS] / [FAIL]
- scenarios.md updated: [PASS] / [FAIL]
- Tests passing: [PASS] / [FAIL]

## Changes Made

### Files Created
- <path>
- <path>

### Files Modified
- <path>
- <path>

### Vulnerabilities Planted
- VULN-0<N> (A0X): <file> -> <method> -- <description>

### Blockers
- <none or list>
```

---

## 7. Step 6: Evaluation -- Difficulty + Hint Leakage

### 7.1 Difficulty rating

After all phases are complete, rate each vulnerability and chain on a 1--5 scale:

| Rating | Label | Criteria |
|--------|-------|----------|
| 1 | Trivial | Single HTTP request, no auth needed |
| 2 | Easy | Requires authentication or simple parameter manipulation |
| 3 | Moderate | Requires understanding service topology or multi-step request |
| 4 | Hard | Requires cross-service exploitation or custom tooling |
| 5 | Expert | Requires chaining 3+ steps across services with specialized payloads |

Record ratings in `eval-report.md`:

```markdown
## Difficulty Assessment

| Vuln ID | OWASP | Location | Difficulty | Rationale |
|---------|-------|----------|------------|-----------|
| VULN-04 | A04 | `controller/enrollment.py:enroll()` | 1 | Single POST with bad course_id |
| VULN-05 | A09 | `workers/grading_listener.py:grade()` | 2 | Submit quiz, then check audit table is empty |
| VULN-06 | A10 | `services/import_service.py:fetch_content()` | 3 | Need debug leak first + craft internal URL |
| VULN-07 | A07 | `controllers/auth.py:dashboard_login()` | 1 | Inspect cookie headers after login |
| chain-01 | A05->A02->A01 | 3 services | 4 | Three-step across debug, auth, submission services |
| chain-02 | A04->A09 | 2 services | 3 | Enroll path -> grading pipeline |
| chain-03 | A05->A10 | 2 services | 3 | Debug leak -> SSRF pivot |
```

### 7.2 Hint leakage validation

Search all source files for benchmark keywords **outside** the permitted locations:

**Permitted locations** (leakage allowed here):
- Source annotation comments (`// VULNERABILITY`, `// CHAIN LINK`, `// DECOY`)
- `.vulns` JSON file
- `README.md` (dedicated chain section only)
- `scenarios.md`
- Files under `docs/plans/complexity/`

**Forbidden locations** (hints found here = leakage):
- Any `.py`, `.java`, `.ts`, `.js`, `.html` source file NOT containing an annotation
- Test files
- Configuration files (beyond `.vulns`)
- Docker files
- `requirements.txt` / `pom.xml` / `package.json` (dependency-pinning comments)

**Search commands**:

```bash
# Python -- search only .py files, excluding permit-list files
rg -n "VULNERABILITY|CHAIN LINK|DECOY|intentional vuln|benchmark" \
  apps/<lang>/app-<NN> \
  -g "*.py" \
  -g "!**/.vulns" \
  -g "!**/README.md" \
  -g "!**/scenarios.md" \
  -g "!docs/plans/complexity/**" \
  | grep -v "VULNERABILITY\|CHAIN LINK\|DECOY"

# Java -- search only .java files
rg -n "VULNERABILITY|CHAIN LINK|DECOY|intentional vuln|benchmark" \
  apps/<lang>/app-<NN> \
  -g "*.java" \
  -g "!**/.vulns" \
  -g "!**/README.md" \
  -g "!**/scenarios.md" \
  -g "!docs/plans/complexity/**" \
  | grep -v "VULNERABILITY\|CHAIN LINK\|DECOY"

# TypeScript/JavaScript -- search .ts and .js
rg -n "VULNERABILITY|CHAIN LINK|DECOY|intentional vuln|benchmark" \
  apps/<lang>/app-<NN> \
  -g "*.{ts,js}" \
  -g "!**/.vulns" \
  -g "!**/README.md" \
  -g "!**/scenarios.md" \
  -g "!docs/plans/complexity/**" \
  | grep -v "VULNERABILITY\|CHAIN LINK\|DECOY"
```

**Validation result**: Add to `eval-report.md`:

```markdown
## Hint Leakage Validation

| Search Scope | Files Scanned | Matches | Status |
|-------------|---------------|---------|--------|
| All `.py` source files | 37 | 0 outside annotations | [PASS] PASS |
| Test files | 1 | 0 | [PASS] PASS |
| Config files (non-.vulns) | 5 | 0 | [PASS] PASS |
| Docker files | 2 | 0 | [PASS] PASS |

**Result**: ZERO matches outside the permit list. No hint leakage detected.
```

---

## 8. Step 7: Artifact Generation

### 8.1 Final directory structure

```
docs/plans/complexity/app-<NN>-<name>/
|-- README.md                    # App-level index (see below)
|-- expansion-plan.md            # Master plan
|-- vuln-inventory.md            # No-touch inventory
|-- eval-report.md               # Difficulty ratings + hint leakage
|-- phase-01/
|   |-- plan.md
|   |-- TODO.md
|   '-- status-report.md         # Generated post-implementation
|-- phase-02/
|   |-- plan.md
|   |-- TODO.md
|   '-- status-report.md
'-- ...                          # Additional phases
```

### 8.2 App-level README template

```markdown
# Complexity Upgrade Plan -- app-<NN>: <name>

## Overview

<1-2 sentences describing the upgrade>

## Architecture Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| <component> | <tech> | <role> |

## Phase Index

| Phase | Title | Focus | New Vulns | Status |
|-------|-------|-------|-----------|--------|
| [1](phase-01/plan.md) | <title> | <scope> | -- | Not started / Complete |
| [2](phase-02/plan.md) | <title> | <scope> | A0X | Not started / Complete |
| [3](phase-03/plan.md) | <title> | <scope> | A0X | Not started / Complete |
| [4](phase-04/plan.md) | <title> | <scope> | A0X | Not started / Complete |
| [5](phase-05/plan.md) | <title> | <scope> | -- | Not started / Complete |

## Key Documents

| Document | Description |
|----------|-------------|
| [expansion-plan.md](./expansion-plan.md) | Master plan |
| [vuln-inventory.md](./vuln-inventory.md) | No-touch zone reference |
| [eval-report.md](./eval-report.md) | Difficulty ratings + hint leakage |

## OWASP Coverage

<Before -> After summary>
```

---

## Appendix A: Template Files

All templates above are designed to be copied verbatim and filled in for each app. They are also embedded in the file structure of [app-05](app-05-learning-mgmt/) as concrete examples.

Quick-reference links to example files:

| Artifact | Example |
|----------|---------|
| `expansion-plan.md` | [app-05/expansion-plan.md](app-05-learning-mgmt/expansion-plan.md) |
| `vuln-inventory.md` | [app-05/vuln-inventory.md](app-05-learning-mgmt/vuln-inventory.md) |
| `phase-NN/plan.md` | [app-05/phase-03/plan.md](app-05-learning-mgmt/phase-03/plan.md) |
| `phase-NN/TODO.md` | [app-05/phase-03/TODO.md](app-05-learning-mgmt/phase-03/TODO.md) |
| `README.md` | [app-05/README.md](app-05-learning-mgmt/README.md) |
| `eval-report.md` | (this guide defines the format; no example yet) |

---

## Appendix B: Language-Specific Notes

### Python (Flask)

- Use `flask` Blueprints for modular controllers
- Docker base image: `python:3.11-slim`
- Testing: `pytest`
- Config pattern: `os.environ.get("VAR", "default")` with a `settings.py`

### Java (Spring Boot)

- Use `@RestController`, `@Service`, `@Repository` annotations
- Docker base image: `eclipse-temurin:17-jre-alpine`
- Testing: `@SpringBootTest` with `@AutoConfigureMockMvc`
- Dependency management: Maven `pom.xml` or Gradle `build.gradle`
- For Log4j chains: pin `log4j-core:2.14.1` explicitly (as done in app-06 plan)

### TypeScript / JavaScript (Express)

- Use `express.Router()` for modular routes
- Docker base image: `node:20-alpine`
- Testing: `jest` or `mocha`
- Config pattern: `process.env.VAR || 'default'`

### Common Docker patterns

```yaml
services:
  db:
    image: postgres:15-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
  app:
    build: .
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8085:8085"
```
