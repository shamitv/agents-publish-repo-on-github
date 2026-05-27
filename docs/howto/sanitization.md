# Sanitizing a Project for Benchmark Scanning

## Overview

Every app in this repository contains **inline source annotations** — comments like `// VULNERABILITY A01: ...`, `// CHAIN LINK 1 (chain-01): ...`, and `// DECOY: ...` — that are **required by the AGENTS.md spec** during authoring. These annotations let maintainers verify that vulnerability plantings conform to the specification.

However, these same annotations **contaminate the benchmark** when an AI scanning agent reads them. An agent that sees `// VULNERABILITY A01: IDOR returns any order by ID` doesn't need to *find* the vulnerability — it just needs to *parse the comment*.

**Solution**: Before scanning, produce a **sanitized copy** of the app that strips all annotations, excludes evaluator-only files, and removes dependency noise. The original annotated source stays in the repository; only the temp copy goes to the scanner.

### Two Modes

| Mode | Purpose | Annotations | Used by |
|------|---------|-------------|---------|
| **Authoring** | Development & maintenance | Present (required by AGENTS.md) | Humans, CI verification |
| **Scanning** | Benchmark evaluation | Stripped | AI scanning agents |

---

## What Gets Sanitized

### Source Code Annotations

Every AGENTS.md-mandated annotation must be removed from source files. The keywords are identical across all languages:

| Keyword | Appears in |
|---------|-----------|
| `VULNERABILITY` | All languages (standalone vuln marking) |
| `CHAIN LINK` | All languages (chain step marking) |
| `DECOY` | All languages (decoy safe-pattern marking) |

### Comment Syntax by Language

| Language | Line comments | Block comments | Docstring prose | Files to exclude |
|----------|--------------|----------------|-----------------|------------------|
| Python | `# VULN...` | — | `VULN...` (inside `"""..."""`) | `tests/*`, `docs/tech/*.md` |
| Java | `// VULN...` | `/* VULN... */` | — | `tests/*`, `docs/tech/*.md` |
| TypeScript | `// VULN...` | `/* VULN... */`, `{/* VULN... */}` | — | `tests/*`, `docs/tech/*.md` |
| JavaScript | `// VULN...` | `/* VULN... */` | — | `tests/*`, `docs/tech/*.md` |

### Test Files

Test files commonly contain assertions like:

```python
self.assertIn("VULNERABILITY A01", source)
self.assertIn("CHAIN LINK 1 (chain-01)", source)
```

These are **string literals**, not comments — a naive comment-stripping regex will not touch them. Test files must be **excluded entirely** from the scan copy.

### Evaluator-Only Files

These files contain ground truth data, attack narratives, or vulnerability tables. They must not appear in the scan workspace:

| File | Contents |
|------|----------|
| `.vulns` | Machine-readable vulnerability manifest (OWASP IDs, locations, CWE) |
| `scenarios.md` | Chained attack narratives with OWASP references |
| `docs/tech/architecture.md` | Architecture doc that may reference specific vulns |

### Dependency & Build Artifacts

These directories are pure noise and must be excluded:

| Directory | Source |
|-----------|--------|
| `.venv/` | Python virtual environment |
| `node_modules/` | npm dependencies |
| `dist/` | Build output |
| `exports/` | Generated report files |
| `build/` | Java build output |
| `target/` | Java build output |

---

## The `.vulns` Sanitization Key

The machine-readable vulnerability manifest (`.vulns`) drives the sanitization process. Each app defines its cleanup rules in an optional top-level `sanitization` key:

