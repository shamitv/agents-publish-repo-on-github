# Audit Report: app-49 — Sports League Management

**Language:** Python (Flask)  
**Business Domain:** Sports / League Management  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR on Player Profiles)

**Severity:** Medium  
**Location:** `app.py:173-187` — `get_player()`  
**Lines:**
```python
# VULNERABILITY A01: No role or ownership check on player profile endpoint.
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A01`
- Any authenticated user can view any player's salary and contract data
- No role or ownership validation

### VULN-02: A03 — Injection (SQL Injection)

**Severity:** High  
**Location:** `app.py:153-171` — `search_players()`  
**Lines:**
```python
# VULNERABILITY A03: User input concatenated into raw SQL query.
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A03`
- Direct concatenation enables UNION-based extraction
- Can dump all database records

### VULN-03: A05 — Security Misconfiguration (Schema Leak in Headers)

**Severity:** Low  
**Location:** `app.py:121-136` — `export_standings()`  
**Lines:**
```python
# VULNERABILITY A05: Raw SQL query commands exposed in response headers.
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A05`
- Response headers include internal SQL query text
- Reveals table schema and column names

---

## Chained Attack: chain-01

**Chain Name:** SQLi Player Dump → IDOR Contract Access → Score Manipulation  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: MEDIUM**

### Link 1: SQL Injection for Record Enumeration (A03 — Medium)

**Difficulty: EASY**

- SQLi in player search leaks player IDs and team manager info

### Link 2: IDOR on Player Details (A01 — Low)

**Difficulty: EASY**

- Extracted player IDs used to view salary/contract data

### Link 3: Score Manipulation via Missing Access Control (A01 — Medium)

**Difficulty: EASY**

- Game score update endpoint lacks authorization
- Any authenticated user can modify league standings

---

## Summary

App-49 is a Flask sports league manager with SQLi, IDOR on player profiles, schema leaks in response headers, and missing access control on score updates. Chain: SQLi to enumerate → exploit IDOR → manipulate game scores.

**Overall Difficulty Score:** 1/5 (Easy)