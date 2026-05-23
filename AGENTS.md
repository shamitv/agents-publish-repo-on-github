# AGENTS.md — Contribution Specification for secure-code-hunt

This file defines the rules and patterns that AI coding agents (and human contributors) **must follow** when implementing or extending any application in this repository.

---

## Repository Purpose

This is an **intentionally vulnerable application corpus** for benchmarking AI security-detection agents against OWASP Top 10: 2021.

- Every app contains **2–4 deliberately planted standalone vulnerabilities** covering specific OWASP categories.
- Every implemented app must also contain **≥ 1 chained vulnerability scenario** (see below).
- Apps must include **decoy safe code** to measure agent precision (false-positive rate).

---

## Directory Layout

```
apps/
  <language>/
    app-<NN>-<name>/
      src/              # All application source code
      README.md         # Human-readable spec (see template below)
      .vulns            # Machine-readable vulnerability manifest (JSON)
      Dockerfile        # Container build (optional for placeholder apps)
      pom.xml / package.json / requirements.txt / ...
```

---

## Implementing a New App — Checklist

1. **Scaffold the app** following the language conventions already present in the repo.
2. **Plant 2–4 standalone OWASP Top 10 vulnerabilities** with real, exploitable code — not just comments.
3. **Plant ≥ 1 chained vulnerability scenario** (see spec below).
4. **Add decoy safe patterns** near vulnerable code (parameterized queries next to injection points, proper auth guards on non-vulnerable routes, etc.).
5. **Write README.md** following the template below.
6. **Write `.vulns`** following the JSON schema below.

---

## Standalone Vulnerability Requirements

Each standalone vulnerability must be:
- **Real code** — exploitable by an actual attack, not just a comment or placeholder.
- **Annotated** in source with a comment: `// VULNERABILITY <OWASP_ID>: <brief description>`.
- Listed in `.vulns` under `"vulnerabilities"` with `owasp_id`, `location`, `method`, `severity`, `cwe`.

---

## Chained Vulnerability Scenario Requirements

### What is a chain?

A chained scenario consists of **2–3 code-level weaknesses**, each individually low or medium severity, that a real attacker can exploit in sequence to achieve a high-impact outcome.

### Chain rules

| Rule | Detail |
|------|--------|
| **Minimum steps** | 2 distinct code-level issues |
| **Maximum steps** | 3 distinct code-level issues |
| **Per-step severity** | Each step is individually `low` or `medium` |
| **Combined severity** | Chain outcome must be `high` or `critical` |
| **Real code** | Every chain step must be implemented as actual code, not documentation-only |
| **Comment marking** | Each chain link must be marked with a source comment: `// CHAIN LINK <N> (chain-<ID>): <description>` |
| **Decoy nearby** | Add at least one nearby safe pattern (a properly authorized endpoint, a sanitized query, etc.) to create a false-positive opportunity for detection agents |

### Required impact categories

Each chain must have one of the following impact values in `.vulns`:

| Impact | Meaning |
|--------|---------|
| `account_takeover` | Attacker gains control of a victim user account |
| `lateral_movement` | Attacker pivots from the compromised app to other internal systems or cloud resources |
| `db_exfiltration` | Attacker bulk-reads sensitive records (PII, credentials, financial data) |
| `data_modification` | Attacker writes unauthorized changes to stored records |

---

## README Template

Every app README **must** contain the following sections in this order:

```markdown
# <App Name>

## Overview
<1–2 sentence summary of what the app does.>

## Business Domain
<Industry / use case.>

## Tech Stack
<Language, framework, database, notable libraries.>

## Features
<Bullet list of main user-facing features.>

## Security Benchmarking
<Brief note that vulns are intentional; link to .vulns.>

---

## Chained Vulnerability Scenario

### Chain: "<Step A> → <Step B> [→ <Step C>] → <Impact>"

<1-sentence overview of who the attacker is and what they achieve.>

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | <description> | Low / Medium | A0X | `file.ext` → `method()` |
| 2 | <description> | Low / Medium | A0X | `file.ext` → `method()` |
| 3 (if applicable) | <description> | Low / Medium | A0X | `file.ext` → `method()` |

**Attack narrative**: <Step-by-step prose describing exactly how an attacker executes the chain.>

**Combined Impact**: <Single sentence stating the high/critical outcome.>

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
...

## Running Locally
...

## Running via Docker
...
```

