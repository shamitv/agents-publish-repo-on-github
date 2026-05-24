# Prep-for-Runs Plan: Clean Vulnerability Annotations from All 50 Apps

## Objective

Prepare the repository for agent benchmarking runs by:
1. **Scanning** every source file in each app for vulnerability annotations
2. **Removing** all `VULNERABILITY` and `CHAIN LINK` comments from source code (keep only in `.vulns`)
3. **Moving** chained scenario details from `README.md` into separate `scenarios.md` per app
4. **Committing + pushing** after each app's cleanup
5. **Verifying** `.vulns` JSON and updating difficulty stats if needed

---

## Rationale

- `// VULNERABILITY` and `// CHAIN LINK` comments are implementation-time annotations that make detection **trivial** for agents
- `README.md` currently contains the full chained scenario narrative, which also leaks metadata to benchmarking agents
- `.vulns` JSON must remain as the **single source of truth** for ground-truth vulnerability data
- `scenarios.md` will hold the human-readable chain narrative for internal reference

---

## Inventory: 50 Apps

### Python (14 apps)
| # | ID | Name | Location |
|---|-----|------|----------|
| 1 | app-01 | E-Commerce Catalog | `apps/python/app-01-ecommerce-catalog/` |
| 2 | app-02 | Patient Portal | `apps/python/app-02-patient-portal/` |
| 3 | app-03 | Banking Service | `apps/python/app-03-banking-service/` |
| 4 | app-04 | Real Estate Platform | `apps/python/app-04-real-estate/` |
| 5 | app-05 | Learning Management System | `apps/python/app-05-learning-mgmt/` |
| 6 | app-21 | Insurance Claims | `apps/python/app-21-insurance-claims/` |
| 7 | app-22 | Food Delivery | `apps/python/app-22-food-delivery/` |
| 8 | app-23 | Government Permits | `apps/python/app-23-govt-permits/` |
| 9 | app-24 | Veterinary Clinic | `apps/python/app-24-vet-clinic/` |
| 10 | app-25 | Supply Chain Tracker | `apps/python/app-25-supply-chain/` |
| 11 | app-46 | Charity Donations | `apps/python/app-46-charity-donations/` |
| 12 | app-47 | Smart Home Manager | `apps/python/app-47-smart-home/` |
| 13 | app-48 | Freelancer Marketplace | `apps/python/app-48-freelancer-market/` |
| 14 | app-49 | Sports League Management | `apps/python/app-49-sports-league/` |

### Java (11 apps)
| # | ID | Name | Location |
|---|-----|------|----------|
| 15 | app-06 | HR Management | `apps/java/app-06-hr-management/` |
| 16 | app-07 | Airline Booking | `apps/java/app-07-airline-booking/` |
| 17 | app-08 | Warehouse Management | `apps/java/app-08-warehouse-mgmt/` |
| 18 | app-09 | Legal Document Manager | `apps/java/app-09-legal-documents/` |
| 19 | app-10 | Telecom Billing | `apps/java/app-10-telecom-billing/` |
| 20 | app-26 | Pharmaceutical Tracking | `apps/java/app-26-pharma-tracking/` |
| 21 | app-27 | Hotel Reservation | `apps/java/app-27-hotel-reservation/` |
| 22 | app-28 | Manufacturing QC | `apps/java/app-28-mfg-quality/` |
| 23 | app-29 | Fleet Management | `apps/java/app-29-fleet-management/` |
| 24 | app-30 | Auction Platform | `apps/java/app-30-auction-platform/` |
| 25 | app-50 | Energy Utility Billing | `apps/java/app-50-energy-billing/` |

