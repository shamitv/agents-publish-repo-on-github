import json
import os
import sys

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APPS_DIR = os.path.join(REPO_ROOT, "apps")
OUTPUT_PATH = os.path.join(REPO_ROOT, "reports", "README.md")

LANG_DIRS = ["python", "java", "typescript", "javascript"]

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

OWASP_DESCRIPTIONS = {
    "A01": "Broken Access Control",
    "A02": "Cryptographic Failures",
    "A03": "Injection",
    "A04": "Insecure Design",
    "A05": "Security Misconfiguration",
    "A06": "Vulnerable/Outdated Components",
    "A07": "Identification/Auth Failures",
    "A08": "Software/Data Integrity",
    "A09": "Security Logging Failures",
    "A10": "Server-Side Request Forgery"
}

IMPACT_DESCRIPTIONS = {
    "account_takeover": "Account Takeover",
    "data_modification": "Data Modification",
    "db_exfiltration": "Database Exfiltration",
    "lateral_movement": "Lateral Movement"
}

def main():
    apps_info = []
    
    # Track statistics
    lang_counts = {}
    lang_frameworks = {}
    owasp_apps = {oid: [] for oid in OWASP_DESCRIPTIONS}
    impact_apps = {imp: [] for imp in IMPACT_DESCRIPTIONS}
    difficulty_apps = {"Easy": [], "Medium": [], "Hard": []}
    
    total_chains = 0
    all_vuln_counts = []
    all_chain_counts = []
    
    for lang in LANG_DIRS:
        lang_dir = os.path.join(APPS_DIR, lang)
        if not os.path.isdir(lang_dir):
            continue
        for entry in os.listdir(lang_dir):
            if entry.startswith("app-"):
                vulns_path = os.path.join(lang_dir, entry, ".vulns")
                if os.path.isfile(vulns_path):
                    with open(vulns_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    app_id = data["app_id"]
                    app_num = int(app_id.replace("app-", ""))
                    app_name = data["app_name"]
                    framework = data.get("framework", "")
                    
                    vulns = data.get("vulnerabilities", [])
                    chains = data.get("chained_attacks", [])
                    
                    # Accumulate lists
                    all_vuln_counts.append(len(vulns))
                    all_chain_counts.append(len(chains))
                    total_chains += len(chains)
                    
                    # Lang & Framework counting
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1
                    if lang not in lang_frameworks:
                        lang_frameworks[lang] = set()
                    lang_frameworks[lang].add(framework)
                    
                    # Standalone OWASP mapping (unique apps per category)
                    for v in vulns:
                        oid = v["owasp_id"]
                        if app_id not in owasp_apps[oid]:
                            owasp_apps[oid].append(app_id)
                            
                    # Chained impact mapping (unique apps per impact)
                    for c in chains:
                        imp = c.get("impact", "")
                        if imp in impact_apps and app_id not in impact_apps[imp]:
                            impact_apps[imp].append(app_id)
                            
                    # Difficulty level mapping
                    diff_level = DIFFICULTY_MAP.get(app_id, "Medium")
                    difficulty_apps[diff_level].append(app_id)
                    
                    apps_info.append({
                        "num": app_num,
                        "id": app_id,
                        "name": app_name,
                        "lang": lang,
                        "framework": framework,
                        "vulns": len(vulns),
                        "chains": len(chains)
                    })
                    
    # Sort apps numerically by app number
    apps_info.sort(key=lambda x: x["num"])
    
    # Start building README content
    md = []
    md.append("# Secure Code Hunt — Audit Reports")
    md.append("")
    md.append("This directory contains security audit reports for all **50 intentionally vulnerable applications** in the **secure-code-hunt** benchmark.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Repository Overview")
    md.append("")
    md.append("**Purpose:** An intentionally vulnerable application corpus for benchmarking AI security-detection agents against OWASP Top 10: 2021.")
    md.append("")
    md.append("| Metric | Value |")
    md.append("|--------|-------|")
    md.append("| **Total Apps** | **50** |")
    
    # Formats for language names & framework lists
    lang_display_names = {
        "python": "Python apps",
        "java": "Java apps",
        "javascript": "JavaScript apps",
        "typescript": "TypeScript apps"
    }
    
    for l in LANG_DIRS:
        count = lang_counts.get(l, 0)
        fws = sorted(list(lang_frameworks.get(l, [])))
        # Format framework names: uppercase for known abbreviations, capitalize others
        formatted_fws = []
        for fw in fws:
            if fw.lower() in ["django", "fastapi", "flask", "express", "nestjs"]:
                if fw.lower() == "fastapi":
                    formatted_fws.append("FastAPI")
                elif fw.lower() == "nestjs":
                    formatted_fws.append("NestJS")
                else:
                    formatted_fws.append(fw.capitalize())
            elif fw.lower() == "spring-boot":
                formatted_fws.append("Spring Boot")
            else:
                formatted_fws.append(fw)
        fws_str = ", ".join(formatted_fws)
        md.append(f"| **{lang_display_names[l]}** | {count} ({fws_str}) |")
        
    md.append(f"| **Standalone vulns per app** | {min(all_vuln_counts)}–{max(all_vuln_counts)} |")
    md.append(f"| **Chained attacks per app** | {min(all_chain_counts)}–{max(all_chain_counts)} |")
    md.append(f"| **Total exploit chains** | {total_chains} |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Completed Audit Reports")
    md.append("")
    md.append("| # | App | Language | Framework | Vulns | Chains |")
    md.append("|---|-----|----------|-----------|-------|--------|")
    for app in apps_info:
        # Format language and framework to match exactly
        lang_str = app["lang"].lower()
        fw_str = app["framework"].lower()
        md.append(f"| {app['num']} | {app['name']} | {lang_str} | {fw_str} | {app['vulns']} | {app['chains']} |")
        
    md.append("")
    md.append("---")
    md.append("")
    md.append("## OWASP Coverage")
    md.append("")
    md.append("| OWASP ID | Category | Apps with This Vuln |")
    md.append("|----------|----------|---------------------|")
    
    for oid in sorted(OWASP_DESCRIPTIONS.keys()):
        desc = OWASP_DESCRIPTIONS[oid]
        # Sort app numbers
        nums = sorted([int(aid.replace("app-", "")) for aid in owasp_apps[oid]])
        nums_str = ", ".join([f"{n:02d}" for n in nums])
        md.append(f"| {oid} | {desc} | {len(nums)} apps — {nums_str} |")
        
    md.append("")
    md.append("All 10 OWASP Top 10:2021 categories are covered across the 50 apps.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Chained Attack Coverage")
    md.append("")
    
    # Sort impacts to ensure predictable ordering
    sorted_impacts = ["account_takeover", "data_modification", "db_exfiltration", "lateral_movement"]
    
    md.append("| Impact | Apps with This Chain Type |")
    md.append("|--------|--------------------------|")
    for imp in sorted_impacts:
        desc = IMPACT_DESCRIPTIONS[imp]
        nums = sorted([int(aid.replace("app-", "")) for aid in impact_apps[imp]])
        nums_str = ", ".join([f"{n:02d}" for n in nums])
        md.append(f"| {desc} | {len(nums)} apps — {nums_str} |")
        
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Difficulty Breakdown")
    md.append("")
    md.append("| Level | Rating | Apps |")
    md.append("|-------|--------|------|")
    for diff in ["Easy", "Medium", "Hard"]:
        nums = sorted([int(aid.replace("app-", "")) for aid in difficulty_apps[diff]])
        nums_str = ", ".join([f"{n:02d}" for n in nums])
        md.append(f"| {diff} | {len(nums)} apps | {nums_str} |")
        
    md.append("")
    md.append("Each report's `Difficulty` column links to the individual report file for detailed analysis.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Methodology")
    md.append("")
    md.append("Each report follows this structure:")
    md.append("- **Standalone vulnerabilities** — OWASP category, severity, location, exploitation difficulty")
    md.append("- **Chained attack** — Step-by-step chain of low/medium issues reaching high-impact outcome")
    md.append("- **Difficulty rating** — Easy, Medium, or Hard based on required exploit knowledge and complexity")
    md.append("")
    md.append("Vulnerability detection agents should be able to identify all issues listed without fixing them (per AGENTS.md rules). Decoy safe patterns are intentionally placed near vulnerable code to measure agent precision (false-positive rate).")
    
    # Write output to reports/README.md
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
        
    print(f"reports/README.md successfully updated at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()