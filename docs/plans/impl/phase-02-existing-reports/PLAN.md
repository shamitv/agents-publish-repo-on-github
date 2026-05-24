# Phase 2 — Generate Report for Existing Source (app-23)

**Status:** 🔴 TODO  
**App:** app-23 — Government Permits Portal  
**Language:** Python (Django)  
**Source files:** 10 files (`.py` source code present)

## Objective

Analyze the existing Django source code in `apps/python/app-23-govt-permits/` and:
1. Identify all planted vulnerabilities
2. Document them in a `.vulns` JSON manifest
3. Create a detailed audit report in `reports/`
4. Identify any chained attack scenarios

## Steps

- [ ] Read all `.py` source files in the app
- [ ] Examine `models.py` for data exposure / crypto issues
- [ ] Examine `views.py` for access control / injection issues
- [ ] Examine `urls.py` for exposed endpoints
- [ ] Examine `settings.py` for misconfiguration
- [ ] Identify standalone vulnerabilities (2–4 required)
- [ ] Identify chained scenarios (1 required)
- [ ] Create `.vulns` manifest following the JSON schema
- [ ] Create `reports/app-23-govt-permits.md`
- [ ] Update `reports/README.md` to include app-23

## Expected OWASP Coverage

Based on being a govt permits portal with Django, likely vulns:
- A01: Broken Access Control (IDOR on permit lookups)
- A03: Injection (SQLi via raw queries or insufficient ORM usage)
- A05: Security Misconfiguration (DEBUG=true or exposed admin)
- A09: Insufficient Logging (no audit trail for permit approvals)