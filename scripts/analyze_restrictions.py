import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from collections import defaultdict

# Sample some EPS (digital) fagkoder to check their restrictions
SAMPLE_EPS_CODES = [
    'AKT2004', 'ANG2001', 'NOR1066', 'NOR1268', 'HIS2015', 'GEO2007',
    'FSP6349', 'PSP5790', 'PSP5802', 'PSP5820'
]

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
        return None

def analyze_restrictions(fagkode: str):
    data = fetch_json(fagkode)
    if not data:
        return None
    
    system = (data.get("gjennomføringssystem") or "").upper()
    eksamen = data.get("eksamen") or {}
    aids = eksamen.get("aids") or {}
    
    is_sprakfag = bool(aids.get("isSpråkFag"))
    has_open_internet = bool(aids.get("hasOpenInternetAccess"))
    is_paste_disabled = bool(aids.get("isPasteDisabled"))
    is_seb = bool(data.get("isSebEksamen"))
    
    ck = (aids.get("ckEditorSetting") or {}).get("navn") or ""
    ck_lower = ck.lower()
    
    if "automatisk" in ck_lower:
        spell = "Automatisk"
    elif "hovedmål" in ck_lower:
        spell = "Hovedmål"
    elif "sidemål" in ck_lower:
        spell = "Sidemål"
    elif "ingen" in ck_lower:
        spell = "Ingen"
    else:
        spell = "Ukjent"
    
    return {
        'fagkode': fagkode,
        'system': system,
        'spellcheck': spell,
        'is_sprakfag': is_sprakfag,
        'has_open_internet': has_open_internet,
        'is_paste_disabled': is_paste_disabled,
        'is_seb': is_seb
    }

print("Analyzing EPS exam restrictions:")
print("="*80)

for fagkode in SAMPLE_EPS_CODES:
    info = analyze_restrictions(fagkode)
    if info:
        print(f"\n{info['fagkode']}:")
        print(f"  System: {info['system']}")
        print(f"  Spellcheck: {info['spellcheck']}")
        print(f"  Språkfag: {info['is_sprakfag']}")
        print(f"  Open Internet: {info['has_open_internet']}")
        print(f"  Paste Disabled: {info['is_paste_disabled']}")
        print(f"  SEB: {info['is_seb']}")
        
        # Expected restrictions
        print(f"  Expected restrictions:")
        print(f"    - Kommunisere: YES (always for EPS)")
        if info['system'] == 'EPS':
            if info['has_open_internet']:
                print(f"    - Begrenset internett: NO (open internet)")
            else:
                print(f"    - Begrenset internett: YES")
            print(f"    - Chatbot: YES (always for EPS)")
        if info['is_sprakfag']:
            print(f"    - Oversettelsesprogram: YES (språkfag)")
        if info['is_paste_disabled']:
            print(f"    - Paste/Word: YES (paste disabled)")
    
    time.sleep(0.3)
