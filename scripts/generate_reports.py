import json
import os
import re
import sys

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")
APPS_DIR = os.path.join(REPO_ROOT, "apps")

LANG_DIRS = {
    "python": os.path.join(APPS_DIR, "python"),
    "java": os.path.join(APPS_DIR, "java"),
    "typescript": os.path.join(APPS_DIR, "typescript"),
    "javascript": os.path.join(APPS_DIR, "javascript"),
}

def generate_report_markdown(vulns_data, app_folder_name):
    app_id = vulns_data["app_id"]
    app_name = vulns_data["app_name"]
    language = vulns_data["language"]
    framework = vulns_data.get("framework", "")
    
    # Capitalize framework and language for display
    lang_display = language.capitalize()
    
    # Framework display name formatting
    fw_upper = framework.upper()
    if fw_upper in ["JWT", "API", "ATS", "CMS", "IOT", "P2P", "HR", "LMS"]:
        fw_display = fw_upper
    elif framework:
        fw_display = framework.capitalize()
    else:
        fw_display = "N/A"
    
    # 1. Build Vulnerability Summary Table
    # Columns: | ID | OWASP | Category | Severity | Location | CWE |
    summary_rows = []
    for idx, vuln in enumerate(vulns_data.get("vulnerabilities", []), 1):
        owasp_id = vuln["owasp_id"]
        category = vuln["category"]
        severity = vuln["severity"].capitalize()
        location = vuln["location"]
        cwe = vuln.get("cwe", "")
        summary_rows.append(f"| V{idx} | {owasp_id} | {category} | {severity} | {location} | {cwe} |")
    summary_table = "\n".join(summary_rows)
    
    # 2. Build Standalone Vulnerabilities Details
    vuln_details = []
    for idx, vuln in enumerate(vulns_data.get("vulnerabilities", []), 1):
        owasp_id = vuln["owasp_id"]
        category = vuln["category"]
        severity = vuln["severity"].capitalize()
        location = vuln["location"]
        method = vuln.get("method", "")
        line_range = vuln.get("line_range", "N/A")
        description = vuln["description"]
        cwe = vuln.get("cwe", "")
        
        # CWE link
        cwe_match = re.match(r'CWE-(\d+)', cwe)
        if cwe_match:
            cwe_num = cwe_match.group(1)
            cwe_link = f"[{cwe}](https://cwe.mitre.org/data/definitions/{cwe_num}.html)"
        else:
            cwe_link = cwe if cwe else "N/A"
            
        detail = f"""### VULN-{idx:02d}: {owasp_id} — {category}

- **Severity:** {severity}
- **Location:** `{location}`:{line_range} (method: `{method}`)
- **CWE:** {cwe_link}

#### Description
{description}
"""
        vuln_details.append(detail)
    standalone_details = "\n".join(vuln_details)
    
    # 3. Build Chained Attack Scenarios
    chain_details = []
    for chain in vulns_data.get("chained_attacks", []):
        chain_id = chain["chain_id"]
        chain_name = chain.get("chain_name", "Chained Scenario")
        impact = chain.get("impact", "")
        difficulty = chain.get("difficulty", "medium").capitalize()
        subtlety_tags = " ".join([f"`{tag}`" for tag in chain.get("subtlety_tags", [])])
        
        # Prerequisites
        prereqs = chain.get("chain_prerequisites", [])
        if prereqs:
            prereqs_list = "\n".join([f"- {p}" for p in prereqs])
        else:
            prereqs_list = "- None specified"
            
        # Narrative
        narrative = chain.get("attack_scenario", "No narrative provided.")
        
        # Components table
        # We need the columns: | Step | Description | Severity | OWASP | CWE | Location | Method |
        comp_rows = []
        for comp in chain.get("components", []):
            step = comp["step"]
            comp_desc = comp["description"]
            comp_severity = comp["severity"].capitalize()
            comp_owasp = comp["owasp_id"]
            comp_cwe = comp.get("cwe", "")
            comp_loc = comp["location"]
            comp_method = comp.get("method", "")
            comp_rows.append(f"| {step} | {comp_desc} | {comp_severity} | {comp_owasp} | {comp_cwe} | {comp_loc} | `{comp_method}` |")
        components_table = "\n".join(comp_rows)
        
        chain_id_display = chain_id.upper() if isinstance(chain_id, str) else str(chain_id)
        
        chain_markup = f"""### {chain_id_display}: {chain_name}

- **Combined Impact:** `{impact}`
- **Difficulty:** {difficulty}
- **Subtlety Tags:** {subtlety_tags}

#### Prerequisites
{prereqs_list}

#### Attack Narrative
{narrative}

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
{components_table}
"""
        chain_details.append(chain_markup)
        
    chained_details = "\n".join(chain_details) if chain_details else "No chained attack scenarios defined."
    
    # 4. Build Decoys Table
    decoy_rows = []
    for decoy in vulns_data.get("decoys", []):
        decoy_loc = decoy["location"]
        decoy_desc = decoy["description"]
        decoy_rows.append(f"| {decoy_loc} | {decoy_desc} |")
    decoys_table = "\n".join(decoy_rows) if decoy_rows else "| None | No decoys defined. |"
    
    # Assemble complete markdown
    markdown = f"""# Security Report: {app_id} — {app_name}

**Language:** {lang_display} ({fw_display})
**Directory:** `apps/{language}/{app_folder_name}`

---

## Application Information
- **App ID:** {app_id}
- **Name:** {app_name}
- **Language:** {lang_display}
- **Framework:** {fw_display}

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
{summary_table}

---

## Standalone Vulnerabilities

{standalone_details}

---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

{chained_details}

---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
{decoys_table}
"""
    return markdown

def main():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        
    generated_count = 0
    errors_count = 0
    
    for lang, lang_dir in LANG_DIRS.items():
        if not os.path.isdir(lang_dir):
            continue
        for entry in sorted(os.listdir(lang_dir)):
            if entry.startswith("app-"):
                app_path = os.path.join(lang_dir, entry)
                vulns_path = os.path.join(app_path, ".vulns")
                if os.path.isfile(vulns_path):
                    try:
                        with open(vulns_path, "r", encoding="utf-8") as f:
                            vulns_data = json.load(f)
                        
                        markdown = generate_report_markdown(vulns_data, entry)
                        report_filename = f"{entry}.md"
                        report_path = os.path.join(REPORTS_DIR, report_filename)
                        
                        with open(report_path, "w", encoding="utf-8") as f:
                            f.write(markdown)
                            
                        print(f"Generated report for {entry} -> {report_filename}")
                        generated_count += 1
                    except Exception as e:
                        print(f"Error processing {entry}: {e}")
                        errors_count += 1
                        
    print(f"\nDone. Successfully generated {generated_count} reports. Errors: {errors_count}")

if __name__ == "__main__":
    main()
