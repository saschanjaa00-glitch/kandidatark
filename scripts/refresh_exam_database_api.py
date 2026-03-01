import json
import re
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from pathlib import Path
from datetime import datetime

ROOT = Path(r"c:\Users\sasch\Kandidatark")
INDEX_PATH = ROOT / "index.html"
CODES_PATH = ROOT / "requested_codes.txt"


def load_codes(path: Path):
    text = path.read_text(encoding="utf-8")
    raw = re.findall(r"[A-Z0-9]+(?:-[A-Z0-9]+)?", text.upper())
    seen = set()
    codes = []
    for code in raw:
        if code not in seen:
            seen.add(code)
            codes.append(code)
    return codes


def fetch_json(url: str, timeout: int = 20):
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    })
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def iso_to_time(iso_value):
    if not iso_value:
        return None
    try:
        dt = datetime.fromisoformat(iso_value)
        return dt.strftime("%H:%M")
    except Exception:
        m = re.search(r"T(\d{2}:\d{2})", str(iso_value))
        return m.group(1) if m else None


def build_hjelpemidler(payload):
    eksamen = payload.get("eksamen") or {}
    aids = eksamen.get("aids") or {}

    is_seb = bool(payload.get("isSebEksamen"))
    system = (payload.get("gjennomføringssystem") or "").upper()
    is_sprakfag = bool(aids.get("isSpråkFag"))
    has_open_internet = bool(aids.get("hasOpenInternetAccess"))
    is_paste_disabled = bool(aids.get("isPasteDisabled"))

    ck = (aids.get("ckEditorSetting") or {}).get("navn") or ""
    ck_lower = ck.lower()

    if "automatisk" in ck_lower:
        spellcheck_text = "Denne eksamenen har stavekontroll som kjenner igjen språket du skriver på."
    elif "hovedmål" in ck_lower:
        spellcheck_text = "Denne eksamenen har stavekontroll i ditt hovedmål."
    elif "sidemål" in ck_lower:
        spellcheck_text = "Denne eksamenen har stavekontroll i ditt sidemål."
    elif "ingen" in ck_lower:
        spellcheck_text = "Denne eksamenen har ikke innebygd stavekontroll i oppgaven."
    else:
        spellcheck_text = ""

    if is_seb:
        seb_text = (
            "Det er tillatt å bruke hjelpemidler som er på papir; som bøker, oppslagsverk, notater og liknende. "
            "Du kan også ha tilgang til noen få nettbaserte hjelpemidler."
        )
        return " ".join(part for part in [spellcheck_text, seb_text] if part).strip()

    rules = []
    rules.append("Det er ikke tillatt å kommunisere med andre på nettet eller på andre måter under eksamen.")

    if system == "EPS":
        if has_open_internet:
            rules.append("Du kan fritt bruke internett under eksamen, men ikke kommunisere.")
        else:
            rules.append("Du har tilgang til et begrenset utvalg nettbaserte hjelpemidler, men ikke internett for øvrig.")

    if is_sprakfag:
        rules.append("Det er ikke tillatt å bruke oversettelsesprogram under eksamen.")

    if system == "EPS":
        rules.append("Du kan ikke bruke automatisk tekstgenerator som chatbot eller tilsvarende teknologi.")

    if is_paste_disabled:
        rules.append("Du skal skrive svarene dine direkte inn i nettleseren, og det er ikke tillatt å kladde i et annet program (som Word) for så å klippe og lime inn i besvarelsen.")

    unique_rules = []
    seen = set()
    for rule in rules:
        if rule not in seen:
            seen.add(rule)
            unique_rules.append(rule)

    prefix = "Alle hjelpemidler er lov på eksamen, med følgende unntak:"
    body = " ".join(unique_rules)
    return " ".join(part for part in [spellcheck_text, prefix, body] if part).strip()


def build_times(payload):
    eksamen = payload.get("eksamen") or {}
    deler = eksamen.get("eksamensdeler") or []

    parsed = []
    for d in deler:
        fra = iso_to_time(d.get("fra"))
        til = iso_to_time(d.get("til"))
        if fra and til:
            parsed.append((fra, til, d.get("eksamensdelType") or ""))

    if parsed:
        parsed.sort(key=lambda x: x[0])
        del1 = parsed[0]
        del2 = parsed[1] if len(parsed) > 1 else None
        return del1[0], del1[1], (del2[0] if del2 else None), (del2[1] if del2 else None)

    fra = iso_to_time((eksamen or {}).get("eksamenFromNorwegianTime"))
    til = iso_to_time((eksamen or {}).get("eksamenToNorwegianTime"))
    if fra and til:
        return fra, til, None, None

    return None, None, None, None


