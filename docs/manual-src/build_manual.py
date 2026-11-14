"""Rebuild docs/NOR-Studio-Manual.pdf from manual.html.

Needs: pip install playwright pypdf && playwright install chromium
(Install the Inter font for the intended look; otherwise a fallback sans-serif is used.)
Run from anywhere:  python docs/manual-src/build_manual.py
"""
import asyncio, pathlib
from playwright.async_api import async_playwright
from pypdf import PdfReader, PdfWriter

HERE = pathlib.Path(__file__).resolve().parent
SRC = (HERE / "manual.html").as_uri()
OUT = HERE.parent / "NOR-Studio-Manual.pdf"
FOOT = ('<div style="width:100%;font:8px Inter,sans-serif;color:#7a869c;padding:0 0.85in;'
        'display:flex;justify-content:space-between"><span>NOR Studio · User manual</span>'
        '<span class="pageNumber"></span></div>')

async def render():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        # cover: full bleed, no footer
        await pg.goto(SRC); await pg.wait_for_timeout(800)
        await pg.add_style_tag(content="section{display:none!important} @page{margin:0}")
        await pg.pdf(path=str(HERE / "_cover.pdf"), width="8.5in", height="11in", print_background=True,
                     margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        # body: page margins from the CSS, page numbers in the footer
        await pg.goto(SRC); await pg.wait_for_timeout(800)
        await pg.add_style_tag(content=".cover{display:none!important}")
        await pg.pdf(path=str(HERE / "_body.pdf"), format="Letter", print_background=True, prefer_css_page_size=True,
                     display_header_footer=True, header_template="<div></div>", footer_template=FOOT)
        await b.close()

asyncio.run(render())
w = PdfWriter()
for part in ("_cover.pdf", "_body.pdf"):
    for page in PdfReader(str(HERE / part)).pages: w.add_page(page)
    (HERE / part).unlink()
w.add_metadata({"/Title": "NOR Studio User Manual", "/Author": "The Goat Tech"})
w.write(str(OUT)); print("Wrote", OUT)