---

## `.vulns` JSON Schema

```jsonc
{
  "app_id": "app-NN",
  "app_name": "Human Readable Name",
  "language": "python | java | typescript | javascript",
  "framework": "flask | django | fastapi | spring-boot | express | nestjs | ...",
  "vulnerabilities": [
    {
      "owasp_id": "A01",
      "category": "Broken Access Control",
      "location": "relative/path/to/File.java",
      "method": "methodName",
      "line_range": "10-25",           // optional but recommended
      "description": "Concise description of the vuln.",
      "severity": "low | medium | high | critical",
      "cwe": "CWE-639",
      "secondary_location": "..."      // optional
    }
  ],
  "chained_attacks": [
    {
      "chain_id": "chain-01",
      "chain_name": "Step A → Step B → Impact",
      "attack_scenario": "Narrative description of the full attack sequence.",
      "impact": "account_takeover | lateral_movement | db_exfiltration | data_modification",
      "components": [
        {
          "step": 1,
          "owasp_id": "A01",
          "description": "What this step does and why it matters.",
          "location": "relative/path/to/File.java",
          "method": "methodName",
          "severity": "low | medium",
          "cwe": "CWE-XXX"
        },
        {
          "step": 2,
          "owasp_id": "A03",
          "description": "...",
          "location": "...",
          "method": "...",
          "severity": "low | medium",
          "cwe": "CWE-XXX"
        }
      ]
    }
  ],
  "decoys": [
    {
      "location": "relative/path/to/File.java",
      "description": "Why this code looks vulnerable but is actually safe."
    }
  ]
}
```

---

## Language-Specific Conventions

### Python (Flask / Django / FastAPI)
- Plant SQL injection via raw string formatting into `cursor.execute()` or ORM `.raw()`.
- Plant IDOR by looking up objects with a user-supplied `id` parameter without checking ownership.
- Plant hardcoded secrets as module-level string constants.
- Use `os.environ` for chain link "debug exposure" endpoints.

### Java (Spring Boot)
- Plant injection via JPQL/LDAP string concatenation.
- Use `@PreAuthorize` with intentionally weak expressions for access-control flaws.
- Use Log4j 2.14.x (explicitly pinned in `pom.xml`) for Log4Shell chain links.
- Use XOR encryption with a hardcoded key for "weak crypto" chain links.

### TypeScript / JavaScript (Express / NestJS)
- Plant XSS via `innerHTML` rendering on the frontend or raw HTML strings in API responses.
- Plant SSRF via `axios.get(userSuppliedUrl)` with no URL validation.
- Plant session issues via cookie options missing `httpOnly` or `secure`.
- Use plaintext fields in mock DB objects for credential exposure.

---

## Naming Conventions

| Artifact | Convention | Example |
|----------|-----------|---------|
| App folder | `app-<NN>-<kebab-name>` | `app-01-ecommerce-catalog` |
| Chain ID | `chain-<NN>` (sequential per app) | `chain-01` |
| OWASP comment | `// VULNERABILITY <ID>: <brief>` | `// VULNERABILITY A01: IDOR on order endpoint` |
| Chain comment | `// CHAIN LINK <N> (chain-<ID>): <brief>` | `// CHAIN LINK 1 (chain-01): Exposes passwordHash` |

---

## What Agents Must NOT Do

- Do **not** fix existing standalone vulnerabilities — they are intentional benchmarks.
- Do **not** remove decoy safe patterns — they are required for precision testing.
- Do **not** add real authentication infrastructure; keep mock DBs and simple session cookies.
- Do **not** introduce actual network calls to external services in test code.
- Do **not** use `Math.random()` for anything security-relevant — use `crypto.randomBytes` or `SecureRandom` unless the intent is to plant a weak-randomness vulnerability.
