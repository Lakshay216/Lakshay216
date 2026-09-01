# Finish and publish your animated GitHub profile

The project already includes the animated portrait panel, animated info card,
contribution heatmap renderer, daily GitHub Action, and profile README layout.

## 1. Add your real details

Your username is already set to `Lakshay216`. Edit any card text you want in
`profile.json`.

## 2. Add your portrait

Use a clear, front-facing JPG or PNG with even lighting. Then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements-portrait.txt
python scripts/prep_photo.py /full/path/to/your-photo.jpg
python scripts/make_ascii_svg.py
```

Without a photo, `profile-ascii.svg` intentionally displays a placeholder.

## 3. Generate the real contribution graph

```bash
pip install -r scripts/requirements.txt
python scripts/fetch_contributions.py
python scripts/render_heatmap_svg.py
python scripts/make_info_card.py
```

## 4. Publish

Create a public repository whose name exactly matches your GitHub username.
Copy everything in this folder into it, commit, and push to the `main` branch.
On GitHub, open **Actions → Update profile art → Run workflow** once. The
workflow will then refresh the graph every day at about 06:17 UTC.

If GitHub Actions cannot push, open **Settings → Actions → General → Workflow
permissions**, select **Read and write permissions**, and save.
