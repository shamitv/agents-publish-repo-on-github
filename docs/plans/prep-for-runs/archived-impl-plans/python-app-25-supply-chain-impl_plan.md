# Implementation Plan - Supply Chain Inventory Tracker (App 25)

This application has been implemented as a Flask-based microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A06: Vulnerable and Outdated Components**:
   - Location: `requirements.txt` / `app.py`
   - Vulnerable code: Pins `PyYAML==5.3.1` and calls `yaml.load()` on dynamic remote inputs.
2. **A07: Identification and Authentication Failures**:
   - Location: `app.py` → `login()`
   - Vulnerable code: Plaintext password storage and comparison, session cookie lacks the `secure` flag.
3. **A10: Server-Side Request Forgery**:
   - Location: `app.py` → `check_supplier_api()`
   - Vulnerable code: Arbitrary client-controlled URL fetched without validation.

## Chained Attack
- **Chain-01**: SSRF (A10) → YAML Deserialization (A06)
- Attacker targets internal network via SSRF and triggers remote code execution via unsafe deserialization of the fetched payload.

## Decoys
- Safe YAML config loading using `yaml.safe_load()`.
- Parameterized warehouse search query preventing SQL injection.