```json
{
  "app_id": "app-01",
  "vulnerabilities": [ ... ],
  "chained_attacks": [ ... ],
  "decoys": [ ... ],
  "sanitization": {
    "exclude_files": [
      "tests/test_modular_contract.py",
      "docs/tech/architecture.md"
    ],
    "exclude_dirs": [
      ".venv",
      "node_modules",
      "dist",
      "exports"
    ],
    "strip_patterns": [
      {
        "regex": "(?m)^\\s*#\\s*(VULNERABILITY|CHAIN LINK|DECOY)\\b.*$",
        "replace": "",
        "description": "Strip Python line-comment annotations"
      },
      {
        "regex": "(?m)^\\s+(VULNERABILITY|CHAIN LINK|DECOY)\\b.*$",
        "replace": "",
        "description": "Strip docstring prose annotations (no # prefix)"
      },
      {
        "regex": "(?m)^\\s*//\\s*(VULNERABILITY|CHAIN LINK|DECOY)\\b.*$",
        "replace": "",
        "description": "Strip TypeScript/Java/JS line-comment annotations"
      },
      {
        "regex": "\\{\\s*/\\*\\s*.*?(VULNERABILITY|CHAIN LINK|DECOY).*?\\*/\\s*\\}",
        "replace": "",
        "description": "Strip JSX block-comment annotations"
      }
    ]
  }
}
```

### Schema

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `exclude_files` | `string[]` | No | Glob patterns for files to remove from scan copy |
| `exclude_dirs` | `string[]` | No | Directory names to skip entirely during copy |
| `strip_patterns` | `object[]` | No | Array of regex replace rules applied to source files |

Each `strip_patterns` entry:

| Key | Type | Description |
|-----|------|-------------|
| `regex` | `string` | Perl-compatible regex (with `(?m)` multiline flag for line-level patterns) |
| `replace` | `string` | Replacement text (usually empty string) |
| `description` | `string` | Human-readable explanation of what this pattern does |

---

## Reference Implementation

A production-ready sanitizer is available at `tools/sanitize_app.py`. It reads `.vulns["sanitization"]` for app-specific rules, applies hard-coded defaults, and supports:
- Python tokenize-based comment and docstring stripping
- Regex-based stripping for Java, TypeScript/JSX, JavaScript, XML, and HTML
- Two-level verifier (hard-fail + suspicious token detection)
- JSON report output for audit trails

### Usage

```bash
# Sanitize a single app
python tools/sanitize_app.py apps/python/app-01-ecommerce-catalog /tmp/scan-workspace

# Generate a JSON report
python tools/sanitize_app.py apps/java/app-06-hr-management /tmp/scan-workspace --report /tmp/report.json

# Exit 2 if suspicious tokens remain (not just hard-fail)
python tools/sanitize_app.py apps/typescript/app-11-social-analytics /tmp/scan-workspace --strict

# Sanitize all 50 apps
python tools/run_all.py
```

The script exits with:
- `0` — passed (no hard fails)
- `1` — hard fail (annotation keywords remain in scan copy)
- `2` — suspicious tokens found (only with `--strict`)

### Validation Results

The sanitizer was validated against all 50 apps:

```
Language    Apps  Passed  Failed
--------    ----  ------  ------
Python        14      14       0
Java          11      11       0
TypeScript    10      10       0
JavaScript    15      15       0
--------    ----  ------  ------
TOTAL         50      50       0
```

---

## Verification / Acceptance Checklist

Before launching a benchmark run, confirm:

```
[ ] All .vulns, scenarios.md, architecture.md, test/policy files are excluded
[ ] .venv/, node_modules/, dist/, exports/, build/, target/ are excluded
[ ] grep -rn 'VULNERABILITY\|CHAIN LINK\|DECOY' <scan_dir>/src returns zero hits
[ ] Tests/ directory is absent from scan copy, or grep returns zero hits if retained
[ ] App still starts and all endpoints respond (no regex accidentally broke code)
```

---

## Integration into Scan Pipeline

A typical pre-scan workflow:

```
1. For each app (app-01 through app-50):
   a. Read apps/<lang>/app-NN-<name>/.vulns
   b. Call sanitize_app() → produces clean copy in temp workspace
   c. Start app container from clean copy
   d. Run scanning agent against running container
   e. Compare agent findings against .vulns ground truth
   f. Score recall, precision, coverage, localization
2. Aggregate scores across all 50 apps
```

The sanitizer is the **first step** in the pipeline. It ensures the scanner sees realistic source code without embedded answer keys.
