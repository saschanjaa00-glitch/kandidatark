import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

def fetch_json(fagkode: str):
    url = f"https://kandidat.udir.no/api/eksamen-info/{fagkode}"
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    })
    try:
        with urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as e:
        print(f"Error: {e}")
        return None

# Check a MAT, REA, and SAM example
codes_to_check = ['MAT1021', 'REA3036', 'SAM3061']

for fagkode in codes_to_check:
    print(f"\n{'='*80}")
    print(f"Full JSON for: {fagkode}")
    print('='*80)
    data = fetch_json(fagkode)
    if data:
        print(json.dumps(data, indent=2, ensure_ascii=False))
