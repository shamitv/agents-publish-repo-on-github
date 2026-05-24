# Chained Vulnerability Scenarios — Smart Home

## Chain: "Debug Token Leak → SSRF Internal Recon → Unsigned Firmware Injection"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug endpoint leaks device API tokens | Medium | A05 | `app.py` → `debug_devices()` |
| 2 | Sensor data proxy fetches internal URLs (SSRF) | Medium | A10 | `app.py` → `fetch_sensor_data()` |
| 3 | Device firmware update downloads unsigned binaries | Medium | A08 | `app.py` → `update_firmware()` |


**Attack narrative**: 1. The attacker makes a GET request to the public endpoint `/api/debug/devices`. Due to misconfiguration, this endpoint does not require authentication and returns the list of all active smart home devices alongside their authentication token keys.
2. The attacker uses these tokens to authenticate requests to the sensor data proxy at `/api/devices/sensor-data?url=http://192.168.1.1:8000`. By passing various internal URLs, the attacker performs SSRF-based port scanning to find local servers.
3. The attacker hosts a malicious firmware binary on an internal host (or uses SSRF to proxy it from an external host).
4. The attacker sends a POST request to `/api/devices/{device_id}/firmware/update`, providing the path to the malicious firmware.
5. The hub downloads the file and installs the update without confirming its signature or checksum, giving the attacker control of the smart appliance.

**Combined Impact**: `lateral_movement` — The attacker gains execution capability on the local firmware of the IoT devices and pivots onto the local home network.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
