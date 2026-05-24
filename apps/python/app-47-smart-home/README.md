# Smart Home Device Manager

## Overview
A FastAPI web application representing an IoT Smart Home Hub, allowing residents to register smart home devices, execute commands, view sensor telemetry, and trigger remote firmware updates.

## Business Domain
IoT & Smart Home Automation

## Tech Stack
- Python 3.10
- FastAPI
- SQLite (in-memory)

## Features
- User login & session management
- Register and view smart home devices (Thermostat, Lock, Garage)
- Send commands to specific devices (with token verification decoy)
- Proxy request telemetry from sensor data endpoints
- Apply device firmware updates from remote download URLs
- Rate-limited status checking

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/python/app-47-smart-home/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "Debug Token Leak → SSRF Internal Recon → Unsigned Firmware Injection"

An attacker leaks device tokens via an exposed debug endpoint, conducts internal reconnaissance via SSRF, and installs arbitrary unsigned firmware on registered home appliances.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug endpoint leaks device API tokens | Medium | A05 | `app.py` → `debug_devices()` |
| 2 | Sensor data proxy fetches internal URLs (SSRF) | Medium | A10 | `app.py` → `fetch_sensor_data()` |
| 3 | Device firmware update downloads unsigned binaries | Medium | A08 | `app.py` → `update_firmware()` |

**Attack narrative**:
1. The attacker makes a GET request to the public endpoint `/api/debug/devices`. Due to misconfiguration, this endpoint does not require authentication and returns the list of all active smart home devices alongside their authentication token keys.
2. The attacker uses these tokens to authenticate requests to the sensor data proxy at `/api/devices/sensor-data?url=http://192.168.1.1:8000`. By passing various internal URLs, the attacker performs SSRF-based port scanning to find local servers.
3. The attacker hosts a malicious firmware binary on an internal host (or uses SSRF to proxy it from an external host).
4. The attacker sends a POST request to `/api/devices/{device_id}/firmware/update`, providing the path to the malicious firmware.
5. The hub downloads the file and installs the update without confirming its signature or checksum, giving the attacker control of the smart appliance.

**Combined Impact**: `lateral_movement` — The attacker gains execution capability on the local firmware of the IoT devices and pivots onto the local home network.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/login` | None | Authenticate user and receive session cookie |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/debug/devices` | None | Leak registered devices and access tokens (vulnerable debug endpoint) |
| GET    | `/api/devices/sensor-data` | Session | Proxy request telemetry data (vulnerable to SSRF) |
| POST   | `/api/devices/{device_id}/firmware/update` | Session | Trigger device firmware update (vulnerable to unsigned binaries) |
| POST   | `/api/devices/{device_id}/command` | Session + Token | Send command to device (Decoy: validates device token) |
| GET    | `/api/devices/{device_id}/status` | Session | Poll device current status (Decoy: rate-limited) |

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. The application runs on port `8097`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-47-smart-home .
   ```
2. Run the container:
   ```bash
   docker run -p 8097:8097 app-47-smart-home
   ```
