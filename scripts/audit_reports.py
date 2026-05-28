"""
Audit script: Compare reports/*.md against apps/*/.vulns manifests.

For each app, check:
1. Does the report cover all standalone vulnerabilities from .vulns?
2. Does the report cover all chained attack scenarios from .vulns?
3. Are the OWASP IDs, severities, and methods correctly referenced?
"""

import json
import os
import re
import glob
import sys

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


REPO_ROOT = r"d:\work\secure-code-hunt"
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")
APPS_DIR = os.path.join(REPO_ROOT, "apps")

# Map app IDs to their language directories
LANG_DIRS = {
    "python": os.path.join(APPS_DIR, "python"),
    "java": os.path.join(APPS_DIR, "java"),
    "typescript": os.path.join(APPS_DIR, "typescript"),
    "javascript": os.path.join(APPS_DIR, "javascript"),
}

def find_vulns_file(app_id):
    """Find the .vulns file for a given app ID (e.g., 'app-01')."""
    for lang, lang_dir in LANG_DIRS.items():
        if not os.path.isdir(lang_dir):
            continue
        for entry in os.listdir(lang_dir):
            if entry.startswith(app_id + "-"):
                vulns_path = os.path.join(lang_dir, entry, ".vulns")
                if os.path.isfile(vulns_path):
                    return vulns_path
    return None

