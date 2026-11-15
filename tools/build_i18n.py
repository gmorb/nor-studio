"""Put the translations from i18n/*.json into index.html.

Each JSON file maps the English text (whitespace collapsed; blocks with inline markup use their inner HTML)
to its translation. Keys with {name} slots are patterns for text that contains numbers or file names.
Run from the repo root after editing a translation:  python tools/build_i18n.py [index.html]
Spanish comes in two files: es-419.json (Latin America) and es.json (Spain).
To add a language: copy i18n/es.json to i18n/<code>.json, translate the values, add an <option> for it in
the #langSel menu in index.html, and add the code to the list in setLang().
"""
import json, pathlib, re, sys
root = pathlib.Path(__file__).resolve().parent.parent
html = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else root / "index.html"
data = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / "i18n").glob("*.json"))}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
s = html.read_text(encoding="utf-8")
new, n = re.subn(r'<script id="i18n-data">.*?</script>', lambda m: f'<script id="i18n-data">window.I18N_DATA={blob};</script>', s, count=1, flags=re.S)
if not n: sys.exit('No <script id="i18n-data"> block found in ' + str(html))
html.write_text(new, encoding="utf-8")
print(f"{html.name}: " + ", ".join(f"{k} {len(v)} strings" for k, v in data.items()))
