#!/usr/bin/env python3
"""
Prep-for-Runs: Clean vulnerability annotations from all 50 apps.
Removes VULNERABILITY and CHAIN LINK comments from source code,
extracts chain scenarios to scenarios.md, archives impl_plan.md files.
"""

import os
import re
import json
import sys
import shutil

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'docs', 'plans', 'prep-for-runs', 'archived-impl-plans')

# All 50 apps with their language, id, name, and directory
APPS = [
    # Batch 1: Python (14 apps)
    ('python', 'app-01', 'ecommerce-catalog'),
    ('python', 'app-02', 'patient-portal'),
    ('python', 'app-03', 'banking-service'),
    ('python', 'app-04', 'real-estate'),
    ('python', 'app-05', 'learning-mgmt'),
    ('python', 'app-21', 'insurance-claims'),
    ('python', 'app-22', 'food-delivery'),
    ('python', 'app-23', 'govt-permits'),
    ('python', 'app-24', 'vet-clinic'),
    ('python', 'app-25', 'supply-chain'),
    ('python', 'app-46', 'charity-donations'),
    ('python', 'app-47', 'smart-home'),
    ('python', 'app-48', 'freelancer-market'),
    ('python', 'app-49', 'sports-league'),
    # Batch 2: Java (11 apps)
    ('java', 'app-06', 'hr-management'),
    ('java', 'app-07', 'airline-booking'),
    ('java', 'app-08', 'warehouse-mgmt'),
    ('java', 'app-09', 'legal-documents'),
    ('java', 'app-10', 'telecom-billing'),
    ('java', 'app-26', 'pharma-tracking'),
    ('java', 'app-27', 'hotel-reservation'),
    ('java', 'app-28', 'mfg-quality'),
    ('java', 'app-29', 'fleet-management'),
    ('java', 'app-30', 'auction-platform'),
    ('java', 'app-50', 'energy-billing'),
    # Batch 3: JavaScript (15 apps)
    ('javascript', 'app-16', 'restaurant-reviews'),
    ('javascript', 'app-17', 'iot-dashboard'),
    ('javascript', 'app-18', 'p2p-lending'),
    ('javascript', 'app-19', 'cms'),
    ('javascript', 'app-20', 'fitness-tracker'),
    ('javascript', 'app-36', 'parking-mgmt'),
    ('javascript', 'app-37', 'crop-planner'),
    ('javascript', 'app-38', 'museum-catalog'),
    ('javascript', 'app-39', 'wedding-planner'),
    ('javascript', 'app-40', 'pet-adoption'),
    ('javascript', 'app-41', 'library-reservation'),
    ('javascript', 'app-42', 'construction-tracker'),
    ('javascript', 'app-43', 'music-streaming'),
    ('javascript', 'app-44', 'election-polling'),
    ('javascript', 'app-45', 'travel-expense'),
    # Batch 4: TypeScript (10 apps)
    ('typescript', 'app-11', 'social-analytics'),
    ('typescript', 'app-12', 'crypto-wallet'),
    ('typescript', 'app-13', 'project-mgmt'),
    ('typescript', 'app-14', 'telemedicine'),
    ('typescript', 'app-15', 'digital-assets'),
    ('typescript', 'app-31', 'event-ticketing'),
    ('typescript', 'app-32', 'support-tickets'),
    ('typescript', 'app-33', 'recruitment-ats'),
    ('typescript', 'app-34', 'subscription-box'),
    ('typescript', 'app-35', 'compliance-tracker'),
]

