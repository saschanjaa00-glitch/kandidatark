import json
import time
from urllib.request import Request, urlopen

# Sample some fagkodes from different index groups
SAMPLE_CODES = {
    'Index 0 (433 codes)': ['AKT2004', 'ANG2001', 'NOR1066'],
    'Index 2 (97 codes)': ['PSP5820'],
    'Index 3 (45 codes)': ['PSP5802'],
    'Index 4 (89 codes)': ['FSP6349'],
    'Index 7 (10 codes)': ['NOR1268'],
    'Index 9 (2 codes)': [],  # Need to find one
    'Index 13 (32 codes)': ['REA3060', 'MAT1021']
}

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

def check_expected_restrictions(fagkode):
    data = fetch_json(fagkode)
    if not data:
        print(f"❌ {fagkode}: No data")
        return
    
    system = (data.get("gjennomføringssystem") or "").upper()
    eksamen = data.get("eksamen") or {}
    aids = eksamen.get("aids") or {}
    
    is_sprakfag = bool(aids.get("isSpråkFag"))
    has_open_internet = bool(aids.get("hasOpenInternetAccess"))
    is_paste_disabled = bool(aids.get("isPasteDisabled"))
    is_seb = bool(data.get("isSebEksamen"))
    
    ck = (aids.get("ckEditorSetting") or {}).get("navn") or ""
    
    print(f"\n{fagkode} ({system}):")
    print(f"  Spell: {ck}")
    
    # For EPS, should always have these 3:
    if system == "EPS" and not is_seb:
        print(f"  ✅ Should have: Kommunisere + Begrenset internett + Chatbot")
        if is_sprakfag:
            print(f"  ✅ Should also have: Oversettelsesprogram")
        if is_paste_disabled:
            print(f"  ✅ Should also have: Paste/Word restriction")
    elif is_seb:
        print(f"  ℹ️  SEB exam - different rules")
    elif system == "PGSA":
        print(f"  ✅ PGSA two-part: Should have: Kommunisere + Begrenset internett + Chatbot")

for group, codes in SAMPLE_CODES.items():
    if codes:
        print(f"\n{'='*60}")
        print(f"{group}")
        print('='*60)
        for code in codes:
            check_expected_restrictions(code)
            time.sleep(0.3)
