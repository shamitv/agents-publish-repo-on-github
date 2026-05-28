#!/usr/bin/env python3
"""Run sanitize_app.py on all 50 apps and collect results."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

app_roots = sorted(p.parent for p in ROOT.rglob(".vulns")
                   if "node_modules" not in str(p))

print(f"Found {len(app_roots)} apps with .vulns")

work_dir = ROOT / "temp" / "scan-batch"
work_dir.mkdir(parents=True, exist_ok=True)

results = []
for i, app in enumerate(app_roots, 1):
    rel = app.relative_to(ROOT)
    print(f"  [{i}/{len(app_roots)}] {rel}...", end=" ", flush=True)
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "sanitize_app.py"),
             str(app), str(work_dir),
             "--report", str(app / "sanitize-report.json")],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            print("PASSED")
        else:
            # Extract summary line(s)
            lines = result.stdout.strip().split("\n")
            summary = [l for l in lines if l.strip() and not l.startswith("Sanitizing") and not l.startswith("Wrote") and not l.startswith("Report")]
            print(f"FAILED ({result.returncode}): {summary[-1] if summary else 'unknown'}"[:100])
        results.append({"app": rel, "exit": result.returncode})
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        results.append({"app": rel, "exit": -1})

passed = sum(1 for r in results if r["exit"] == 0)
failed = [r for r in results if r["exit"] != 0]
print(f"\n=== RESULTS: {passed}/{len(results)} passed, {len(failed)} failed ===")
for r in failed:
    print(f"  FAILED: {r['app']} (exit {r['exit']})")
