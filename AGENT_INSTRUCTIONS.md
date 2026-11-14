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
   docs/banner.svg  docs/HARDWARE_GUIDE.md  docs/screenshots/*.png
   .github/workflows/pages.yml  .github/ISSUE_TEMPLATE/*.md
   ```
   `AGENT_INSTRUCTIONS.md` (this file) may be left out of the repo.
3. **Never commit** NOR dumps (`*.bin`), backups, boardview files (`*.pcb`) or Sony service manual PDFs. They contain console-specific data or confidential, copyrighted material. `.gitignore` already blocks them. Check with `git status` before committing.

## 2. Create the repository and push

Using the GitHub CLI (`gh auth status` must show a logged-in account):

```bash
cd <this folder>
git init -b main
git add .
git status            # confirm no .bin / .pcb / .pdf files are staged
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
gh release create v1.2.0 nor-studio.html -R OWNER/REPO \
  --title "NOR Studio v1.2.0" --notes-file CHANGELOG.md
rm nor-studio.html
```

## 5. Final checks (report the results to the owner)

- [ ] README renders on GitHub with the banner, badges and all 5 screenshots (no broken images).
- [ ] "Open the app" badge links to the live Pages URL.
- [ ] The live page opens. **Programmer → Demo mode → Read chip** works, and **UART → Demo mode → Read error codes** shows decoded codes.
- [ ] The Help tab and footer show the credits: *based on PS5 NOR Modifier by TheCod3r (GPL-2.0), rebuilt with AI assistance, improvements/features/ideas by The Goat Tech*.
- [ ] `LICENSE` is GPL-2.0 and `NOTICE.md` is present.
- [ ] No `.bin`, `.pcb` or service-manual PDFs are in the repo (`git ls-files | grep -Ei '\.(bin|pcb|pdf)$'` returns nothing).

Send the owner: the repo URL, the Pages URL and the release URL.

## Notes

- License: the project contains code and logic derived from PS5 NOR Modifier (GPL-2.0), so it must stay **GPL-2.0**. Keep `LICENSE` and the credits intact.
- To update the app later, replace `index.html`, add a line to `CHANGELOG.md`, commit and push. Pages redeploys automatically.
