# Implementation Plans — secure-code-hunt

This directory contains phased implementation plans for completing all 50 intentionally vulnerable applications in the secure-code-hunt benchmark.

## Current Status Summary

| Status | Count | Apps |
|--------|-------|------|
| 🟢 **Done** (source + report) | 12 | 01, 02, 03, 04, 06, 07, 08, 09, 11, 12, 13, 23 |
| 🟡 **Need Report Only** | 1 | 23 (has source, no .vulns/report) |
| 🔴 **Need Full Implementation** | 37 | All others (scaffold-only) |

## Implementation Phases

| Phase | Focus | Apps | Effort |
|-------|-------|------|--------|
| [Phase 1 — Inventory](phase-01-inventory/PLAN.md) | Deep file audit of all 50 apps | All | ✅ Done |
| [Phase 2 — Missing Reports](phase-02-existing-reports/PLAN.md) | Generate report for app-23 | 23 | Small |
| [Phase 3 — Python Apps](phase-03-python-apps/PLAN.md) | Implement 9 Python scaffolds | 05, 21, 22, 24, 25, 46, 47, 48, 49 | Large |
| [Phase 4 — Java Apps](phase-04-java-apps/PLAN.md) | Implement 7 Java scaffolds | 10, 26, 27, 28, 29, 30, 50 | Medium |
| [Phase 5 — JavaScript Apps](phase-05-javascript-apps/PLAN.md) | Implement 15 JavaScript scaffolds | 16, 17, 18, 19, 20, 36-45 | Large |
| [Phase 6 — TypeScript Apps](phase-06-typescript-apps/PLAN.md) | Implement 7 TypeScript scaffolds | 14, 15, 31, 32, 33, 34, 35 | Medium |
| [Phase 7 — Documentation](phase-07-documentation/PLAN.md) | Update READMEs, generate master TODO | N/A | Small |

## OWASP Difficulty Distribution Goal

To create a good benchmark, we need a mix of difficulty across the 50 apps:

| Difficulty | Target Count | Current | Remaining |
|------------|-------------|---------|-----------|
| ★☆☆☆☆ Very Easy | 5 | 1 (app-12) | 4 |
| ★★☆☆☆ Easy | 12 | 4 (03, 09, 11, 13) | 8 |
| ★★★☆☆ Medium | 18 | 5 (01, 02, 04, 06, 07) | 13 |
| ★★★★☆ Medium-Hard | 10 | 1 (app-08) | 9 |
| ★★★★★ Hard | 5 | 0 | 5 |

## Vuln Planting Rules (from AGENTS.md)

Each app must have:
- **2–4 standalone OWASP Top 10 vulnerabilities** (real, exploitable code)
- **≥ 1 chained vulnerability scenario** (2–3 low/medium steps → high/critical impact)
- **Decoy safe patterns** near vulnerable code (for false-positive testing)
- Required chain impacts: `account_takeover`, `lateral_movement`, `db_exfiltration`, `data_modification`

## Key Design Principles

1. **Coverage completeness**: Target gaps in OWASP coverage (A04, A05, A06, A07, A08, A09 are underrepresented)
2. **Difficulty spread**: Mix easy-to-find vulns with subtle ones (crypto flaws, deserialization chain steps)
3. **Domain variety**: Banking, healthcare, logistics, social media, etc.
4. **Framework variety**: Flask + Django (Python), Spring Boot (Java), Express (JS/TS), NestJS (TS)

---

*Last updated: 2026-05-24*