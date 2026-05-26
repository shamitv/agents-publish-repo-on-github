import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMPLEXITY_PLANS_DIR = os.path.join(REPO_ROOT, "docs", "plans", "complexity")

CONSTRAINT_MARKDOWN = """
---

## 5. Code Comment Constraints (Agent Tipping Prevention)
- **No Code-Level Tips**: Source code files (`src/`) must not contain any explicit comments, annotations, or markers (e.g. `// VULNERABILITY`, `// CHAIN LINK`, etc.) that could tip off security-detection agents.
- **Metadata Localization**: All details regarding standalone vulnerabilities, exploit chains, and locations are strictly restricted to the ground-truth metadata files (`.vulns` JSON manifest) and internal reference files (`scenarios.md`).
"""

def update_plans():
    if not os.path.isdir(COMPLEXITY_PLANS_DIR):
        print(f"Directory not found: {COMPLEXITY_PLANS_DIR}")
        return

    for entry in sorted(os.listdir(COMPLEXITY_PLANS_DIR)):
        app_dir = os.path.join(COMPLEXITY_PLANS_DIR, entry)
        if not os.path.isdir(app_dir):
            continue

        plan_path = os.path.join(app_dir, "plan.md")
        todo_path = os.path.join(app_dir, "todo.md")

        # 1. Update plan.md
        if os.path.isfile(plan_path):
            with open(plan_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check if constraint is already present
            if "Agent Tipping Prevention" not in content:
                content = content.strip() + "\n" + CONSTRAINT_MARKDOWN
                with open(plan_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Updated plan.md for {entry}")
            else:
                print(f"plan.md for {entry} already contains constraints")

        # 2. Update todo.md
        if os.path.isfile(todo_path):
            with open(todo_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Look for Verification Phase to insert the check
            updated = False
            new_lines = []
            todo_text = "- [ ] Audit all source code to ensure NO comments or annotations exist that can tip off agents. Limit all vulnerability/chain mapping details strictly to `.vulns` and `scenarios.md`."
            
            # Check if already present
            joined_content = "".join(lines)
            if todo_text not in joined_content:
                for line in lines:
                    if "Verify SQL injection" in line or "Verify IDOR" in line or "Verify weak" in line or "Verify Log4j" in line:
                        if not updated:
                            new_lines.append(f"{todo_text}\n")
                            updated = True
                    new_lines.append(line)
                
                # If we couldn't find a matching line to insert before, append it
                if not updated:
                    new_lines.append(f"\n{todo_text}\n")
                
                with open(todo_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                print(f"Updated todo.md for {entry}")
            else:
                print(f"todo.md for {entry} already contains the audit task")

if __name__ == "__main__":
    update_plans()