ANNOTATION_PATTERNS = [
    # Python comments
    re.compile(r'#\s*VULNERABILITY\s.*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'#\s*CHAIN\s+LINK\s.*$', re.IGNORECASE | re.MULTILINE),
    # Java/JS/TS single-line comments
    re.compile(r'//\s*VULNERABILITY\s.*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'//\s*CHAIN\s+LINK\s.*$', re.IGNORECASE | re.MULTILINE),
    # Multi-line block comments with VULNERABILITY/CHAIN LINK
    re.compile(r'/\*[\s\S]*?VULNERABILITY[\s\S]*?\*/', re.IGNORECASE),
    re.compile(r'/\*[\s\S]*?CHAIN\s+LINK[\s\S]*?\*/', re.IGNORECASE),
    # Python docstring comments with VULNERABILITY
    re.compile(r'""".*?VULNERABILITY.*?"""', re.IGNORECASE | re.DOTALL),
    re.compile(r""".*?VULNERABILITY.*?""", re.IGNORECASE | re.DOTALL),
    re.compile(r'""".*?CHAIN\s+LINK.*?"""', re.IGNORECASE | re.DOTALL),
    re.compile(r""".*?CHAIN\s+LINK.*?""", re.IGNORECASE | re.DOTALL),
]

# Also catch inline comments like: # VULNERABILITY A03: ..
INLINE_PATTERN = re.compile(r'(#|//)\s*VULNERABILITY\s.*?(?=\n)', re.IGNORECASE)
INLINE_CHAIN_PATTERN = re.compile(r'(#|//)\s*CHAIN\s+LINK\s.*?(?=\n)', re.IGNORECASE)

def get_app_dir(language, app_id, app_name):
    return os.path.join(BASE_DIR, 'apps', language, f'{app_id}-{app_name}')

def get_source_files(app_dir):
    """Get all source files in the app directory."""
    extensions = ('.py', '.java', '.js', '.ts', '.html')
    files = []
    for root, dirs, filenames in os.walk(app_dir):
        # Skip node_modules
        dirs[:] = [d for d in dirs if d != 'node_modules' and d != '__pycache__']
        for fn in filenames:
            if fn.endswith(extensions):
                files.append(os.path.join(root, fn))
    return files

def count_annotations(content):
    """Count VULNERABILITY and CHAIN LINK annotations in content."""
    count = 0
    for pattern in ANNOTATION_PATTERNS:
        count += len(pattern.findall(content))
    count += len(INLINE_PATTERN.findall(content))
    count += len(INLINE_CHAIN_PATTERN.findall(content))
    return count

def clean_annotations(content):
    """Remove all VULNERABILITY and CHAIN LINK annotation comments from content."""
    for pattern in ANNOTATION_PATTERNS:
        content = pattern.sub('', content)
    content = INLINE_PATTERN.sub('', content)
    content = INLINE_CHAIN_PATTERN.sub('', content)
    # Clean up empty lines that might result from removing comment lines
    lines = content.split('\n')
    cleaned = []
    for line in lines:
        if line.strip():
            cleaned.append(line)
    return '\n'.join(cleaned)

def extract_chain_section(readme_content):
    """Extract the chained vulnerability scenario section from README."""
    # Find ## Chained Vulnerability Scenario or ## Chain Vulnerability Scenario
    match = re.search(r'##\s+Chain(?:ed)?\s+Vulnerability\s+Scenario.*?(?=\n##\s|\Z)', readme_content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return None

def create_scenarios_md(app_dir, app_name, chain_content):
    """Create scenarios.md file from extracted chain content."""
    if not chain_content:
        return False
    
    # Parse the chain content to extract details for the table
    scenarios_path = os.path.join(app_dir, 'scenarios.md')
    
    # Extract the chain name
    chain_name_match = re.search(r'##\s+Chain:\s*"([^"]*)"', chain_content)
    chain_name = chain_name_match.group(1) if chain_name_match else "Unnamed Chain"
    
    # Extract the table from the content
    table_match = re.search(r'\|.*?\n\|.*?\n(\|.*?\n)+', chain_content)
    table_content = table_match.group(0) if table_match else ""
    
    # Extract attack narrative
    narrative_match = re.search(r'\*\*Attack narrative\*\*:\s*(.*?)(?:\n\n|\Z)', chain_content, re.DOTALL)
    narrative = narrative_match.group(1).strip() if narrative_match else ""
    
    # Extract combined impact
    impact_match = re.search(r'\*\*Combined Impact\*\*:\s*(.*?)(?:\n\n|\Z)', chain_content, re.DOTALL)
    impact = impact_match.group(1).strip() if impact_match else ""
    
    scenarios_md = f"""# Chained Vulnerability Scenarios — {app_name}

## Chain: "{chain_name}"

{table_content}

**Attack narrative**: {narrative}

**Combined Impact**: {impact}

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
"""
    with open(scenarios_path, 'w', encoding='utf-8') as f:
        f.write(scenarios_md)
    return True

def update_readme(app_dir):
    """Update README.md to replace chain section with a link to scenarios.md."""
    readme_path = os.path.join(app_dir, 'README.md')
    if not os.path.exists(readme_path):
        return False
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the chained vulnerability scenario section
    new_content = re.sub(
        r'##\s+Chain(?:ed)?\s+Vulnerability\s+Scenario.*?(?=\n##\s|\Z)',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    ).strip()
    
    # Add reference to scenarios.md in the features section or at the end
    if 'For chained vulnerability scenarios' not in new_content:
        # Find ## Features and add after it
        features_match = re.search(r'##\s+Features', new_content)
        if features_match:
            new_content = new_content.replace(
                features_match.group(0),
                features_match.group(0) + '\n\nFor chained vulnerability scenarios, see [scenarios.md](scenarios.md).'
            )
        else:
            new_content += '\n\nFor chained vulnerability scenarios, see [scenarios.md](scenarios.md).'
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

def archive_impl_plan(language, app_id, app_name, app_dir):
    """Move impl_plan.md to the archive directory."""
    impl_plan_path = os.path.join(app_dir, 'impl_plan.md')
    if not os.path.exists(impl_plan_path):
        return False
    
    archive_name = f'{language}-{app_id}-{app_name}-impl_plan.md'
    archive_path = os.path.join(ARCHIVE_DIR, archive_name)
    
    # Use shutil.move instead of git mv since we'll do git operations separately
    shutil.move(impl_plan_path, archive_path)
    print(f"  Archived: {archive_name}")
    return True

def process_app(language, app_id, app_name):
    """Process a single app: scan, clean, extract scenarios, archive."""
    app_dir = get_app_dir(language, app_id, app_name)
    
    if not os.path.exists(app_dir):
        print(f"  SKIP: {language}/{app_id}-{app_name} - directory not found")
        return False
    
    print(f"\n=== Processing {language}/{app_id}-{app_name} ===")
    
    # STEP A: SCAN - find all annotation files
    source_files = get_source_files(app_dir)
    total_annotations = 0
    files_with_annotations = []
    
    for sf in source_files:
        try:
            with open(sf, 'r', encoding='utf-8') as f:
                content = f.read()
            count = count_annotations(content)
            if count > 0:
                files_with_annotations.append((sf, count))
                total_annotations += count
        except Exception as e:
            print(f"  ERROR reading {sf}: {e}")
    
    print(f"  Found {total_annotations} annotation(s) in {len(files_with_annotations)} file(s)")
    for sf, count in files_with_annotations:
        rel_path = os.path.relpath(sf, app_dir)
        print(f"    {rel_path}: {count} annotation(s)")
    
    # STEP B: REMOVE annotations from source code
    for sf, count in files_with_annotations:
        with open(sf, 'r', encoding='utf-8') as f:
            content = f.read()
        cleaned = clean_annotations(content)
        with open(sf, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f"  Cleaned: {os.path.relpath(sf, app_dir)}")
    
    # STEP C: Extract chain scenario to scenarios.md, update README.md
    readme_path = os.path.join(app_dir, 'README.md')
    scenarios_path = os.path.join(app_dir, 'scenarios.md')
    
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        chain_section = extract_chain_section(readme_content)
        
        # Get app name from README for scenarios.md title
        app_name_readable = app_name.replace('-', ' ').title()
        
        if chain_section and not os.path.exists(scenarios_path):
            create_scenarios_md(app_dir, app_name_readable, chain_section)
            print(f"  Created: scenarios.md")
        
        # Update README
        update_readme(app_dir)
        print(f"  Updated: README.md")
    
    # STEP D: Archive impl_plan.md
    archived = archive_impl_plan(language, app_id, app_name, app_dir)
    if not archived:
        print(f"  No impl_plan.md to archive")
    
    # STEP E: Verify
    total_remaining = 0
    for sf in source_files:
        if os.path.exists(sf):
            with open(sf, 'r', encoding='utf-8') as f:
                content = f.read()
            total_remaining += count_annotations(content)
    
    if total_remaining == 0:
        print(f"  VERIFY: PASS - No annotations remaining")
    else:
        print(f"  VERIFY: FAIL - {total_remaining} annotation(s) still present")
        return False
    
    return True

def main():
    print(f"Prep-for-Runs: Cleaning vulnerability annotations from {len(APPS)} apps")
    print(f"Archive directory: {ARCHIVE_DIR}")
    print("=" * 60)
    
    results = []
    
    for i, (language, app_id, app_name) in enumerate(APPS, 1):
        success = process_app(language, app_id, app_name)
        results.append((language, app_id, app_name, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r[3])
    failed = sum(1 for r in results if not r[3])
    
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed > 0:
        print("\nFailed apps:")
        for language, app_id, app_name, success in results:
            if not success:
                print(f"  {language}/{app_id}-{app_name}")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())