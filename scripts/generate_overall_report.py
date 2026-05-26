import json
import os
import sys
from collections import Counter

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APPS_DIR = os.path.join(REPO_ROOT, "apps")
OUTPUT_PATH = os.path.join(REPO_ROOT, "reports", "overall.md")

LANG_DIRS = ["python", "java", "typescript", "javascript"]

# Predefined overall application difficulty map as established in scripts/chain_stats.py
DIFFICULTY_MAP = {
    'app-01': 'Hard', 'app-02': 'Medium', 'app-03': 'Medium', 'app-04': 'Medium', 'app-05': 'Hard',
    'app-06': 'Medium', 'app-07': 'Easy', 'app-08': 'Easy', 'app-09': 'Medium', 'app-10': 'Medium',
    'app-11': 'Medium', 'app-12': 'Medium', 'app-13': 'Medium', 'app-14': 'Medium', 'app-15': 'Medium',
    'app-16': 'Medium', 'app-17': 'Medium', 'app-18': 'Easy', 'app-19': 'Medium', 'app-20': 'Easy',
    'app-21': 'Medium', 'app-22': 'Easy', 'app-23': 'Medium', 'app-24': 'Medium', 'app-25': 'Medium',
    'app-26': 'Hard', 'app-27': 'Medium', 'app-28': 'Medium', 'app-29': 'Hard', 'app-30': 'Medium',
    'app-31': 'Medium', 'app-32': 'Medium', 'app-33': 'Medium', 'app-34': 'Medium', 'app-35': 'Medium',
    'app-36': 'Medium', 'app-37': 'Medium', 'app-38': 'Medium', 'app-39': 'Easy', 'app-40': 'Medium',
    'app-41': 'Medium', 'app-42': 'Medium', 'app-43': 'Medium', 'app-44': 'Easy', 'app-45': 'Medium',
    'app-46': 'Medium', 'app-47': 'Hard', 'app-48': 'Easy', 'app-49': 'Medium', 'app-50': 'Hard',
}

