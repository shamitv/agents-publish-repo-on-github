# Audit Report: app-17 — IoT Device Dashboard

**Language:** JavaScript (Express)  
**Business Domain:** IoT / Smart Home  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures (Cleartext Secrets)

**Severity:** Medium  
**Location:** `src/index.js:52-63` — `initDb`  
**Lines:**
```javascript
// VULNERABILITY A02: Storing device credentials/access keys in cleartext in the database
```

**Difficulty: EASY**

- Device secret keys (`IOT-DEV-KEY-THERMO-1122`, `IOT-DEV-KEY-GATEWAY-8877`) stored in plaintext
- Directly readable from database queries without any encryption

### VULN-02: A05 — Security Misconfiguration (Information Leakage)

**Severity:** Medium  
**Location:** `src/index.js:134-173` — `POST /api/devices/command`  
**Lines:**
```javascript
// VULNERABILITY A05: Security Misconfiguration - Verbose Error Disclosure
```

**Difficulty: EASY**

- Sending `TRIGGER-ERROR` command causes server to return full stack trace plus `gateway_config`
- Leaks internal telemetry server URL and access key `INTERNAL-SECRET-TELEMETRY-TOKEN-2026`

### VULN-03: A10 — Server-Side Request Forgery (SSRF)

**Severity:** High  
**Location:** `src/index.js:175-192` — `POST /api/devices/refresh`  
**Lines:**
```javascript
// VULNERABILITY A10: Server-Side Request Forgery (SSRF)
```

**Difficulty: EASY**

- `statusUrl` parameter is fetched directly via `axios.get()` with no validation
- Can access internal endpoints like `http://localhost:8017/api/internal/telemetry`
- No IP filtering or allowlist

---

## Chained Attack: chain-01

**Chain Name:** Command Error Leak → SSRF Internal Pivot  
**Combined Impact:** Lateral Movement  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Verbose Error Disclosure (A05 — Medium)

**Difficulty: EASY**

- Send `POST /api/devices/command` with `{ "deviceId": 1, "command": "TRIGGER-ERROR" }`
- Response leaks `telemetry_access_key: INTERNAL-SECRET-TELEMETRY-TOKEN-2026` and the telemetry URL

### Link 2: SSRF to Internal Endpoint (A10 — Medium)

**Difficulty: EASY**

- Send `POST /api/devices/refresh` with `{ "statusUrl": "http://localhost:8017/api/internal/telemetry?token=INTERNAL-SECRET-TELEMETRY-TOKEN-2026" }`
- Server proxies request to internal telemetry endpoint, returning all device secret keys

---

## Summary

App-17 is a JavaScript Express IoT dashboard with plaintext device secrets, a verbose error handler that leaks internal telemetry credentials, and an SSRF vulnerability in the device refresh endpoint. Chain: Command error leak → SSRF internal pivot → device credential exfiltration.

**Overall Difficulty Score:** 2/5 (Easy)