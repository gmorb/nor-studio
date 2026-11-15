"""Rebuild the NOR Studio manual PDFs from manual.html.

English is manual.html as written. Each file in i18n/ (pt-BR, es-419, es, zh-CN, zh-TW)
maps every English text block to its translation; the build swaps them in, points the
screenshots at jpg/<lang>/ and writes docs/NOR-Studio-Manual.<lang>.pdf.

Needs: pip install playwright pypdf beautifulsoup4 && playwright install chromium
Fonts: Inter for Latin text, Noto Sans CJK SC/TC for Chinese (fallbacks are used otherwise).
Run:   python docs/manual-src/build_manual.py            (all languages)
       python docs/manual-src/build_manual.py en zh-CN   (only these)

When you change English text in manual.html, update the same block (the key is the
block's inner HTML) in every i18n/*.json, or the build stops and lists the blocks that
have no translation. Blocks that stay the same in every language (pin names, codes) are
listed with themselves as the translation.
"""
import asyncio, json, pathlib, sys
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pypdf import PdfReader, PdfWriter

HERE = pathlib.Path(__file__).resolve().parent
DOCS = HERE.parent
LANGS = ["en", "pt-BR", "es-419", "es", "zh-CN", "zh-TW"]
BLOCK = ["h1", "h2", "h3", "h4", "p", "li", "td", "th", "figcaption", "title"]
# Portuguese and Spanish run about 20% longer than English, so tighten the type a little
# to keep every chapter on the same pages as the English manual.
COMPACT = ("body{font-size:9.6pt;line-height:1.47} .lede{font-size:10.4pt;margin-bottom:12px}"
           " h3{margin:15px 0 5px} p{margin:0 0 7px} li{margin-bottom:3px} figure{margin:8px 0 11px}"
           " figure.mid img{width:66%} figure img[style*='56%']{width:47%!important}"
           " figure img[style*='50%']{width:42%!important} td,th{padding-top:4px;padding-bottom:4px}"
           " table{font-size:8.9pt} .note{padding:8px 12px;margin:9px 0} .steps>li{margin-bottom:6px}")
EXTRA_CSS = {"pt-BR": COMPACT, "es-419": COMPACT, "es": COMPACT}
FONTS = {
    "zh-CN": "Inter, 'Noto Sans CJK SC', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif",
    "zh-TW": "Inter, 'Noto Sans CJK TC', 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', sans-serif",
}

def blocks(soup):
    """The text blocks that get translated: leaf block elements, plus TOC links and cover/note divs."""
    for el in soup.find_all(BLOCK + ["div", "a"]):
        if el.name == "div" and not set(el.get("class") or []) & {"sub", "meta", "ver", "note"}: continue
        if el.name == "a" and "toc" not in (el.parent.get("class") or []): continue
        if el.find(BLOCK + ["div"]): continue
        html = el.decode_contents().strip()
        if html and any(c.isalpha() for c in el.get_text()): yield el, html

def translate(lang):
    """Write _manual.<lang>.html next to manual.html and return (path, footer text, title)."""
    soup = BeautifulSoup((HERE / "manual.html").read_text(encoding="utf-8"), "html.parser")
    if lang == "en":
        return HERE / "manual.html", "NOR Studio · User manual", "NOR Studio User Manual"
    data = json.loads((HERE / "i18n" / f"{lang}.json").read_text(encoding="utf-8"))
    seg, missing = data["segments"], []
    for el, html in blocks(soup):
        if html in seg:
            el.clear(); el.append(BeautifulSoup(seg[html], "html.parser"))
        else:
            missing.append(html[:90])
    if missing:
        sys.exit(f"{lang}: {len(missing)} blocks have no translation, e.g.\n  " + "\n  ".join(missing[:8]))
    soup.html["lang"] = lang
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src.startswith("jpg/") and (HERE / "jpg" / lang / src[4:]).exists():
            img["src"] = f"jpg/{lang}/{src[4:]}"
    if lang in FONTS:
        style = soup.new_tag("style"); style.string = f"body{{font-family:{FONTS[lang]}}}"
        soup.head.append(style)
    if lang in EXTRA_CSS:
        style = soup.new_tag("style"); style.string = EXTRA_CSS[lang]
        soup.head.append(style)
    out = HERE / f"_manual.{lang}.html"
    out.write_text(str(soup), encoding="utf-8")
    return out, data["__footer"], data["__title"]

def footer(text, lang):
    font = FONTS.get(lang, "Inter, sans-serif")
    return (f'<div style="width:100%;font-size:8px;font-family:{font};color:#7a869c;padding:0 0.85in;'
            f'display:flex;justify-content:space-between"><span>{text}</span><span class="pageNumber"></span></div>')

async def render(lang):
    src, foot, title = translate(lang)
    name = "NOR-Studio-Manual.pdf" if lang == "en" else f"NOR-Studio-Manual.{lang}.pdf"
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        # cover: full bleed, no footer
        await pg.goto(src.as_uri()); await pg.wait_for_timeout(800)
        await pg.add_style_tag(content="section{display:none!important} @page{margin:0}")
        await pg.pdf(path=str(HERE / "_cover.pdf"), width="8.5in", height="11in", print_background=True,
                     margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        # body: page margins from the CSS, page numbers in the footer
        await pg.goto(src.as_uri()); await pg.wait_for_timeout(800)
        await pg.add_style_tag(content=".cover{display:none!important}")
        await pg.pdf(path=str(HERE / "_body.pdf"), format="Letter", print_background=True, prefer_css_page_size=True,
                     display_header_footer=True, header_template="<div></div>", footer_template=footer(foot, lang))
        await b.close()
    if src.name.startswith("_"): src.unlink()
    w = PdfWriter()
    for part in ("_cover.pdf", "_body.pdf"):
        for page in PdfReader(str(HERE / part)).pages: w.add_page(page)
        (HERE / part).unlink()
    w.add_metadata({"/Title": title, "/Author": "The Goat Tech", "/Lang": lang})
    w.write(str(DOCS / name)); print("Wrote", DOCS / name)

for lang in (sys.argv[1:] or LANGS):
    if lang not in LANGS: sys.exit(f"Unknown language {lang}; pick from {', '.join(LANGS)}")
    asyncio.run(render(lang))
