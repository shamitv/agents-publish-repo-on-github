# Chained Vulnerability Scenarios — Social Analytics

## Chain: "SSRF to Cloud Metadata → Full Credential Response → IAM Key Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `POST /api/preview` fetches any URL server-side via `axios.get()` with no IP blocklist, hostname validation, or DNS rebinding protection — allows reaching `169.254.169.254` (AWS IMDS) | Medium | A10 | `src/index.ts` → `/api/preview` handler |
| 2 | The SSRF response previously truncated output to 500 characters; truncation removed so the full metadata service response body is returned to the caller. AWS IMDSv1 IAM credential payloads are 600+ bytes and would have been cut off | Low | A05 | `src/index.ts` → `/api/preview` handler |
| 3 | `GET /api/debug/headers` returns all incoming request headers, including proxy-injected internal routing headers; a client proxying through the metadata fetch can extract forwarded authorization headers | Low | A05 | `src/index.ts` → `/api/debug/headers` handler |


**Attack narrative**: The attacker posts `{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}` to `/api/preview`. The SSRF returns the full IAM role name. A follow-up request fetches `http://169.254.169.254/latest/meta-data/iam/security-credentials/{role}` and the complete response (now untruncated) delivers `AccessKeyId`, `SecretAccessKey`, and `Token`. The attacker uses these temporary credentials to assume the instance role and pivot across cloud resources.

**Combined Impact**: Complete AWS IAM credential exfiltration enabling lateral movement across cloud infrastructure.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
