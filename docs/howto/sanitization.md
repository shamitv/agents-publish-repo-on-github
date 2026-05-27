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

## Reference: Python Sanitizer Implementation

The following function reads `.vulns`, copies the app to a temp directory, applies all sanitization rules, and returns the path to the clean workspace.

```python
#!/usr/bin/env python3
"""sanitize.py — Produce a scan-ready copy of a benchmark app.

Usage:
    python sanitize.py /path/to/app /path/to/work_dir

Reads .vulns from the app root, applies exclude rules and strip patterns,
and writes a sanitized copy to <work_dir>/<app_name>.
"""

import json
import re
import shutil
import sys
from pathlib import Path


# Keywords that mark AGENTS.md-mandated annotations.
# These appear in comments, docstrings, and test assertions across all languages.
_HINT_KEYWORDS = r"(VULNERABILITY|CHAIN LINK|DECOY)"

# Directories always excluded from scan copies, regardless of .vulns config.
_HARDCODED_EXCLUDE_DIRS = {".venv", "node_modules", "dist", "exports", "build", "target"}

# Files always excluded from scan copies, regardless of .vulns config.
_HARDCODED_EXCLUDE_FILES = {
    ".vulns", "scenarios.md", "README.md", "docs/tech/architecture.md",
    "tests", "src/test", "__tests__",
}


def _build_annotation_regexes() -> list[tuple[re.Pattern, str]]:
    """Return language-agnostic regex patterns that cover all comment styles.

    These serve as a fallback when .vulns has no strip_patterns defined.
    """
    return [
        # Python inline + full-line # comments (no leading anchor — catches
        # both "import pickle  # VULN A08: ..." and "# VULN A01: ...")
        (re.compile(rf"(?m)#\s*{_HINT_KEYWORDS}\b.*$"), ""),
        # Python docstring prose (no # prefix)
        (re.compile(rf"(?m)^\s+{_HINT_KEYWORDS}\b.*$"), ""),
        # Java / TS / JS inline + full-line // comments
        (re.compile(rf"(?m)//\s*{_HINT_KEYWORDS}\b.*$"), ""),
        # Single-line JSX block comments: {/* VULN ... */}
        (re.compile(rf"\{{/\*\s*{_HINT_KEYWORDS}[^*/]*\*/\}}"), ""),
        # Multi-line JSX block comments: handle as single contiguous match
        (re.compile(rf"{{/\*[\s\S]*?{_HINT_KEYWORDS}[\s\S]*?\*/}}"), ""),
        # Java / JS block comments on one line
        (re.compile(rf"/\*\s*{_HINT_KEYWORDS}[^*]*\*/"), ""),
        # Single-line XML / HTML comments: <!-- VULN A06: ... -->
        (re.compile(rf"(?m)<!--\s*{_HINT_KEYWORDS}.*?-->"), ""),
        # Multi-line XML / HTML comments spanning lines
        (re.compile(rf"<!--[\s\S]*?{_HINT_KEYWORDS}[\s\S]*?-->"), ""),
    ]


def _load_sanitization_rules(vulns_path: Path) -> dict:
    """Load the sanitization section from an app's .vulns manifest."""
    if not vulns_path.exists():
        return {}
    data = json.loads(vulns_path.read_text(encoding="utf-8"))
    return data.get("sanitization", {})


def _apply_line_patterns(content: str, patterns: list[tuple[re.Pattern, str]]) -> str:
    """Apply (regex, replacement) pairs to file content."""
    for pattern, replacement in patterns:
        content = pattern.sub(replacement, content)
    return content


def sanitize_app(app_root: Path, work_dir: Path) -> Path:
    """Produce a scan-ready copy of an app.

    Args:
        app_root: Absolute path to the app directory (e.g., .../app-01-ecommerce-catalog).
        work_dir: Absolute path to a temporary working directory.

    Returns:
        Absolute path to the sanitized copy.

    Raises:
        FileNotFoundError: If app_root does not exist.
    """
    if not app_root.is_dir():
        raise FileNotFoundError(f"App directory not found: {app_root}")

    vulns_path = app_root / ".vulns"
    rules = _load_sanitization_rules(vulns_path)

    # ---- Step 1: Determine output path ----
    dst = work_dir / app_root.name

    # ---- Step 2: Copy app, excluding hard-coded + app-specific directories ----
    exclude_dirs = sorted(_HARDCODED_EXCLUDE_DIRS | set(rules.get("exclude_dirs", [])))
    shutil.copytree(
        app_root,
        dst,
        symlinks=False,
        ignore=shutil.ignore_patterns(*exclude_dirs),
        dirs_exist_ok=True,
    )

    # ---- Step 3: Remove hard-coded + app-specific excluded files ----
    exclude_files = sorted(_HARDCODED_EXCLUDE_FILES | set(rules.get("exclude_files", [])))
    for pattern in exclude_files:
        for matched_path in dst.glob(pattern):
            if matched_path.is_file():
                matched_path.unlink()
            elif matched_path.is_dir():
                shutil.rmtree(matched_path)

    # ---- Step 4: Build regex patterns ----
    # Always start with built-in defaults; extend (never replace) with .vulns patterns.
    patterns = _build_annotation_regexes()
    for entry in rules.get("strip_patterns", []):
        patterns.append((re.compile(entry["regex"]), entry.get("replace", "")))

    # ---- Step 5: Apply patterns to all source files ----
    source_extensions = {".py", ".java", ".ts", ".tsx", ".js", ".jsx", ".xml", ".html"}
    for src_file in dst.rglob("*"):
        if src_file.suffix in source_extensions:
            try:
                original = src_file.read_text(encoding="utf-8")
                cleaned = _apply_line_patterns(original, patterns)
                if cleaned != original:
                    src_file.write_text(cleaned, encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue  # skip binary files or unreadable files

    return dst


def verify_clean(app_root: Path) -> int:
    """Check for remaining hint contamination in the scan copy.

    Checks:
      1. Source files for annotation keywords (VULNERABILITY, CHAIN LINK, DECOY).
      2. Hard-coded excluded basenames are not present in the scan copy.
      3. Remaining Markdown/docs for hint keywords or OWASP references.

    Returns:
        Number of contaminated files found. Zero = clean.
    """
    hint_re = re.compile(rf"{_HINT_KEYWORDS}")
    owasp_re = re.compile(r"OWASP|CWE-\d{3}")
    contaminated = []

    # Check 1: Source files for annotation keywords
    for src_file in app_root.rglob("*"):
        if src_file.suffix in {".py", ".java", ".ts", ".tsx", ".js", ".jsx", ".xml", ".html"}:
            try:
                content = src_file.read_text(encoding="utf-8")
                if hint_re.search(content):
                    contaminated.append(src_file)
            except (UnicodeDecodeError, PermissionError):
                continue

    # Check 2: Hard-coded excluded basenames must not be present
    for basename in _HARDCODED_EXCLUDE_FILES:
        for f in app_root.rglob(basename):
            contaminated.append(f)

    # Check 3: Remaining Markdown/docs files must not contain hint terms
    for md_file in app_root.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            if hint_re.search(content) or owasp_re.search(content):
                contaminated.append(md_file)
        except (UnicodeDecodeError, PermissionError):
            continue

    if contaminated:
        distinct = sorted(set(contaminated), key=str)
        print(f"WARNING: {len(distinct)} file(s) still contain contamination:")
        for f in distinct:
            print(f"  {f.relative_to(app_root)}")
    else:
        print("OK: No contamination found in scan copy.")

    return len(contaminated)


# ---- CLI Entry Point ----

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <app_root> <work_dir>")
        sys.exit(1)

    app_root = Path(sys.argv[1]).resolve()
    work_dir = Path(sys.argv[2]).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"Sanitizing {app_root}...")
    clean_path = sanitize_app(app_root, work_dir)
    print(f"Wrote sanitized copy to {clean_path}")

    exit_code = verify_clean(clean_path)
    sys.exit(exit_code)
```

### Usage

```bash
# Sanitize a single app
python sanitize.py apps/python/app-01-ecommerce-catalog /tmp/scan-workspace

# Sanitize all 50 apps
for app in apps/*/*/; do
  python sanitize.py "$app" /tmp/scan-workspace
done
```

The script exits with code 0 if every source file in the sanitized copy is clean, and 1 if any annotation keyword remains.

---

## Verification / Acceptance Checklist

Before launching a benchmark run, confirm:

```
[ ] All .vulns, scenarios.md, architecture.md, test/policy files are excluded
[ ] .venv/, node_modules/, dist/, exports/, build/, target/ are excluded
[ ] grep -rn 'VULNERABILITY\|CHAIN LINK\|DECOY' <scan_dir>/src returns zero hits
[ ] grep -rn 'VULNERABILITY\|CHAIN LINK\|DECOY' <scan_dir>/tests returns zero hits
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
