from pathlib import Path
import re

root = Path(r"c:\Users\sasch\Kandidatark")
index_path = root / "index.html"
data_dir = root / "data"
data_path = data_dir / "examDatabaseCompact.js"

content = index_path.read_text(encoding="utf-8")

pattern = re.compile(r"\n\s*const examDatabaseCompact = \{[\s\S]*?\n\s*\};\n", re.MULTILINE)
match = pattern.search(content)
if not match:
    raise RuntimeError("Could not find examDatabaseCompact object block in index.html")

obj_block = match.group(0)
obj_decl = obj_block.strip()
obj_js = obj_decl.replace("const examDatabaseCompact =", "window.examDatabaseCompact =", 1) + "\n"

data_dir.mkdir(parents=True, exist_ok=True)
data_path.write_text(obj_js, encoding="utf-8")

# Replace inline object with window-backed assignment
replacement = "\n        const examDatabaseCompact = window.examDatabaseCompact || {};\n"
content = content[:match.start()] + replacement + content[match.end():]

# Ensure external data script is loaded before inline app script
inject_marker = "    <script>\n        let currentData = null;"
if inject_marker in content and 'src="data/examDatabaseCompact.js"' not in content:
    content = content.replace(
        inject_marker,
        "    <script src=\"data/examDatabaseCompact.js\"></script>\n\n" + inject_marker,
        1,
    )

index_path.write_text(content, encoding="utf-8")

print(f"Wrote: {data_path}")
print("Updated: index.html")