### JavaScript (15 apps)
| # | ID | Name | Location |
|---|-----|------|----------|
| 26 | app-16 | Restaurant Reviews | `apps/javascript/app-16-restaurant-reviews/` |
| 27 | app-17 | IoT Dashboard | `apps/javascript/app-17-iot-dashboard/` |
| 28 | app-18 | P2P Lending | `apps/javascript/app-18-p2p-lending/` |
| 29 | app-19 | CMS | `apps/javascript/app-19-cms/` |
| 30 | app-20 | Fitness Tracker | `apps/javascript/app-20-fitness-tracker/` |
| 31 | app-36 | Parking Management | `apps/javascript/app-36-parking-mgmt/` |
| 32 | app-37 | Crop Planner | `apps/javascript/app-37-crop-planner/` |
| 33 | app-38 | Museum Catalog | `apps/javascript/app-38-museum-catalog/` |
| 34 | app-39 | Wedding Planner | `apps/javascript/app-39-wedding-planner/` |
| 35 | app-40 | Pet Adoption | `apps/javascript/app-40-pet-adoption/` |
| 36 | app-41 | Library Reservation | `apps/javascript/app-41-library-reservation/` |
| 37 | app-42 | Construction Tracker | `apps/javascript/app-42-construction-tracker/` |
| 38 | app-43 | Music Streaming | `apps/javascript/app-43-music-streaming/` |
| 39 | app-44 | Election Polling | `apps/javascript/app-44-election-polling/` |
| 40 | app-45 | Travel & Expense | `apps/javascript/app-45-travel-expense/` |

### TypeScript (10 apps)
| # | ID | Name | Location |
|---|-----|------|----------|
| 41 | app-11 | Social Analytics | `apps/typescript/app-11-social-analytics/` |
| 42 | app-12 | Crypto Wallet | `apps/typescript/app-12-crypto-wallet/` |
| 43 | app-13 | Project Management | `apps/typescript/app-13-project-mgmt/` |
| 44 | app-14 | Telemedicine | `apps/typescript/app-14-telemedicine/` |
| 45 | app-15 | Digital Assets | `apps/typescript/app-15-digital-assets/` |
| 46 | app-31 | Event Ticketing | `apps/typescript/app-31-event-ticketing/` |
| 47 | app-32 | Support Tickets | `apps/typescript/app-32-support-tickets/` |
| 48 | app-33 | Recruitment ATS | `apps/typescript/app-33-recruitment-ats/` |
| 49 | app-34 | Subscription Box | `apps/typescript/app-34-subscription-box/` |
| 50 | app-35 | Compliance Tracker | `apps/typescript/app-35-compliance-tracker/` |

---

## Per-App Workflow

Each app follows the same 5-step process:

### Step A — SCAN
**Action**: Recursively read all source code files in the app directory (excluding `.vulns`, `package-lock.json`, binary assets in `static/`, `node_modules`). Identify:
- All `// VULNERABILITY ...` or `# VULNERABILITY ...` or `/* VULNERABILITY ... */` comments
- All `// CHAIN LINK ...` or `# CHAIN LINK ...` or `/* CHAIN LINK ... */` comments
- The "Chained Vulnerability Scenario" section in `README.md`
- Any other vulnerability-descriptive comments in source

### Step B — REMOVE vuln annotations from source code
**Action**: Strip all `VULNERABILITY` and `CHAIN LINK` comment lines from source files. Keep the underlying vulnerable code **intact** — only remove the annotation comments.

**What to remove** (examples):
- `// VULNERABILITY A03: Raw SQL string concatenation mapping user-input parameters (SQL Injection target)`
- `// CHAIN LINK 1 (chain-01): User enumeration endpoint.`
- `// VULNERABILITY A01: IDOR. Checks order details by ID directly without verifying owner...`
- Multi-line block comments that describe vulnerabilities

**What to keep**:
- Decoy safe-pattern comments (e.g., `// Decoy: Secure, parameterized SQL query for login verification`)
- TODO or implementation notes that don't describe vulnerabilities
- All vulnerable code, function logic, imports, etc.

### Step C — MOVE chain details to `scenarios.md`
**Action**:
1. Extract the full "Chained Vulnerability Scenario" section from `README.md` (everything from `## Chained Vulnerability Scenario` to the next `##` heading or end-of-file)
2. Create `scenarios.md` in the app root with the extracted content
3. Update `README.md`:
   - Remove the extracted "Chained Vulnerability Scenario" section
   - Replace with a single line: `For detailed chained vulnerability scenarios, see [scenarios.md](scenarios.md).`
   - Keep all other sections intact (Overview, Business Domain, Tech Stack, Features, API Endpoints, Running, etc.)

