# Prep-for-Runs — Preparation Plan for Agent Benchmarking

This directory contains the preparation plan for cleaning up app source code before running security agent benchmarks. The goal is to remove vulnerability annotations from source code and README files, moving that metadata exclusively into `.vulns` JSON manifests and `scenarios.md` files.

## Why

- **Agents should discover vulnerabilities organically**, not be guided by `// VULNERABILITY` comments.
- **Ground truth belongs in `.vulns` JSON** — machine-readable, single source of truth.
- **READMES should be user-facing docs**, not vulnerability lists.
- **Chained scenario narratives** move to `scenarios.md` per app.

## Workflow Per App

For each app, the following steps must be executed **in order**:

### Step A: Scan

Run a regex scan across all source files in the app directory to identify:
- `VULNERABILITY` annotations (source comments)
- `CHAIN LINK` annotations (source comments)
- `vulnerability` mentions in README.md (text references)

Record all hits so nothing is missed.

### Step B: Remove annotations from source code

Delete every `// VULNERABILITY`, `# VULNERABILITY`, `// CHAIN LINK`, `# CHAIN LINK` comment line from all source files (`.py`, `.js`, `.ts`, `.java`, `.html`, etc.).

The vulnerabilities themselves (the actual exploitable code) **must remain intact** — only the annotation comments are removed.

### Step C: Create `scenarios.md` (if not already present)

Extract the chained vulnerability scenario narrative from the README.md and place it in a new `scenarios.md` file in the app directory. The README.md should then:
- Remove the "Chained Vulnerability Scenario" section
- Replace it with a brief pointer line: `For chained vulnerability scenarios, see [scenarios.md](scenarios.md).`

### Step D: Update README.md

- Remove "Chained Vulnerability Scenario" section entirely (or replace with pointer to scenarios.md).
- Remove any "Security Benchmarking" or vulnerability metadata that's not user-facing.
- Keep the rest (Overview, Business Domain, Tech Stack, Features, API Endpoints, Running Locally, Running via Docker).

### Step E: Verify no remaining annotations

Run the same scan from Step A again. Confirm zero hits.

### Step F: Commit & push

```
git add apps/<language>/app-<NN>-<name>/
git commit -m "prep: clean vuln annotations from app-<NN>"
git push
```

### Step G: Update `.vulns` and difficulty stats (if needed)

After cleaning, review `.vulns` for accuracy — ensure location references still match, severity is correct, and add any missing metadata. Update `reports/` stats if difficulty scoring references source file line numbers that changed.

---

## App Inventory

### Python (Flask) — 14 apps ✅
| # | App | Status | Priority |
|---|-----|--------|----------|
| 1 | app-01-ecommerce-catalog | ✅ Done | High |
| 2 | app-02-patient-portal | ✅ Done | High |
| 3 | app-03-banking-service | ✅ Done | High |
| 4 | app-04-real-estate | ✅ Done | High |
| 5 | app-05-learning-mgmt | ✅ Done | High |
| 21 | app-21-insurance-claims | ✅ Done | High |
| 22 | app-22-food-delivery | ✅ Done | High |
| 23 | app-23-govt-permits | ✅ Done | High |
| 24 | app-24-vet-clinic | ✅ Done | High |
| 25 | app-25-supply-chain | ✅ Done | High |
| 46 | app-46-charity-donations | ✅ Done | High |
| 47 | app-47-smart-home | ✅ Done | High |
| 48 | app-48-freelancer-market | ✅ Done | High |
| 49 | app-49-sports-league | ✅ Done | High |

### Java (Spring Boot) — 6 apps ✅
| # | App | Status | Priority |
|---|-----|--------|----------|
| 6 | app-06-hr-management | ✅ Done | High |
| 7 | app-07-airline-booking | ✅ Done | High |
| 8 | app-08-warehouse-mgmt | ✅ Done | High |
| 9 | app-09-legal-documents | ✅ Done | High |
| 10 | app-10-telecom-billing | ✅ Done | High |
| 50 | app-50-energy-billing | ✅ Done | High |

