#!/usr/bin/env python3
"""sanitize_app.py — Produce a scan-ready copy of a benchmark app.

Usage:
    python tools/sanitize_app.py APP_ROOT WORK_DIR [--strict] [--report REPORT_PATH]

Reads .vulns from the app root, applies hard-coded and app-specific
sanitization rules, and writes a sanitized copy to WORK_DIR/<app_name>.
"""

import json
import re
import shutil
import sys
import tokenize
import io
from pathlib import Path


# ── Constants ──────────────────────────────────────────────────────────

# Keywords that always trigger a hard-fail.
_HARD_KEYWORDS = r"(VULNERABILITY|CHAIN LINK|DECOY|OWASP|CWE[-\s]\d{3,4})"

# Keywords that trigger a suspicious flag (only in comments/docstrings).
_SUSPICIOUS_KEYWORDS = (
    r"(?i)(decoy|safe pattern|actual injection|actual vulnerability|"
    r"never (actually )?(applied|called)|allowlist bypass|cloud metadata|"
    r"localhost[/\s]private IP|stored XSS|SSRF vector|SSRF surface|"
    r"ground truth|no touch|not (actually )?(applied|called|used))"
)

# Directories always excluded.
_HARDCODED_EXCLUDE_DIRS = {
    ".venv", "node_modules", "dist", "exports", "build", "target",
    "__pycache__", ".mypy_cache", ".pytest_cache",
}

# Files/patterns always excluded.
_HARDCODED_EXCLUDE_FILES = {
    ".vulns", "scenarios.md", "README.md", "docs/tech/architecture.md",
    "tests", "src/test", "__tests__",
}

# Source file extensions that get regex-based stripping.
_SOURCE_EXTENSIONS = {".py", ".java", ".ts", ".tsx", ".js", ".jsx", ".xml", ".html"}


# ── Regex Builders ─────────────────────────────────────────────────────

def _build_hint_re() -> re.Pattern:
    return re.compile(r"(VULNERABILITY|CHAIN LINK|[Dd][Ee][Cc][Oo][Yy]|OWASP|CWE[-\s]\d{3,4})")


def _build_suspicious_re() -> re.Pattern:
    return re.compile(_SUSPICIOUS_KEYWORDS)


def _build_annotation_regexes() -> list[tuple[re.Pattern, str]]:
    """Return built-in regex patterns covering all languages."""
    H = r"(VULNERABILITY|CHAIN LINK|[Dd][Ee][Cc][Oo][Yy])"
    return [
        # Python # comments (keyword anywhere after #)
        (re.compile(rf"(?m)#.*?{H}\b.*$"), ""),
        # Python docstring prose (no # prefix, starts with keyword)
        (re.compile(rf"(?m)^\s+{H}\b.*$"), ""),
        # Java / TS / JS // comments (keyword anywhere after //)
        (re.compile(rf"(?m)//.*?{H}\b.*$"), ""),
        # Single-line JSX block comments: {/* VULN ... */}
        (re.compile(rf"\{{/\*\s*{H}[^*/]*\*/\}}"), ""),
        # Multi-line JSX block comments
        (re.compile(rf"{{/\*[\s\S]*?{H}[\s\S]*?\*/}}"), ""),
        # Java / JS block comments on one line
        (re.compile(rf"/\*\s*{H}[^*]*\*/"), ""),
        # Single-line XML / HTML comments
        (re.compile(rf"(?m)<!--\s*{H}.*?-->"), ""),
        # Multi-line XML / HTML comments
        (re.compile(rf"<!--[\s\S]*?{H}[\s\S]*?-->"), ""),
    ]


# ── Python Token-Aware Stripping ──────────────────────────────────────