**`scenarios.md` template**:
```markdown
# Chained Vulnerability Scenarios — <App Name>

## Chain: "<Chain Name>"

<Full attack narrative as extracted from README>

### Steps

| Step | Issue | Severity | OWASP | Location |
|------|-------|----------|-------|----------|
| 1 | <desc> | <sev> | <ID> | <loc> |
| 2 | <desc> | <sev> | <ID> | <loc> |
| 3 | <desc> | <sev> | <ID> | <loc> |

**Combined Impact**: <impact description>

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
```

### Step D — COMMIT and PUSH
**Action**:
```bash
git add apps/<language>/app-<NN>-<name>/
git commit -m "prep(app-<NN>): clean vuln annotations, extract scenarios.md"
git push
```

### Step E — UPDATE `.vulns` and difficulty stats (as needed)
**Action**: After each app, verify the `.vulns` JSON is accurate. If any difficulty scores or severity ratings need adjustment, update them. Also update `docs/plans/impl/README.md` difficulty stats if changed.

---

## Execution Order

Process apps in batches by language to maintain focus:

### Batch 1: Python (14 apps) — app-01..05, app-21..25, app-46..49
1. `python/app-01-ecommerce-catalog`
2. `python/app-02-patient-portal`
3. `python/app-03-banking-service`
4. `python/app-04-real-estate`
5. `python/app-05-learning-mgmt`
6. `python/app-21-insurance-claims`
7. `python/app-22-food-delivery`
8. `python/app-23-govt-permits`
9. `python/app-24-vet-clinic`
10. `python/app-25-supply-chain`
11. `python/app-46-charity-donations`
12. `python/app-47-smart-home`
13. `python/app-48-freelancer-market`
14. `python/app-49-sports-league`

### Batch 2: Java (11 apps) — app-06..10, app-26..30, app-50
15. `java/app-06-hr-management`
16. `java/app-07-airline-booking`
17. `java/app-08-warehouse-mgmt`
18. `java/app-09-legal-documents`
19. `java/app-10-telecom-billing`
20. `java/app-26-pharma-tracking`
21. `java/app-27-hotel-reservation`
22. `java/app-28-mfg-quality`
23. `java/app-29-fleet-management`
24. `java/app-30-auction-platform`
25. `java/app-50-energy-billing`

### Batch 3: JavaScript (15 apps) — app-16..20, app-36..45
26. `javascript/app-16-restaurant-reviews`
27. `javascript/app-17-iot-dashboard`
28. `javascript/app-18-p2p-lending`
29. `javascript/app-19-cms`
30. `javascript/app-20-fitness-tracker`
31. `javascript/app-36-parking-mgmt`
32. `javascript/app-37-crop-planner`
33. `javascript/app-38-museum-catalog`
34. `javascript/app-39-wedding-planner`
35. `javascript/app-40-pet-adoption`
36. `javascript/app-41-library-reservation`
37. `javascript/app-42-construction-tracker`
38. `javascript/app-43-music-streaming`
39. `javascript/app-44-election-polling`
40. `javascript/app-45-travel-expense`

### Batch 4: TypeScript (10 apps) — app-11..15, app-31..35
41. `typescript/app-11-social-analytics`
42. `typescript/app-12-crypto-wallet`
43. `typescript/app-13-project-mgmt`
44. `typescript/app-14-telemedicine`
45. `typescript/app-15-digital-assets`
46. `typescript/app-31-event-ticketing`
47. `typescript/app-32-support-tickets`
48. `typescript/app-33-recruitment-ats`
49. `typescript/app-34-subscription-box`
50. `typescript/app-35-compliance-tracker`

---

## Files Per App That Need Scanning

### Python apps
- `app.py` (or `main.py` / `manage.py`)
- `src/` directory (all `.py` files)
- `tests/` (all `.py` files — decoy tests may reference vulns)
- `README.md`

### Java apps
- `src/main/java/` (all `.java` files)
- `src/test/java/` (all `.java` files)
- `README.md`

