# Chained Vulnerability Scenarios — E-Commerce Product Catalog API

## Chain: "User Enumeration -> Session Forgery -> Catalog Modification"

An attacker combines three individually low/medium-severity issues to modify catalog data as an administrator.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/users/exists` confirms valid usernames without authentication | Low | A01 | `services/catalog-service/src/controllers/user_controller.py` -> `user_exists()` |
| 2 | Hardcoded Flask `SECRET_KEY` allows forged signed session cookies | Medium | A02 | `services/catalog-service/src/config/settings.py` -> `SECRET_KEY` |
| 3 | Product creation trusts the session role without stronger authorization proof | Medium | A01 | `services/catalog-service/src/controllers/product_controller.py` -> `create_product()` |

**Attack narrative**: The attacker probes `/api/users/exists?username=admin`, signs a Flask session cookie with the hardcoded key, and posts attacker-controlled catalog records through `/api/products`.

**Combined Impact**: Unauthorized catalog data modification.

---

## Chain: "Weak Supplier ID Validation -> Catalog Poisoning via Bulk Upload"

An attacker chains a weak validator with a trusting bulk upload endpoint to modify catalog data under a forged supplier identity.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Supplier ID validator accepts zero, negative, and non-numeric values without error | Low | A04 | `packages/domain/validators.py` -> `validate_supplier_id_chain()` |
| 2 | Bulk CSV upload trusts `supplierId` from request body without ownership verification | Medium | A01 | `services/catalog-service/src/controllers/bulk_upload_controller.py` -> `bulk_upload_products()` |

**Attack narrative**: The attacker crafts a CSV file containing a `supplierId` column set to a different supplier's ID (e.g., `supplier-002`). In step 1, the weak `validate_supplier_id_chain()` validator passes the forged ID through without rejecting it. In step 2, the bulk upload endpoint (`POST /api/products/bulk-upload`) reads the `supplierId` from the CSV and creates products under the forged identity without verifying the authenticated supplier owns that ID. The attacker can upload arbitrary catalog records attributed to any supplier.

**Combined Impact**: Unauthorized catalog data modification through forged supplier identity.

---

## Chain: "SSRF via Webhook URL -> Internal Service Access"

An attacker registers a webhook with a crafted callback URL pointing to internal services, and the webhook delivery system makes an outbound request to that URL, enabling SSRF.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Webhook delivery system makes HTTP requests to unvalidated user-supplied URLs | High | A10 | `services/reporting-service/src/services/webhook_retry.py` -> `create_delivery()` |

**Attack narrative**: The attacker registers a webhook with `callback_url` set to `http://169.254.169.254/latest/meta-data/` (AWS metadata endpoint) or `http://localhost:5000/admin/` (internal service). The registration succeeds without URL validation, and the delivery system attempts an HTTP POST to that URL, potentially exposing internal service data.

**Combined Impact**: Access to internal cloud metadata or internal service endpoints.

---

## Chain: "Custom Widget XSS -> Flag Metadata XSS -> Exfiltration"

An attacker injects script via a custom dashboard widget renderer, then leverages an unsanitized feature flag metadata endpoint to exfiltrate data.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Custom dashboard widget renders raw HTML templates with no CSP or sanitization | Low | A06 | `apps/typescript/app-01-supplier-portal/src/components/DashboardWidgets.tsx` -> `CustomWidgetRenderer()` |
| 2 | Admin flag detail page renders flag description via `dangerouslySetInnerHTML` without sanitization | Low | A06 | `apps/typescript/app-01-supplier-portal/src/pages/admin/FlagDetail.tsx` -> `AdminFlagDetailPage` |

**Attack narrative**: The attacker visits the custom widget builder page and submits an HTML template containing `<img src=x onerror=alert(document.cookie)>`. The `CustomWidgetRenderer` component renders this via `dangerouslySetInnerHTML` with no sanitization, executing the XSS payload in the supplier's browser session (step 1). Using the stolen session token, the attacker navigates to the admin console as a privileged user. The admin flag detail page renders the `description` field via `dangerouslySetInnerHTML` (step 2), which contains a second XSS payload that exfiltrates audit log data containing all supplier report records.

**Combined Impact**: Cross-site scripting enabling session theft and data exfiltration.

---

_This file is supplemental internal narrative. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