### Java (additional) — 5 apps ✅
| # | App | Status | Priority |
|---|-----|--------|----------|
| 26 | app-26-pharma-tracking | ✅ Done | High |
| 27 | app-27-hotel-reservation | ✅ Done | High |
| 28 | app-28-mfg-quality | ✅ Done | High |
| 29 | app-29-fleet-management | ✅ Done | High |
| 30 | app-30-auction-platform | ✅ Done | High |

### JavaScript (Express) — 10 apps ✅
| # | App | Status | Priority |
|---|-----|--------|----------|
| 16 | app-16-restaurant-reviews | ✅ Done | High |
| 17 | app-17-iot-dashboard | ✅ Done | High |
| 18 | app-18-p2p-lending | ✅ Done | High |
| 19 | app-19-cms | ✅ Done | High |
| 20 | app-20-fitness-tracker | ✅ Done | High |
| 36 | app-36-parking-mgmt | ✅ Done | High |
| 37 | app-37-crop-planner | ✅ Done | High |
| 38 | app-38-museum-catalog | ✅ Done | High |
| 39 | app-39-wedding-planner | ✅ Done | High |
| 40 | app-40-pet-adoption | ✅ Done | High |

### JavaScript (additional) — 5 apps ✅
| # | App | Status | Priority |
|---|-----|--------|----------|
| 41 | app-41-library-reservation | ✅ Done | High |
| 42 | app-42-construction-tracker | ✅ Done | High |
| 43 | app-43-music-streaming | ✅ Done | High |
| 44 | app-44-election-polling | ✅ Done | High |
| 45 | app-45-travel-expense | ✅ Done | High |

### TypeScript (NestJS) — 10 apps ✅
| # | App | Status | Priority |
|---|-----|--------|----------|
| 11 | app-11-social-analytics | ✅ Done | High |
| 12 | app-12-crypto-wallet | ✅ Done | High |
| 13 | app-13-project-mgmt | ✅ Done | High |
| 14 | app-14-telemedicine | ✅ Done | High |
| 15 | app-15-digital-assets | ✅ Done | High |
| 31 | app-31-event-ticketing | ✅ Done | High |
| 32 | app-32-support-tickets | ✅ Done | High |
| 33 | app-33-recruitment-ats | ✅ Done | High |
| 34 | app-34-subscription-box | ✅ Done | High |
| 35 | app-35-compliance-tracker | ✅ Done | High |

---

## Execution Batches

### Batch 1: Python apps (14 apps)
Process all 14 Python apps sequentially. For each:
1. Scan → 2. Remove annotations → 3. Create/update scenarios.md → 4. Update README → 5. Verify → 6. Commit & push → 7. Update .vulns if needed

### Batch 2: Java apps (11 apps)
Same process for all 11 Java apps.

### Batch 3: JavaScript apps (15 apps)
Same process for all 15 JavaScript apps.

### Batch 4: TypeScript apps (10 apps)
Same process for all 10 TypeScript apps.

### Final pass
1. Global grep across entire repo for any remaining `VULNERABILITY` or `CHAIN LINK` patterns
2. Final commit with message: `"prep: final pass — verify all annotations removed"`
3. Update difficulty stats in reports/ if line numbers have shifted

---

## Task Definitions

For automation/reference, each app requires these atomic tasks:

| Task ID | Description | Scope |
|---------|-------------|-------|
| `scan-<NN>` | Scan all source files for VULNERABILITY/CHAIN LINK annotations | Per-app |
| `clean-<NN>` | Remove annotation comments from source code | Per-app |
| `scenario-<NN>` | Extract chain narrative to scenarios.md, update README | Per-app |
| `readme-<NN>` | Strip vulnerability metadata from README.md | Per-app |
| `verify-<NN>` | Re-scan to confirm zero remaining annotations | Per-app |
| `commit-<NN>` | `git add`, `git commit`, `git push` for this app | Per-app |
| `vulns-<NN>` | Review and update `.vulns` JSON and difficulty stats | Per-app |