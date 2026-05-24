import json, os

apps_dir = 'apps'
total_chains = 0
chain_counts = {}
difficulty = {}

difficulty_map = {
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

for lang in os.listdir(apps_dir):
    lang_path = os.path.join(apps_dir, lang)
    if not os.path.isdir(lang_path):
        continue
    for app in os.listdir(lang_path):
        app_path = os.path.join(lang_path, app)
        vulns_path = os.path.join(app_path, '.vulns')
        if os.path.isfile(vulns_path):
            with open(vulns_path) as f:
                data = json.load(f)
            chains = data.get('chained_attacks', [])
            num_chains = len(chains)
            total_chains += num_chains
            if num_chains not in chain_counts:
                chain_counts[num_chains] = 0
            chain_counts[num_chains] += 1
            
            d = difficulty_map.get(app, 'Unknown')
            if d not in difficulty:
                difficulty[d] = {'apps': 0, 'chains': 0}
            difficulty[d]['apps'] += 1
            difficulty[d]['chains'] += num_chains

print(f'Total exploit chains across all apps: {total_chains}')
print(f'Chain count distribution: {dict(sorted(chain_counts.items()))}')
print()
print('Difficulty Distribution:')
for d in ['Easy', 'Medium', 'Hard']:
    if d in difficulty:
        print(f'  {d}: {difficulty[d]["apps"]} apps, {difficulty[d]["chains"]} chains')
print(f'  Total: {sum(v["apps"] for v in difficulty.values())} apps, {sum(v["chains"] for v in difficulty.values())} chains')