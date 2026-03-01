import re
import html
import json
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from pathlib import Path

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


def fetch_html(url: str, timeout: int = 20):
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_tags_keep_breaks(s: str) -> str:
    s = re.sub(r"<\s*br\s*/?>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"</\s*(p|li|div|h[1-6])\s*>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    joined = " ".join(lines)
    joined = re.sub(r"\s+", " ", joined).strip()
    return joined


def extract_times(page_text: str):
    t = re.sub(r"\s+", " ", page_text)

    del1 = re.search(r"Del\s*1[^0-9]{0,80}(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})", t, flags=re.IGNORECASE)
    del2 = re.search(r"Del\s*2[^0-9]{0,80}(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})", t, flags=re.IGNORECASE)

    if del1 and del2:
        return del1.group(1), del1.group(2), del2.group(1), del2.group(2)

    if del1 and not del2:
        return del1.group(1), del1.group(2), None, None

    exam = re.search(r"kl\.?\s*(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})", t, flags=re.IGNORECASE)
    if exam:
        return exam.group(1), exam.group(2), None, None

    return None, None, None, None


def extract_hjelpemidler(page_html: str):
    # Try structured HTML section first
    m = re.search(
        r"Hjelpemidler\s+under\s+eksamen</h[1-6]>(.*?)(?:<h[1-6][^>]*>|</section>|Har\s+du\s+spørsmål\s+om\s+din\s+eksamen\?)",
        page_html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if m:
        text = strip_tags_keep_breaks(m.group(1))
        if text:
            return text

    # Fallback: text-window extraction
    full_text = strip_tags_keep_breaks(page_html)
    marker = "Hjelpemidler under eksamen"
    idx = full_text.find(marker)
    if idx == -1:
        return ""

    tail = full_text[idx + len(marker):].strip()
    stop_candidates = [
        "Har du spørsmål om din eksamen?",
        "Tilbake til oversikten",
        "Fant du det du lette etter?",
        "Informasjon om eksamen fra Utdanningsdirektoratet",
    ]
    stop_pos = len(tail)
    for stop in stop_candidates:
        p = tail.find(stop)
        if p != -1 and p < stop_pos:
            stop_pos = p

    text = tail[:stop_pos].strip()
    text = re.sub(r"\s+", " ", text).strip()
    return text


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
        url = f"https://kandidat.udir.no/eksamensinfo/{code}"
        try:
            html_text = fetch_html(url)
            plain_text = strip_tags_keep_breaks(html_text)
            d1s, d1e, d2s, d2e = extract_times(plain_text)
            hjelp = extract_hjelpemidler(html_text)

            entries[code] = {
                "del1_start": d1s,
                "del1_end": d1e,
                "del2_start": d2s,
                "del2_end": d2e,
                "hjelpemidler": hjelp,
            }
        except (HTTPError, URLError, TimeoutError, OSError) as e:
            failures.append((code, str(e)))
            entries[code] = {
                "del1_start": None,
                "del1_end": None,
                "del2_start": None,
                "del2_end": None,
                "hjelpemidler": "",
            }

        if i % 25 == 0 or i == len(codes):
            print(f"Processed {i}/{len(codes)}")
            time.sleep(0.05)

    content = INDEX_PATH.read_text(encoding="utf-8")
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
        for code, err in failures[:100]:
            print(f" - {code}: {err}")


if __name__ == "__main__":
    main()