def js_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def generate_block(entries):
    lines = []
    lines.append("        const examDatabaseCompact = {")
    for code in sorted(entries.keys()):
        e = entries[code]
        d1s = f"'{e['del1_start']}'" if e['del1_start'] else "null"
        d1e = f"'{e['del1_end']}'" if e['del1_end'] else "null"
        d2s = f"'{e['del2_start']}'" if e['del2_start'] else "null"
        d2e = f"'{e['del2_end']}'" if e['del2_end'] else "null"
        hjelp = f"'{js_string(e['hjelpemidler'])}'"
        lines.append(f"            '{code}': [{d1s}, {d1e}, {d2s}, {d2e}, {hjelp}],")
    lines.append("        };")
    lines.append("")
    lines.append("        function timeToMinutes(timeStr) {")
    lines.append("            if (!timeStr) return null;")
    lines.append("            const [hours, minutes] = timeStr.split(':').map(Number);")
    lines.append("            return (hours * 60) + minutes;")
    lines.append("        }")
    lines.append("")
    lines.append("        function fetchExamInfo(fagkode) {")
    lines.append("            const normalizedFagkode = String(fagkode || '').trim().toUpperCase();")
    lines.append("            const entry = examDatabaseCompact[normalizedFagkode];")
    lines.append("")
    lines.append("            if (entry) {")
    lines.append("                const [del1Start, del1End, del2Start, del2End, hjelpemidler] = entry;")
    lines.append("                return {")
    lines.append("                    fagkode: normalizedFagkode,")
    lines.append("                    del1: del1Start && del1End ? {")
    lines.append("                        start: del1Start,")
    lines.append("                        end: del1End,")
    lines.append("                        startMinutes: timeToMinutes(del1Start),")
    lines.append("                        endMinutes: timeToMinutes(del1End)")
    lines.append("                    } : null,")
    lines.append("                    del2: del2Start && del2End ? {")
    lines.append("                        start: del2Start,")
    lines.append("                        end: del2End,")
    lines.append("                        startMinutes: timeToMinutes(del2Start),")
    lines.append("                        endMinutes: timeToMinutes(del2End)")
    lines.append("                    } : null,")
    lines.append("                    hjelpemidler: hjelpemidler || '',")
    lines.append("                    notInDatabase: false,")
    lines.append("                    sourceUrl: `https://kandidat.udir.no/eksamensinfo/${normalizedFagkode}`")
    lines.append("                };")
    lines.append("            }")
    lines.append("")
    lines.append("            return {")
    lines.append("                fagkode: normalizedFagkode || String(fagkode || '').trim(),")
    lines.append("                del1: null,")
    lines.append("                del2: null,")
    lines.append("                hjelpemidler: '',")
    lines.append("                notInDatabase: true,")
    lines.append("                sourceUrl: `https://kandidat.udir.no/eksamensinfo/${normalizedFagkode || String(fagkode || '').trim()}`")
    lines.append("            };")
    lines.append("        }")
    lines.append("")
    return "\n".join(lines)


def main():
    codes = load_codes(CODES_PATH)
    print(f"Codes requested: {len(codes)}")

    entries = {}
    failures = []

    for i, code in enumerate(codes, start=1):
        url = f"https://kandidat.udir.no/api/eksamen-info/{code}"
        try:
            payload = fetch_json(url)
            d1s, d1e, d2s, d2e = build_times(payload)
            hjelp = build_hjelpemidler(payload)

            entries[code] = {
                "del1_start": d1s,
                "del1_end": d1e,
                "del2_start": d2s,
                "del2_end": d2e,
                "hjelpemidler": hjelp,
            }
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
            failures.append((code, str(e)))
            entries[code] = {
                "del1_start": None,
                "del1_end": None,
                "del2_start": None,
                "del2_end": None,
                "hjelpemidler": "",
            }

        if i % 50 == 0 or i == len(codes):
            print(f"Processed {i}/{len(codes)}")
            time.sleep(0.03)

    content = INDEX_PATH.read_text(encoding="utf-8")
    start_marker = "        const examDatabaseCompact = {"
    if start_marker not in content:
        start_marker = "        const examDatabase = {"
    end_marker = "        function generateTimeHelpContent"

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        raise RuntimeError("Could not find exam database block markers in index.html")

    new_block = generate_block(entries)
    updated = content[:start_idx] + new_block + content[end_idx:]
    INDEX_PATH.write_text(updated, encoding="utf-8")

    print(f"Updated index.html with {len(entries)} entries")
    print(f"Failures: {len(failures)}")
    if failures:
        print("Failed codes:")
        for code, err in failures[:200]:
            print(f" - {code}: {err}")


if __name__ == "__main__":
    main()
