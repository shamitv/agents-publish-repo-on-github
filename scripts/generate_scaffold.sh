#!/usr/bin/env bash
set -e
# Iterate over each app directory (2 levels deep under apps)
while IFS= read -r -d '' dir; do
  app=$(basename "$dir")
  lang=$(basename "$(dirname "$dir")")
  cat > "$dir/README.md" <<'EOF'
# $app

**Language:** $lang

**Purpose:** Placeholder description for $app. This is a full‑stack sample application used to demonstrate common OWASP Top 10 vulnerabilities such as CORS misconfiguration, broken access control, injection, etc.

## How to Run

\`\`\`sh
# Install dependencies (example)
# Adjust commands per language/framework
\`\`\`

## Vulnerabilities

The ground‑truth list of planted vulnerabilities is defined in `vulnerabilities.json`.

---

*This file is auto‑generated for scaffold purposes.*
EOF

  cat > "$dir/impl_plan.md" <<'EOF'
# Implementation Plan for $app

- Set up project scaffolding for the appropriate language/framework.
- Implement core business functionality (e.g., CRUD endpoints, UI pages).
- Intentionally inject 2‑4 OWASP Top 10 issues (e.g., CORS misconfiguration, insecure deserialization, missing auth checks, etc.).
- Write unit tests for normal flow.
- Document each vulnerability in `vulnerabilities.json` with file path, line number, CWE, and severity.
- Provide a Dockerfile for containerized execution.

---

*Generated automatically; customize as needed.*
EOF
done < <(find /Users/shamit/work/owasp-test/apps -mindepth 2 -maxdepth 2 -type d -print0)