def parse_vulns(vulns_path):
    """Parse .vulns JSON file and extract structured data."""
    with open(vulns_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def parse_report(report_path):
    """Parse a report markdown and extract mentioned OWASP IDs, chains, methods."""
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {
        "owasp_ids_standalone": [],
        "chain_ids": [],
        "methods_mentioned": [],
        "raw_content": content,
    }
    
    # Extract standalone vuln OWASP IDs - handle BOTH formats:
    # Old format: "### VULN-01: A03 —"
    # New format: "| V1 | A03 | Category | Severity | Location | CWE |"
    vuln_pattern_old = re.findall(r'###\s+VULN-\d+:\s+(A\d{2})\s+', content)
    
    # New format: extract from summary table rows like "| V1 | A03 |"
    vuln_pattern_new = re.findall(r'\|\s*V\d+\s*\|\s*(A\d{2})\s*\|', content)
    
    # Also try: "**OWASP Category**: A01" in V-style sections
    vuln_pattern_section = re.findall(r'\*\*OWASP Category\*\*:\s*(A\d{2})', content)
    
    # Combine all found IDs (deduplicate preserving order)
    all_owasp = vuln_pattern_old + vuln_pattern_new + vuln_pattern_section
    seen = set()
    deduped = []
    for a in all_owasp:
        if a not in seen:
            seen.add(a)
            deduped.append(a)
    result["owasp_ids_standalone"] = deduped
    
    # Extract chain IDs (e.g., "## Chained Attack: chain-01" or "chain-01" anywhere)
    chain_pattern = re.findall(r'chain-(\d+)', content, re.IGNORECASE)
    result["chain_ids"] = list(set(["chain-" + c for c in chain_pattern]))
    
    # Extract chain link OWASP IDs - handle BOTH formats:
    # Old: "### Link 1: ... (A01 —"
    link_pattern_old = re.findall(r'###\s+Link\s+\d+:.*?\((A\d{2})\s', content)
    
    # New: chain component table rows "| 1 | description | Medium | A03 | CWE-89 |"
    link_pattern_new = re.findall(r'\|\s*\d+\s*\|[^|]+\|\s*\w+\s*\|\s*(A\d{2})\s*\|', content)
    
    result["chain_link_owasp"] = list(set(link_pattern_old + link_pattern_new))
    
    # Extract methods mentioned
    method_pattern = re.findall(r'`([a-zA-Z_]+(?:\(\))?)`', content)
    result["methods_mentioned"] = method_pattern
    
    # Extract endpoint methods mentioned (e.g., GET /api/expenses/:id)
    endpoint_pattern = re.findall(r'`((?:GET|POST|PUT|DELETE|PATCH)\s+/[^`]+)`', content)
    result["endpoints_mentioned"] = endpoint_pattern
    
    return result


def audit_app(app_id, vulns_path, report_path):
    """Compare .vulns manifest with report for a single app."""
    issues = []
    
    vulns_data = parse_vulns(vulns_path)
    report_data = parse_report(report_path)
    
    # 1. Check standalone vulnerabilities coverage
    vulns_list = vulns_data.get("vulnerabilities", [])
    report_owasp = report_data["owasp_ids_standalone"]
    
    for vuln in vulns_list:
        owasp_id = vuln["owasp_id"]
        method = vuln.get("method", "")
        if owasp_id not in report_owasp:
            issues.append(f"  MISSING STANDALONE VULN: {owasp_id} ({vuln['category']}) in method '{method}' — not found in report")
    
    # Check for extra vulns in report not in .vulns
    vulns_owasp_ids = [v["owasp_id"] for v in vulns_list]
    for rid in report_owasp:
        if rid not in vulns_owasp_ids:
            issues.append(f"  EXTRA VULN IN REPORT: {rid} listed in report but not in .vulns standalone vulnerabilities")
    
    # 2. Check chained attacks coverage
    chains = vulns_data.get("chained_attacks", [])
    report_chain_ids = report_data["chain_ids"]
    
    for chain in chains:
        chain_id = chain["chain_id"]
        if chain_id not in report_chain_ids:
            issues.append(f"  MISSING CHAIN: {chain_id} ('{chain.get('chain_name', '')}') — not covered in report")
        else:
            # Check chain components
            components = chain.get("components", [])
            for comp in components:
                comp_owasp = comp["owasp_id"]
                comp_method = comp.get("method", "")
                # Check if the chain link's OWASP ID is mentioned in the report's chain section
                if comp_owasp not in report_data.get("chain_link_owasp", []):
                    issues.append(f"  MISSING CHAIN LINK: {chain_id} step {comp['step']} ({comp_owasp}) method '{comp_method}' — OWASP ID not found in report chain links")
    
    # Check for extra chains in report
    vulns_chain_ids = [c["chain_id"] for c in chains]
    for rc in report_chain_ids:
        if rc not in vulns_chain_ids:
            issues.append(f"  EXTRA CHAIN IN REPORT: {rc} mentioned in report but not in .vulns")
    
    # 3. Check severity correctness for standalone vulns
    for idx, vuln in enumerate(vulns_list, 1):
        owasp_id = vuln["owasp_id"]
        severity = vuln["severity"]
        # Try old format: "VULN-01: A03 ... \n**Severity:** High"
        severity_pattern = re.findall(
            rf'VULN-{idx:02d}:\s+{owasp_id}\s+.*?\n.*?\*\*Severity:\*\*\s+(\w+)',
            report_data["raw_content"]
        )
        if not severity_pattern:
            severity_pattern = re.findall(
                rf'VULN-{idx}:\s+{owasp_id}\s+.*?\n.*?\*\*Severity:\*\*\s+(\w+)',
                report_data["raw_content"]
            )
        # Try new format: "| V1 | A03 | Category | Severity | Location |"
        if not severity_pattern:
            severity_pattern = re.findall(
                rf'\|\s*V{idx}\s*\|\s*{owasp_id}\s*\|[^|]+\|\s*(\w+)\s*\|',
                report_data["raw_content"]
            )
        if severity_pattern:
            report_sev = severity_pattern[0].lower()
            if report_sev != severity.lower():
                issues.append(f"  SEVERITY MISMATCH: {owasp_id} (V{idx}) -- .vulns says '{severity}', report says '{report_sev}'")
    
    # 4. Check method/endpoint correctness
    # For each vulnerability in .vulns, check if the report references the same method/endpoint
    for vuln in vulns_list:
        owasp_id = vuln["owasp_id"]
        method = vuln.get("method", "")
        if owasp_id in report_owasp and method:
            # Check if the method/endpoint is mentioned anywhere in the report
            if method not in report_data["raw_content"]:
                # Check for partial matches (e.g., function name only)
                func_name = method.split('/')[-1] if '/' in method else method
                if func_name and func_name not in report_data["raw_content"]:
                    issues.append(f"  METHOD MISMATCH: {owasp_id} -- .vulns references '{method}' but report does not mention this endpoint/method")
    
    return issues


def main():
    report_files = sorted(glob.glob(os.path.join(REPORTS_DIR, "app-*.md")))
    
    total_issues = 0
    apps_with_issues = 0
    apps_ok = 0
    missing_vulns_count = 0
    missing_reports = []
    
    all_results = []
    
    for report_path in report_files:
        basename = os.path.basename(report_path).replace(".md", "")
        # Extract app ID like "app-01" from "app-01-ecommerce-catalog"
        match = re.match(r'(app-\d+)', basename)
        if not match:
            continue
        app_id = match.group(1)
        
        vulns_path = find_vulns_file(app_id)
        if not vulns_path:
            missing_vulns_count += 1
            all_results.append((app_id, basename, ["  NO .vulns FILE FOUND"]))
            continue
        
        issues = audit_app(app_id, vulns_path, report_path)
        all_results.append((app_id, basename, issues))
        
        if issues:
            apps_with_issues += 1
            total_issues += len(issues)
        else:
            apps_ok += 1
    
    # Print results
    print("=" * 80)
    print("AUDIT REPORT: reports/ vs .vulns manifests")
    print("=" * 80)
    print()
    
    # Print apps with issues first
    for app_id, basename, issues in all_results:
        if issues:
            print(f"[FAIL] {app_id} ({basename})")
            for issue in issues:
                print(issue)
            print()
    
    # Then print clean apps
    print("-" * 40)
    print("CLEAN APPS (no issues found):")
    for app_id, basename, issues in all_results:
        if not issues:
            print(f"  [OK] {app_id} ({basename})")
    
    print()
    print("=" * 80)
    print(f"SUMMARY: {len(all_results)} apps audited")
    print(f"  [OK] {apps_ok} apps OK")
    print(f"  [FAIL] {apps_with_issues} apps with issues ({total_issues} total issues)")
    if missing_vulns_count:
        print(f"  [WARN] {missing_vulns_count} apps missing .vulns files")
    print("=" * 80)

if __name__ == "__main__":
    main()
