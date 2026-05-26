# GitHub Pages Setup Instructions

## First Time Setup

1. **Push the code to GitHub:**
```bash
git add .
git commit -m "Add cricket statistics website"
git push origin main
```

2. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Click on **Settings** (top right)
   - Scroll down to **Pages** (left sidebar)
   - Under "Build and deployment":
       - Source: **GitHub Actions**
   - Click **Save**

3. **Wait a few minutes**, then visit:
   - https://ostyk.github.io/whcc_stats/

## Updating Statistics

When you have new match scorecards:

1. **Add new PDFs to scorecards/ folder**

2. **Regenerate the website:**
```bash
python generate_website.py
```

3. **Push updates:**
```bash
git add docs/
git commit -m "Update statistics - [date/match info]"
git push
```

4. **Website auto-updates** in 1-2 minutes!

## Testing Locally

Before pushing, test the website locally:

```bash
# Option 1: Open directly
open docs/index.html
# or
xdg-open docs/index.html

# Option 2: Use a local server (recommended for full functionality)
cd docs
python3 -m http.server 8000
# Then visit: http://localhost:8000
```

## Troubleshooting

**Website not updating?**
- Check GitHub Actions tab for deployment status
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Wait a few minutes after pushing
- If a run fails with an action download/codeload error, re-run the failed workflow run (these are often transient).

**Data not showing?**
- Check docs/stats.json exists and has content
- Open browser console (F12) for JavaScript errors
- Verify JSON is valid: `python -m json.tool docs/stats.json`

**404 Error?**
- Verify GitHub Pages is enabled in repository settings
- Check Pages source is set to **GitHub Actions**
- Ensure docs/index.html exists in the main branch
