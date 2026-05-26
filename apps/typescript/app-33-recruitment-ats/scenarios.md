# Chained Vulnerability Scenarios — Recruitment Ats

## Chain: "Predictable API Key Derivation → Zip Slip Arbitrary File Write"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Predictable API token generated using MD5 on sequential IDs | Medium | A02 | `src/index.ts` → `POST /api/auth/api-key` |
| 2 | ZIP archive extraction vulnerability (Zip Slip) | High | A06 | `src/index.ts` → `POST /api/applications/upload-portfolio` |


**Attack narrative**: 1. The attacker knows that user ID 3 corresponds to the recruiter admin.
2. The attacker knows that the application generates API tokens via `md5(userId)`.
3. The attacker calculates the recruiter API key: `md5("3") = eccbc87e4b5ce2fe28308fd9f2a7baf3`.
4. Using this key, the attacker authenticates as the recruiter, bypassing the login interface.
5. The attacker calls `/api/applications/upload-portfolio`, uploading a ZIP payload containing a file entry named `../../package.json` (or similar application files).
6. The zip handler extracts the file directly into the server's workspace directories, achieving arbitrary file write/overwrite.

**Combined Impact**: `data_modification` — Attacker bypasses authentication and overwrites critical application files on the server.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