def _strip_python_source(source: str) -> tuple[str, list[dict]]:
    """Strip hint comments and docstrings from Python source.

    Uses regex for multi-line docstrings (handles both types),
    then tokenize for accurate #-comment stripping.

    Returns (cleaned_source, changes_list).
    """
    changes = []
    hint_re = _build_hint_re()

    # ── Step 1: Replace multi-line docstrings containing hints ──────────
    def _replace_docstring(m: re.Match) -> str:
        content = m.group(0)
        if hint_re.search(content) or _build_suspicious_re().search(content):
            changes.append({"type": "docstring", "content": content[:80]})
            sq = chr(39) * 3
            if content.startswith(sq):
                return sq + "..." + sq
            dq = chr(34) * 3
            return dq + "..." + dq
        return content

    TQ = re.escape(chr(34) * 3)  # triple double quote
    source = re.sub(TQ + ".*?" + TQ, _replace_docstring, source, flags=re.DOTALL)
    TQS = re.escape(chr(39) * 3)  # triple single quote
    source = re.sub(TQS + ".*?" + TQS, _replace_docstring, source, flags=re.DOTALL)

    # ── Step 2: Strip #-comment line-hint via tokenize ─────────────────
    try:
        result_lines = list(source.splitlines(keepends=True))
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    except (tokenize.TokenError, IndentationError):
        return _apply_regex_patterns(source, _build_annotation_regexes()), changes

    for tok in tokens:
        if tok.type != tokenize.COMMENT:
            continue
        if not hint_re.search(tok.string):
            continue
        idx = tok.start[0] - 1
        if idx >= len(result_lines):
            continue
        line = result_lines[idx]
        pos = line.find("#")
        if pos >= 0:
            result_lines[idx] = line[:pos].rstrip() + "\n"
            changes.append({"type": "comment", "content": tok.string.strip()})

    source = "".join(result_lines)

    # ── Step 3: Strip multi-line comment continuations ─────────────────
    # After step 2 removed keyword-prefixed comment lines, continuation
    # lines still survive. Strip any remaining #-line that contains a
    # suspicious keyword (and is within 3 lines of a stripped comment).
    susp_re = _build_suspicious_re()
    lines = source.splitlines(keepends=True)
    for i in range(len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("#") and susp_re.search(stripped):
            lines[i] = "\n"
    source = "".join(lines)

    # ── Step 4: Strip docstring prose lines that survived ──────────────
    # Pattern: whitespace + keyword at line start (inside remaining docstrings)
    prose_re = re.compile(rf"(?m)^\s+(VULNERABILITY|CHAIN LINK|[Dd][Ee][Cc][Oo][Yy])\b.*$")
    source = prose_re.sub("", source)

    return source, changes


def _apply_regex_patterns(content: str, patterns: list[tuple[re.Pattern, str]]) -> str:
    """Apply (regex, replacement) pairs to file content."""
    for pattern, replacement in patterns:
        content = pattern.sub(replacement, content)
    return content


# ── Load Rules ─────────────────────────────────────────────────────────

def _load_sanitization_rules(vulns_path: Path) -> dict:
    if not vulns_path.exists():
        return {}
    data = json.loads(vulns_path.read_text(encoding="utf-8"))
    return data.get("sanitization", {})


# ── Sanitize ───────────────────────────────────────────────────────────

def sanitize_app(app_root: Path, work_dir: Path) -> tuple[Path, list[dict]]:
    """Produce a scan-ready copy of an app.

    Returns (path_to_clean_copy, changes_list).
    """
    if not app_root.is_dir():
        raise FileNotFoundError(f"App directory not found: {app_root}")

    vulns_path = app_root / ".vulns"
    rules = _load_sanitization_rules(vulns_path)
    changes = []

    dst = work_dir / app_root.name

    # Step 2: Copy app, excluding directories
    exclude_dirs = sorted(_HARDCODED_EXCLUDE_DIRS | set(rules.get("exclude_dirs", [])))
    shutil.copytree(
        app_root,
        dst,
        symlinks=False,
        ignore=shutil.ignore_patterns(*exclude_dirs),
        dirs_exist_ok=True,
    )

    # Step 3: Remove excluded files
    exclude_file_patterns = sorted(_HARDCODED_EXCLUDE_FILES | set(rules.get("exclude_files", [])))
    for pattern in exclude_file_patterns:
        for matched_path in dst.glob(pattern):
            if matched_path.is_file():
                changes.append({"action": "removed", "file": str(matched_path.relative_to(dst))})
                matched_path.unlink()
            elif matched_path.is_dir():
                for f in matched_path.rglob("*"):
                    if f.is_file():
                        changes.append({"action": "removed", "file": str(f.relative_to(dst))})
                shutil.rmtree(matched_path)

    # Also remove any file/pattern matching test-like names
    for f in dst.rglob("*"):
        if f.is_file() and not f.suffix:
            continue
        fname = f.name
        if any(p in fname for p in ("_test.", "test_.", "tests.", "_spec.", "spec.")):
            try:
                f.unlink()
                changes.append({"action": "removed", "file": str(f.relative_to(dst))})
            except OSError:
                pass

    # Step 4: Build regex patterns (defaults + app-specific)
    annotation_patterns = _build_annotation_regexes()
    for entry in rules.get("strip_patterns", []):
        annotation_patterns.append((re.compile(entry["regex"]), entry.get("replace", "")))

    # Step 5: Apply stripping to source files
    for src_file in dst.rglob("*"):
        if src_file.suffix not in _SOURCE_EXTENSIONS:
            continue
        try:
            original = src_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        rel = str(src_file.relative_to(dst))

        if src_file.suffix == ".py":
            cleaned, file_changes = _strip_python_source(original)
            for c in file_changes:
                c["file"] = rel
                changes.append(c)
        else:
            cleaned = _apply_regex_patterns(original, annotation_patterns)
            # Detect changes via regex
            if cleaned != original:
                changes.append({"action": "stripped_regex", "file": rel})

        if cleaned != original:
            src_file.write_text(cleaned, encoding="utf-8")

    return dst, changes


# ── Verifier ───────────────────────────────────────────────────────────

def verify_clean(app_root: Path) -> tuple[list[dict], list[dict]]:
    """Verify a sanitized copy for contamination.

    Returns (hard_fails, suspicious_finds).
    """
    hint_re = _build_hint_re()
    susp_re = _build_suspicious_re()
    hard_fails = []
    suspicious = []

    # Check 1: Source files for hard keywords
    for src_file in app_root.rglob("*"):
        if src_file.suffix not in _SOURCE_EXTENSIONS:
            continue
        try:
            content = src_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        rel = str(src_file.relative_to(app_root))

        if hint_re.search(content):
            for m in hint_re.finditer(content):
                hard_fails.append({
                    "file": rel,
                    "match": m.group(),
                    "line": content[:m.start()].count("\n") + 1,
                })

        if susp_re.search(content):
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                if susp_re.search(line):
                    suspicious.append({
                        "file": rel,
                        "line": i,
                        "match": susp_re.search(line).group(),
                    })

    # Check 2: Hard-coded excluded basenames must not be present
    for basename in _HARDCODED_EXCLUDE_FILES:
        for f in app_root.rglob(basename):
            hard_fails.append({
                "file": str(f.relative_to(app_root)),
                "match": f"excluded file/dir still present: {basename}",
                "line": 0,
            })

    # Check 3: Remaining Markdown/docs for hint terms
    for md_file in app_root.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        rel = str(md_file.relative_to(app_root))
        if hint_re.search(content):
            hard_fails.append({
                "file": rel,
                "match": "hint keyword in Markdown",
                "line": 1,
            })
        if susp_re.search(content):
            suspicious.append({
                "file": rel,
                "match": "suspicious term in Markdown",
                "line": 1,
            })

    return hard_fails, suspicious


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Produce a scan-ready sanitized copy of a benchmark app."
    )
    parser.add_argument("app_root", type=str, help="Path to app directory (must contain .vulns)")
    parser.add_argument("work_dir", type=str, help="Output directory for sanitized copy")
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit 2 on suspicious tokens (not just hard-fail)"
    )
    parser.add_argument("--report", type=str, default=None, help="Write JSON report to path")

    args = parser.parse_args()

    app_root = Path(args.app_root).resolve()
    work_dir = Path(args.work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    if not (app_root / ".vulns").exists():
        print(f"ERROR: No .vulns found in {app_root}")
        sys.exit(1)

    print(f"Sanitizing {app_root}...")
    clean_path, changes = sanitize_app(app_root, work_dir)
    print(f"Wrote sanitized copy to {clean_path}")

    hard_fails, suspicious = verify_clean(clean_path)

    # Report
    report = {
        "app": app_root.name,
        "passed": len(hard_fails) == 0,
        "hard_fails": len(hard_fails),
        "suspicious": len(suspicious),
        "hard_fail_details": hard_fails[:50],
        "suspicious_details": suspicious[:50],
        "changes": changes,
    }

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report written to {report_path}")

    if hard_fails:
        print(f"\nHARD FAIL ({len(hard_fails)}):")
        for f in hard_fails[:10]:
            print(f"  {f['file']}:{f.get('line', '?')} — {f['match']}")
    if suspicious:
        print(f"\nSUSPICIOUS ({len(suspicious)}):")
        for f in suspicious[:10]:
            print(f"  {f['file']}:{f.get('line', '?')} — {f['match']}")

    if hard_fails:
        print(f"\nFAILED: {len(hard_fails)} hard-fail(s) remain")
        sys.exit(1)
    if suspicious and args.strict:
        print(f"\nFAILED (strict): {len(suspicious)} suspicious token(s) found")
        sys.exit(2)

    print("\nPASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
