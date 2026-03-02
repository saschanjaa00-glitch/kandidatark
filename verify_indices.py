import re
import json
from collections import defaultdict

# Read the compactified database file
with open('data/examDatabaseCompact.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract dictionary entries
index_usage = defaultdict(list)
matches = re.findall(r"'([A-Z0-9]+)':\s*\[([^\]]+)\]", content)

for fagkode, data in matches:
    # Parse the array
    parts = [p.strip().strip("'") for p in data.split(',')]
    if len(parts) >= 5:
        text_index = parts[4]
        # Check if it's a number (valid index)
        if text_index.isdigit():
            index_usage[int(text_index)].append(fagkode)

print("=" * 80)
print("INDEX USAGE SUMMARY")
print("=" * 80)

# Define what each index represents
index_descriptions = {
    0: "EPS Hovedmål - all 3 restrictions",
    1: "SEB exam (different rules)",
    2: "EPS Automatisk + Språkfag + oversettelse + paste",
    3: "EPS Ingen + Språkfag + oversettelse",
    4: "EPS Ingen + Språkfag + oversettelse + paste",
    5: "EPS Ingen + paste",
    6: "SEB Hovedmål (different rules)",
    7: "EPS Hovedmål + Språkfag + oversettelse",
    8: "EPS simplified (no stavekontroll prefix)",
    9: "EPS Sidemål + Språkfag + oversettelse",
    10: "EPS Automatisk + paste",
    11: "EPS Ingen",
    12: "EPS Automatisk + Språkfag + oversettelse",
    13: "PGSA two-part"
}

for idx in sorted(index_usage.keys()):
    fagkoder = sorted(index_usage[idx])
    print(f"\nIndex {idx}: {index_descriptions.get(idx, 'Unknown')} ({len(fagkoder)} fagkoder)")
    print(f"  Samples: {', '.join(fagkoder[:5])}")
    if len(fagkoder) > 5:
        print(f"           ... and {len(fagkoder) - 5} more")

# Check which indices have all three restrictions
print("\n" + "=" * 80)
print("RESTRICTION VERIFICATION")
print("=" * 80)

restrictions = [
    "Det er ikke tillatt å kommunisere med andre på nettet eller på andre måter under eksamen",
    "Du har tilgang til et begrenset utvalg nettbaserte hjelpemidler, men ikke internett for øvrig",
    "Du kan ikke bruke automatisk tekstgenerator som chatbot eller tilsvarende teknologi"
]

# Extract dictionary from file
dict_match = re.search(r'window\.examTextDictionary = \[(.*?)\];', content, re.DOTALL)
if dict_match:
    dict_content = '[' + dict_match.group(1) + ']'
    # Parse the entries
    entries = re.findall(r"'([^']*(?:\\'[^']*)*)'", dict_content)
    
    for idx, entry in enumerate(entries):
        has_restrictions = [any(r in entry for r in [restrictions[i]]) for i in range(3)]
        status = "✅" if all(has_restrictions) else "❌"
        
        print(f"\nIndex {idx}: {status}")
        for i, restriction in enumerate(restrictions):
            check = "✅" if has_restrictions[i] else "❌"
            print(f"  {check} Restriction {i+1}")
        
        if has_restrictions[0]:
            # Show prefix
            if "Denne eksamenen" in entry:
                prefix = entry.split("Alle hjelpemidler")[0][:50]
                print(f"  Prefix: {prefix}...")
