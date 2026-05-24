# Audit Report: app-47 — Smart Home Device Manager

**Language:** Python (FastAPI)  
**Business Domain:** IoT / Smart Home  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A05 — Security Misconfiguration (Debug Endpoint Leaks)

**Severity:** High  
**Location:** `app.py:110-118` — `debug_devices()`  
**Lines:**
```python
# VULNERABILITY A05: Unauthenticated debug endpoint leaks all device tokens.
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A05`
- No authentication required to access `/api/debug/devices`
- Leaks device IDs, names, and private API tokens

### VULN-02: A08 — Integrity Failures (Unsigned Firmware Injection)

**Severity:** High  
**Location:** `app.py:132-163` — `update_firmware()`  
**Lines:**
```python
# VULNERABILITY A08: Firmware endpoint downloads from URL without checking signature or hash.
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A08`
- Accepts any URL for firmware download
- No cryptographic signature verification
- No hash check before installation

### VULN-03: A10 — Server-Side Request Forgery

**Severity:** Medium  
**Location:** `app.py:120-130` — `fetch_sensor_data()`  
**Lines:**
```python
# VULNERABILITY A10: SSRF via user-controlled sensor data URL.
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A10`
- User-supplied URL is fetched via `requests.get(url)` with no validation
- Can probe internal network

---

## Chained Attack: chain-01

**Chain Name:** Debug Token Leak → SSRF Internal Recon → Unsigned Firmware Injection  
**Combined Impact:** Lateral Movement  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Debug Endpoint Leaks Device Tokens (A05 — Medium)

**Difficulty: EASY**

- Unauthenticated endpoint leaks device tokens

### Link 2: SSRF for Internal Recon (A10 — Medium)

**Difficulty: EASY**

- SSRF probes internal network to find hosts/services

### Link 3: Unsigned Firmware Injection (A08 — Medium)

**Difficulty: EASY**

- Malicious firmware loaded via SSRF-discovered internal host

---

## Summary

App-47 is a FastAPI IoT manager with an unauthenticated debug endpoint, SSRF in sensor proxy, and unsigned firmware updates. Chain: leak tokens → probe internals → deploy malicious firmware.

**Overall Difficulty Score:** 1/5 (Easy)