def main():
    total_apps = 0
    standalone_vulns_count = 0
    total_chains_count = 0
    
    # Standalone vuln aggregations
    vulns_by_owasp = Counter()
    vulns_by_cwe = Counter()
    vulns_by_severity = Counter()
    vulns_by_lang = Counter()
    
    # Chained attack aggregations
    chains_by_impact = Counter()
    chains_by_difficulty = Counter()
    
    # Group by App Difficulty Level
    apps_by_difficulty = {
        "Easy": [],
        "Medium": [],
        "Hard": [],
        "Unknown": []
    }
    
    # Store app details
    apps_data = []
    
    for lang in LANG_DIRS:
        lang_dir = os.path.join(APPS_DIR, lang)
        if not os.path.isdir(lang_dir):
            continue
        for entry in sorted(os.listdir(lang_dir)):
            if entry.startswith("app-"):
                vulns_path = os.path.join(lang_dir, entry, ".vulns")
                if os.path.isfile(vulns_path):
                    with open(vulns_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    app_id = data["app_id"]
                    app_name = data["app_name"]
                    framework = data.get("framework", "N/A")
                    
                    # App Difficulty
                    app_diff = DIFFICULTY_MAP.get(app_id, "Unknown")
                    
                    vulns = data.get("vulnerabilities", [])
                    chains = data.get("chained_attacks", [])
                    
                    app_info = {
                        "id": app_id,
                        "name": app_name,
                        "language": lang,
                        "framework": framework,
                        "difficulty": app_diff,
                        "vulns_count": len(vulns),
                        "chains_count": len(chains)
                    }
                    apps_data.append(app_info)
                    apps_by_difficulty[app_diff].append(app_info)
                    total_apps += 1
                    
                    # Aggregate standalone vulns
                    for v in vulns:
                        standalone_vulns_count += 1
                        vulns_by_owasp[v["owasp_id"]] += 1
                        vulns_by_cwe[v.get("cwe", "N/A")] += 1
                        vulns_by_severity[v["severity"].lower()] += 1
                        vulns_by_lang[lang] += 1
                        
                    # Aggregate chains
                    for c in chains:
                        total_chains_count += 1
                        chains_by_impact[c.get("impact", "N/A").lower()] += 1
                        chains_by_difficulty[c.get("difficulty", "N/A").capitalize()] += 1
                        
    # Sort OWASP categories
    sorted_owasp = sorted(vulns_by_owasp.items())
    # Sort CWEs by count descending
    sorted_cwe = sorted(vulns_by_cwe.items(), key=lambda x: x[1], reverse=True)
    # Sort Severities: Critical, High, Medium, Low
    sev_order = ["critical", "high", "medium", "low"]
    sorted_sev = [(sev, vulns_by_severity[sev]) for sev in sev_order if sev in vulns_by_severity]
    
    # Sort Chain Impact by count descending
    sorted_impact = sorted(chains_by_impact.items(), key=lambda x: x[1], reverse=True)
    # Sort Chain Difficulty: Hard, Medium, Easy
    chain_diff_order = ["Hard", "Medium", "Easy", "Unknown"]
    sorted_chain_diff = [(cd, chains_by_difficulty[cd]) for cd in chain_diff_order if cd in chains_by_difficulty]

    # Generate Markdown
    md = []
    md.append("# Overall Security Audit Metrics Report")
    md.append("")
    md.append("This report aggregates security metrics, vulnerability counts, attack chain scenarios, and difficulty distributions across the entire corpus of 50 vulnerable applications.")
    md.append("")
    
    # Executive Summary
    md.append("## Executive Summary")
    md.append("")
    md.append(f"- **Total Applications:** {total_apps}")
    md.append(f"- **Total Standalone Vulnerabilities:** {standalone_vulns_count}")
    md.append(f"- **Total Chained Attack Scenarios:** {total_chains_count}")
    md.append("")
    md.append("| Metric | Value |")
    md.append("|---|---|")
    md.append(f"| Total Apps | {total_apps} |")
    md.append(f"| Total Standalone Vulns | {standalone_vulns_count} |")
    md.append(f"| Total Chained Attack Scenarios | {total_chains_count} |")
    md.append(f"| Avg Vulns per App | {standalone_vulns_count / total_apps:.2f} |")
    md.append(f"| Avg Chains per App | {total_chains_count / total_apps:.2f} |")
    md.append("")
    
    # Standalone Vulnerabilities Section
    md.append("## Standalone Vulnerabilities Analysis")
    md.append("")
    
    # Group by OWASP Category
    md.append("### Distribution by OWASP Top 10 Category")
    md.append("| OWASP Category | Description | Count | % of Total |")
    md.append("|---|---|---|---|")
    owasp_descriptions = {
        "A01": "Broken Access Control",
        "A02": "Cryptographic Failures",
        "A03": "Injection",
        "A04": "Insecure Design",
        "A05": "Security Misconfiguration",
        "A06": "Vulnerable and Outdated Components",
        "A07": "Identification and Authentication Failures",
        "A08": "Software and Data Integrity Failures",
        "A09": "Security Logging and Monitoring Failures",
        "A10": "Server-Side Request Forgery (SSRF)"
    }
    for owasp_id, count in sorted_owasp:
        desc = owasp_descriptions.get(owasp_id, "Unknown Category")
        pct = (count / standalone_vulns_count) * 100
        md.append(f"| {owasp_id} | {desc} | {count} | {pct:.1f}% |")
    md.append("")
    
    # Group by Severity
    md.append("### Distribution by Severity")
    md.append("| Severity | Count | % of Total |")
    md.append("|---|---|---|")
    for sev, count in sorted_sev:
        pct = (count / standalone_vulns_count) * 100
        md.append(f"| {sev.capitalize()} | {count} | {pct:.1f}% |")
    md.append("")

    # Group by CWE
    md.append("### Top CWEs (Common Weakness Enumerations)")
    md.append("| CWE | Count | Description |")
    md.append("|---|---|---|")
    cwe_desc_map = {
        "CWE-89": "Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')",
        "CWE-639": "Authorization Bypass Through User-Controlled Key ('IDOR')",
        "CWE-22": "Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')",
        "CWE-79": "Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
        "CWE-94": "Improper Control of Generation of Code ('Code Injection' / 'eval')",
        "CWE-798": "Use of Hardcoded Credentials",
        "CWE-918": "Server-Side Request Forgery (SSRF)",
        "CWE-502": "Deserialization of Untrusted Data",
        "CWE-352": "Cross-Site Request Forgery (CSRF)",
        "CWE-204": "Response Message Containing Sensitive Information (User Enumeration)",
        "CWE-287": "Improper Authentication",
        "CWE-307": "Improper Restriction of Excessive Authentication Attempts",
        "CWE-327": "Use of a Broken or Risky Cryptographic Algorithm",
        "CWE-330": "Use of Insufficiently Random Values",
        "CWE-778": "Insufficient Logging",
        "CWE-295": "Improper Certificate Validation",
        "CWE-400": "Uncontrolled Resource Consumption ('Resource Exhaustion')",
        "CWE-611": "Improper Restriction of XML External Entity Reference ('XXE')",
        "CWE-862": "Missing Authorization",
        "CWE-863": "Incorrect Authorization",
        "CWE-916": "Use of Password Hash with Insufficient Complexity",
        "CWE-384": "Session Fixation",
        "CWE-215": "Information Exposure Through Debug Information",
    }
    for cwe, count in sorted_cwe[:15]:  # Show top 15 CWEs
        desc = cwe_desc_map.get(cwe, "Other Security Weakness")
        md.append(f"| {cwe} | {count} | {desc} |")
    md.append("")

    # Chained Attack Scenarios Section
    md.append("## Chained Attack Scenarios Analysis")
    md.append("")
    
    # Distribution by Impact
    md.append("### Distribution by Combined Impact")
    md.append("| Impact Category | Count | Description |")
    md.append("|---|---|---|")
    impact_desc_map = {
        "account_takeover": "Attacker gains control of a victim user account",
        "lateral_movement": "Attacker pivots from the compromised app to other internal systems",
        "db_exfiltration": "Attacker bulk-reads sensitive database records (PII, credentials, etc.)",
        "data_modification": "Attacker writes unauthorized changes to stored records"
    }
    for impact, count in sorted_impact:
        desc = impact_desc_map.get(impact, "Other Impact")
        md.append(f"| `{impact}` | {count} | {desc} |")
    md.append("")

    # Distribution by Chain Difficulty
    md.append("### Distribution by Chain Difficulty")
    md.append("| Chain Difficulty | Count |")
    md.append("|---|---|")
    for cd, count in sorted_chain_diff:
        md.append(f"| {cd} | {count} |")
    md.append("")

    # Group by App Difficulty Level
    md.append("## Grouping by App Difficulty Level")
    md.append("")
    md.append("Applications are categorized into Easy, Medium, and Hard difficulty levels. These levels reflect the difficulty of the vulnerability chains, number of standalone flaws, and sophistication of decoys.")
    md.append("")
    
    # Summary of Difficulty counts
    md.append("### Difficulty Level Summary")
    md.append("| Difficulty Level | App Count | Standalone Vulns | Exploitation Chains |")
    md.append("|---|---|---|---|")
    for diff in ["Easy", "Medium", "Hard"]:
        apps = apps_by_difficulty.get(diff, [])
        v_count = sum(a["vulns_count"] for a in apps)
        c_count = sum(a["chains_count"] for a in apps)
        md.append(f"| {diff} | {len(apps)} | {v_count} | {c_count} |")
    md.append("")
    
    for diff in ["Easy", "Medium", "Hard"]:
        apps = apps_by_difficulty.get(diff, [])
        md.append(f"### {diff} Apps ({len(apps)} Apps)")
        md.append("")
        if not apps:
            md.append("No applications in this category.")
            md.append("")
            continue
            
        md.append("| App ID | Name | Language | Framework | Vulns | Chains |")
        md.append("|---|---|---|---|---|---|")
        for app in apps:
            # Format language & framework for pretty printing
            lang_pretty = app['language'].capitalize()
            fw_pretty = app['framework'].upper() if app['framework'] in ["jwt", "api", "ats", "cms", "iot", "p2p", "hr", "lms"] else app['framework'].capitalize()
            md.append(f"| {app['id']} | {app['name']} | {lang_pretty} | {fw_pretty} | {app['vulns_count']} | {app['chains_count']} |")
        md.append("")
        
    # Write to reports/overall.md
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    print(f"Overall report successfully generated at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
