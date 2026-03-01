import json
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# All two-part exams found
TWO_PART_CODES = [
    # MAT codes
    'MAT1019', 'MAT1021', 'MAT1023', 'MAT1111', 'MAT1113', 'MAT1115', 'MAT1117', 
    'MAT1119', 'MAT1121', 'MAT1123', 'MAT1125', 'MAT1127', 'MAT1129', 'MAT1131', 
    'MAT1133', 'MAT1135', 'MAT1137', 'MAT1139', 'MAT1141', 'MAT1143', 'MAT1145', 
    'MAT1147', 'MAT1149', 'MAT1151',
    # REA codes
    'REA3036', 'REA3039', 'REA3046', 'REA3056', 'REA3058', 'REA3060', 'REA3062',
    # SAM codes
    'SAM3061'
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
    except HTTPError as e:
        if e.code == 404:
            return None
        raise
    except Exception as e:
        print(f"Error fetching {fagkode}: {e}")
        return None

def check_exam(fagkode: str):
    print(f"\n{'='*80}")
    print(f"Checking: {fagkode}")
    print('='*80)
    
    data = fetch_json(fagkode)
    if not data:
        print(f"  ❌ No data available")
        return
    
    # Check gjennomføringssystem
    system = (data.get("gjennomføringssystem") or "").upper()
    print(f"  System: {system}")
    
    # Check eksamensdeler
    eksamensdeler = data.get("eksamensdeler") or []
    print(f"  Number of parts: {len(eksamensdeler)}")
    
    for i, del_data in enumerate(eksamensdeler, 1):
        print(f"\n  Del {i}:")
        print(f"    Name: {del_data.get('navn')}")
        print(f"    Type: {del_data.get('eksamensdeltype')}")
        print(f"    System: {del_data.get('gjennomføringssystem')}")
        start = del_data.get('starttidspunkt')
        slutt = del_data.get('sluttidspunkt')
        print(f"    Time: {start} - {slutt}")
        
        # Check aids for this part
        aids = del_data.get('aids')
        if aids:
            print(f"    Aids info: {json.dumps(aids, indent=6)}")
    
    # Check top-level aids
    eksamen = data.get("eksamen") or {}
    aids = eksamen.get("aids") or {}
    if aids:
        print(f"\n  Top-level aids:")
        print(f"    {json.dumps(aids, indent=6)}")
    
    # Check hjelpemiddeltekst if exists
    hjelpemiddel = data.get("hjelpemiddeltekst") or eksamen.get("hjelpemiddeltekst")
    if hjelpemiddel:
        print(f"\n  Hjelpemiddeltekst: {hjelpemiddel}")
    
    # Check other relevant fields
    print(f"\n  isSebEksamen: {data.get('isSebEksamen')}")
    
    # Look for any text mentioning "papir" or "digital"
    raw_json = json.dumps(data, ensure_ascii=False)
    if 'papir' in raw_json.lower():
        print(f"  ⚠️  Found 'papir' in JSON")
    if 'digital' in raw_json.lower():
        print(f"  ⚠️  Found 'digital' in JSON")

def main():
    print("Checking all two-part exams for paper/digital information...")
    
    for fagkode in TWO_PART_CODES:
        check_exam(fagkode)
        time.sleep(0.5)  # Be polite to the API

if __name__ == "__main__":
    main()
