# Instructions for the agent: publish NOR Studio to GitHub

You are setting up a public GitHub repository for **NOR Studio**, a single-file web app (`index.html`) for PS5 NOR editing, CH341A programming and UART diagnostics. Every file you need is in this folder. Do **not** change `index.html` unless a step below says to.

## 0. Ask the owner first (if not already given)

- GitHub username or organization → `OWNER`
- Repository name → `REPO` (suggested: `nor-studio`)
- Public or private (GitHub Pages on a private repo needs a paid plan)

## 1. Prepare the files

1. Replace every `OWNER` and `REPO` placeholder in `README.md` with the real values:
   ```bash
   sed -i 's#OWNER.github.io/REPO#<owner>.github.io/<repo>#g' README.md
   grep -n "OWNER\|REPO" README.md   # must return nothing
   ```
   On macOS use `sed -i ''`.
2. Make sure these files are present, and **nothing else** is added:
   ```
   index.html  README.md  LICENSE  NOTICE.md  CHANGELOG.md  .gitignore
   docs/banner.svg  docs/HARDWARE_GUIDE.md  docs/screenshots/*.png  docs/social-preview.png
   docs/boards/*.jpg  docs/NOR-Studio-Manual*.pdf  docs/manual-src/**
   i18n/pt.json  i18n/es.json  i18n/es-419.json  i18n/zh.json  i18n/zh-TW.json  tools/build_i18n.py
   .github/workflows/pages.yml  .github/ISSUE_TEMPLATE/*.md
   ```
   `AGENT_INSTRUCTIONS.md` (this file) may be left out of the repo.
   The user manual **must** be committed in all six languages: `docs/NOR-Studio-Manual.pdf` (English) and `docs/NOR-Studio-Manual.pt-BR.pdf`, `.es-419.pdf`, `.es.pdf`, `.zh-CN.pdf`, `.zh-TW.pdf`. These six are the only PDFs that belong in the repo.
3. **Never commit** NOR dumps (`*.bin`), backups, boardview files (`*.pcb`) or Sony service manual PDFs. They contain console-specific data or confidential, copyrighted material. `.gitignore` already blocks them. Check with `git status` before committing.

## 2. Create the repository and push

Using the GitHub CLI (`gh auth status` must show a logged-in account):

```bash
cd <this folder>
git init -b main
git add .
git status            # confirm no .bin / .pcb files, and no PDF except the six docs/NOR-Studio-Manual*.pdf
git commit -m "NOR Studio v1.2.0"
gh repo create OWNER/REPO --public --source=. --remote=origin --push \
  --description "PS5 NOR editor, CH341A programmer & UART diagnostics. Runs in your browser." \
  --homepage "https://OWNER.github.io/REPO/"
gh repo edit OWNER/REPO --add-topic ps5 --add-topic nor --add-topic uart --add-topic ch341a \
  --add-topic webusb --add-topic web-serial --add-topic console-repair --add-topic playstation
```

## 3. Turn on GitHub Pages (GitHub Actions source)

```bash
gh api -X POST repos/OWNER/REPO/pages -f build_type=workflow || \
gh api -X PUT  repos/OWNER/REPO/pages -f build_type=workflow
gh workflow run pages.yml -R OWNER/REPO
gh run watch -R OWNER/REPO        # wait for the deploy to finish
```

Then confirm `https://OWNER.github.io/REPO/` loads and shows the NOR Studio header. Hosting on HTTPS matters: WebUSB and Web Serial only work in secure contexts.

## 4. Create the first release

```bash
cp index.html nor-studio.html
gh release create v1.2.0 nor-studio.html docs/NOR-Studio-Manual*.pdf -R OWNER/REPO \
  --title "NOR Studio v1.2.0" --notes-file CHANGELOG.md
rm nor-studio.html
```

## 4b. Social preview image

GitHub has no API for this, so tell the owner to do it by hand (or do it yourself if you have browser access to their account):
Repository → **Settings** → **General** → **Social preview** → **Edit** → **Upload an image** → choose `docs/social-preview.png` (1280×640).

## 5. Final checks (report the results to the owner)

- [ ] README renders on GitHub with the banner, badges and all screenshots (no broken images).
- [ ] The **manual PDF** badge and the "user manual" link in Getting started open `docs/NOR-Studio-Manual.pdf` (GitHub shows it in its PDF viewer). The language links under it open the five translated manuals. The release has seven assets: `nor-studio.html` and the six `NOR-Studio-Manual*.pdf` files.
- [ ] "Open the app" badge links to the live Pages URL.
- [ ] The live page opens. **Programmer → Demo mode → Read chip** works, and **UART → Demo mode → Read error codes** shows decoded codes.
- [ ] The Help tab and footer show the credits: *based on PS5 NOR Modifier by TheCod3r (GPL-2.0), rebuilt with AI assistance, improvements/features/ideas by The Goat Tech*.
- [ ] `LICENSE` is GPL-2.0 and `NOTICE.md` is present.
- [ ] Social preview set to `docs/social-preview.png` (or the owner was told how to set it).
- [ ] No `.bin`, `.pcb` or service-manual PDFs are in the repo. `git ls-files | grep -Ei '\.(bin|pcb|pdf)$'` must return only the six `docs/NOR-Studio-Manual*.pdf` files.

Send the owner: the repo URL, the Pages URL and the release URL.

## Notes

- License: the project contains code and logic derived from PS5 NOR Modifier (GPL-2.0), so it must stay **GPL-2.0**. Keep `LICENSE` and the credits intact.
- To update the app later, replace `index.html`, add a line to `CHANGELOG.md`, commit and push. Pages redeploys automatically.
- Translations live in `i18n/<lang>.json` and are built into `index.html`. After editing one, run `python tools/build_i18n.py` from the repo root and commit both the JSON and `index.html`. Never edit the `<script id="i18n-data">` block in `index.html` by hand.
- To update the manual: edit `docs/manual-src/manual.html` (English). Translations are in `docs/manual-src/i18n/<lang>.json`, which map each English text block to its translation; change the same block there too, or the build stops and names the blocks with no translation. Screenshots are in `docs/manual-src/jpg/` (English) and `docs/manual-src/jpg/<lang>/` (the app in that language). Run `pip install playwright pypdf beautifulsoup4 && playwright install chromium` once, then `python docs/manual-src/build_manual.py` (all six) or e.g. `python docs/manual-src/build_manual.py en zh-CN`. Install Inter and Noto Sans CJK SC/TC first for the same look. Each language should come out at 17 pages like the English one. Commit the source and the PDFs. The manual's screenshots use demo data only: never put a real console's serial or MACs in it.
