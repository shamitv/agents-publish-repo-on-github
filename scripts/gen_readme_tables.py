import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APPS_DIR = os.path.join(REPO_ROOT, "apps")

LANG_DIRS = ["python", "java", "typescript", "javascript"]

# Map app folder name to domain
DOMAINS = {
    # Python
    "app-01-ecommerce-catalog": "Retail",
    "app-02-patient-portal": "Healthcare",
    "app-03-banking-service": "FinTech",
    "app-04-real-estate": "Real Estate",
    "app-05-learning-mgmt": "Education",
    "app-21-insurance-claims": "Insurance",
    "app-22-food-delivery": "Food & Beverage",
    "app-23-govt-permits": "Government",
    "app-24-vet-clinic": "Veterinary",
    "app-25-supply-chain": "Logistics",
    "app-46-charity-donations": "Non-Profit",
    "app-47-smart-home": "IoT",
    "app-48-freelancer-market": "Gig Economy",
    "app-49-sports-league": "Sports",
    # Java
    "app-06-hr-management": "HR",
    "app-07-airline-booking": "Travel",
    "app-08-warehouse-mgmt": "Logistics",
    "app-09-legal-documents": "Legal",
    "app-10-telecom-billing": "Telecom",
    "app-26-pharma-tracking": "Pharma",
    "app-27-hotel-reservation": "Hospitality",
    "app-28-mfg-quality": "Manufacturing",
    "app-29-fleet-management": "Transportation",
    "app-30-auction-platform": "E-Commerce",
    "app-50-energy-billing": "Utilities",
    # TypeScript
    "app-11-social-analytics": "Marketing",
    "app-12-crypto-wallet": "FinTech",
    "app-13-project-mgmt": "SaaS",
    "app-14-telemedicine": "Telehealth",
    "app-15-digital-assets": "Media",
    "app-31-event-ticketing": "Entertainment",
    "app-32-support-tickets": "Customer Service",
    "app-33-recruitment-ats": "HR Tech",
    "app-34-subscription-box": "Subscription",
    "app-35-compliance-tracker": "RegTech",
    # JavaScript
    "app-16-restaurant-reviews": "Food & Hospitality",
    "app-17-iot-dashboard": "IoT",
    "app-18-p2p-lending": "FinTech",
    "app-19-cms": "Publishing",
    "app-20-fitness-tracker": "Health & Wellness",
    "app-36-parking-mgmt": "Transportation",
    "app-37-crop-planner": "Agriculture",
    "app-38-museum-catalog": "Arts & Culture",
    "app-39-wedding-planner": "Lifestyle",
    "app-40-pet-adoption": "Animal Welfare",
    "app-41-library-reservation": "Public Services",
    "app-42-construction-tracker": "Construction",
    "app-43-music-streaming": "Entertainment",
    "app-44-election-polling": "Civic Tech",
    "app-45-travel-expense": "Enterprise",
}

def main():
    for lang in LANG_DIRS:
        print(f"\n### {lang.capitalize()}")
        print("| # | App Name | Domain | Vulnerabilities |")
        print("|---|----------|--------|-----------------|")
        
        lang_dir = os.path.join(APPS_DIR, lang)
        if not os.path.isdir(lang_dir):
            continue
            
        for entry in sorted(os.listdir(lang_dir)):
            if entry.startswith("app-"):
                vulns_path = os.path.join(lang_dir, entry, ".vulns")
                if os.path.isfile(vulns_path):
                    with open(vulns_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    app_id = data["app_id"].replace("app-", "")
                    app_name = data["app_name"]
                    
                    vulns = data.get("vulnerabilities", [])
                    vuln_ids = sorted(list(set([v["owasp_id"] for v in vulns])))
                    vuln_str = ", ".join(vuln_ids)
                    
                    domain = DOMAINS.get(entry, "Other")
                    link = f"apps/{lang}/{entry}/README.md"
                    
                    print(f"| {app_id} | [{app_name}]({link}) | {domain} | {vuln_str} |")

if __name__ == "__main__":
    main()
