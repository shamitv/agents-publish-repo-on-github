import json, os

apps_dir = 'apps'
apps_data = []
all_vulns = {}
all_chains = {}
lang_count = {}
lang_framework = {}

for lang in sorted(os.listdir(apps_dir)):
    lp = os.path.join(apps_dir, lang)
    if not os.path.isdir(lp):
        continue
    for app in sorted(os.listdir(lp)):
        ap = os.path.join(lp, app)
        vp = os.path.join(ap, '.vulns')
        if not os.path.isfile(vp):
            continue
        with open(vp) as f:
            data = json.load(f)

        app_id = data['app_id']
        app_name = data['app_name']
        framework = data.get('framework', '')

        vulns = data.get('vulnerabilities', [])
        chains = data.get('chained_attacks', [])

        apps_data.append((app_id, app_name, lang, framework, len(vulns), len(chains)))

        for v in vulns:
            oid = v['owasp_id']
            if oid not in all_vulns:
                all_vulns[oid] = []
            all_vulns[oid].append(app_id)

        for c in chains:
            imp = c['impact']
            if imp not in all_chains:
                all_chains[imp] = []
            all_chains[imp].append(app_id)

        lang_count[lang] = lang_count.get(lang, 0) + 1
        if lang not in lang_framework:
            lang_framework[lang] = set()
        lang_framework[lang].add(framework)

print('=== APP TABLE ===')
print('| # | App | Language | Framework | Vulns | Chains |')
print('|---|-----|----------|-----------|-------|--------|')
for i, (aid, aname, lang, fw, nv, nc) in enumerate(apps_data, 1):
    print('| %d | %s | %s | %s | %d | %d |' % (i, aname, lang, fw, nv, nc))

print()
print('=== LANGUAGE BREAKDOWN ===')
for lang in sorted(lang_count):
    print('%s: %d apps (%s)' % (lang, lang_count[lang], ', '.join(sorted(lang_framework[lang]))))
print('Total: %d apps' % sum(lang_count.values()))

print()
print('=== OWASP COVERAGE ===')
for oid in sorted(all_vulns):
    app_list = sorted(set(all_vulns[oid]))
    print('%s: %d apps -> %s' % (oid, len(app_list), ', '.join(app_list)))

print()
print('=== CHAIN IMPACT DISTRIBUTION ===')
for imp in sorted(all_chains):
    app_list = sorted(set(all_chains[imp]))
    print('%s: %d apps -> %s' % (imp, len(app_list), ', '.join(app_list)))