### JavaScript / TypeScript apps
- `src/` (all `.js` / `.ts` files)
- `public/` (all `.js` files in frontend)
- `tests/` (all test files)
- `README.md`

---

## `impl_plan.md` Archiving

Each app currently contains an `impl_plan.md` file that may describe vulnerabilities and implementation details. These must be **moved** (not deleted) to a centralized archive under `docs/plans/prep-for-runs/archived-impl-plans/`.

### Step-by-step:

1. Create the archive directory:
   ```bash
   mkdir -p docs/plans/prep-for-runs/archived-impl-plans
   ```

2. For each app, move the file with a language + app-ID prefixed name:
   ```bash
   git mv apps/<language>/app-<NN>-<name>/impl_plan.md docs/plans/prep-for-runs/archived-impl-plans/<language>-app-<NN>-<name>-impl_plan.md
   ```

### Naming convention:
```
<language>-app-<NN>-<name>-impl_plan.md
```

**Examples:**
- `python-app-01-ecommerce-catalog-impl_plan.md`
- `java-app-06-hr-management-impl_plan.md`
- `javascript-app-16-restaurant-reviews-impl_plan.md`
- `typescript-app-11-social-analytics-impl_plan.md`

### When to archive:
During Step C of each app's workflow, run the `git mv` command above **before** committing. This way, the archive and cleanup happen in the same commit.

---

## Regex Patterns to Find Vuln Annotations

### Language-specific comment patterns to search for:

**Python**:
- `# VULNERABILITY .*`
- `# CHAIN LINK .*`
- Multi-line `""" ... VULNERABILITY ... """` or `''' ... VULNERABILITY ... '''`

**Java**:
- `// VULNERABILITY .*`
- `// CHAIN LINK .*`
- `/\* VULNERABILITY .* \*/`
- `/\* CHAIN LINK .* \*/`

**JavaScript / TypeScript**:
- `// VULNERABILITY .*`
- `// CHAIN LINK .*`
- `/\* VULNERABILITY .* \*/`
- `/\* CHAIN LINK .* \*/`

### Search command template:
```bash
cd apps/<language>/app-<NN>-<name>/
grep -rn "VULNERABILITY\|CHAIN LINK" --include="*.py" --include="*.java" --include="*.js" --include="*.ts" --include="*.md" .
```

---

## Validation Checklist (Per App)

After completing steps A–E for each app, verify:

- [ ] No `VULNERABILITY` or `CHAIN LINK` comments remain in any source file (`*.py`, `*.java`, `*.js`, `*.ts`)
- [ ] `README.md` no longer contains the "Chained Vulnerability Scenario" section
- [ ] `README.md` references `scenarios.md` and `.vulns` for vulnerability details
- [ ] `scenarios.md` exists with the full chain details
- [ ] `.vulns` JSON is intact and accurate
- [ ] `impl_plan.md` no longer references vuln annotations (or is deleted)
- [ ] All source code is intact (no code changes — only comment removals)
- [ ] App still runs correctly (optional: quick smoke test)
- [ ] Changes committed and pushed

---

## Final Pass (After All 50 Apps)

1. **Update `docs/plans/impl/README.md`** if any difficulty stats changed
2. **Update `reports/README.md`** if any report references need updating
3. **Run a global grep** to ensure zero remaining vuln annotations across the entire `apps/` tree:
   ```bash
   grep -rn "VULNERABILITY\|CHAIN LINK" apps/ --include="*.py" --include="*.java" --include="*.js" --include="*.ts" || echo "ALL CLEAN"
   ```
4. **Commit + push** the final validation commit

---

## Summary Checklist (All 50 Apps)

| # | App | SCAN | REMOVE | MOVE to scenarios.md | COMMIT+PUSH | UPDATE .vulns |
|---|-----|------|--------|---------------------|-------------|---------------|
| 1 | app-01 | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | app-02 | ☐ | ☐ | ☐ | ☐ | ☐ |
| ... | ... | ... | ... | ... | ... | ... |
| 50 | app-50 | ☐ | ☐ | ☐ | ☐ | ☐ |