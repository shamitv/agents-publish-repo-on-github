# Implementation Plan - Smart Home Device Manager (App 47)

This application has been implemented as a FastAPI-based microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A05: Security Misconfiguration**:
   - Location: `app.py` → `debug_devices()`
   - Vulnerable code: Exposed unauthenticated debug endpoint leaking device access keys.
2. **A08: Software and Data Integrity Failures**:
   - Location: `app.py` → `update_firmware()`
   - Vulnerable code: Downloads and applies firmware updates without validating signatures or checksums.
3. **A10: Server-Side Request Forgery**:
   - Location: `app.py` → `fetch_sensor_data()`
   - Vulnerable code: Telemetry proxy makes HTTP requests to arbitrary user-controlled URLs.

## Chained Attack
- **Chain-01**: Debug Token Leak (A05) → SSRF Internal Recon (A10) → Unsigned Firmware Injection (A08)
- Attacker leaks credentials via debug endpoint, scans internal networks via SSRF, and deploys unsigned malicious firmware to IoT devices.

## Decoys
- Device-level token checking (`X-Device-Token`) before executing device command dispatches.
- User-level rate-limiting check (1-second cooldown) on status polling endpoints.
