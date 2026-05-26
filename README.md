# whcc_stats

Warsaw Hussars Cricket Club statistics - Interactive website generator from PDF scorecards.

**Live Stats**: [https://ostyk.github.io/whcc_stats/](https://ostyk.github.io/whcc_stats/) 🏏

## Overview

This tool parses manually exported PDF scorecards from CricHeroes and generates a beautiful, interactive statistics website that's automatically hosted on GitHub Pages.

## Features

- 📊 **Interactive Dashboard** - Modern web interface with sortable tables
- 🏆 **Leaderboards** - Top run scorers, best averages, highest strike rates, and more
- 🎯 **Bowling Stats** - Wickets, economy rates, and best figures
- 🔍 **Player Search** - Find and filter individual player statistics
- 📱 **Mobile Friendly** - Responsive design works on all devices
- 🆓 **Free Hosting** - Served via GitHub Pages at no cost

## Setup

1. Create a virtual environment with UV:
```bash
uv venv
```

2. Install dependencies:
```bash
uv pip install pdfplumber pandas
```

## Usage

### Generate the Website

1. Export scorecards from CricHeroes as PDF files
2. Place them in the `scorecards/` folder
3. Run the generator:

```bash
python generate_website.py
```

This will:
- Parse all PDF scorecards in the `scorecards/` folder
- Extract batting and bowling records
- Generate a complete website in the `docs/` folder:
  - `index.html` - Main dashboard
  - `style.css` - Styling
  - `script.js` - Interactive features
  - `stats.json` - Statistics data

### Deploy to GitHub Pages

1. Commit and push the changes:
```bash
git add docs/
git commit -m "Update cricket statistics"
git push
```

2. Enable GitHub Pages (first time only):
   - Go to your repository Settings > Pages
   - Source: **Deploy from a branch**
   - Branch: **main**, folder: **/docs**
   - Save

3. Your site will be live at: `https://ostyk.github.io/whcc_stats/`

### Update with New Scorecards

When new matches are played:
1. Download new scorecards as PDF
2. Add them to `scorecards/` folder
3. Run `python generate_website.py`
4. Commit and push
5. Website auto-updates!

## What Gets Generated

### Batting Statistics
- Most runs in a season
- Highest individual scores
- Best batting averages
- Highest strike rates
- Most fours and sixes
- Complete season stats for all players

### Bowling Statistics
- Top wicket takers
- Best bowling figures
- Best economy rates
- Best bowling averages
- Complete bowling records

### Interactive Features
- Sortable tables
- Player search functionality
- Tabbed navigation
- Responsive mobile design
- Real-time filtering

## Development

### Analyze Data (Jupyter Notebook)

For custom analysis, use the notebook:
```bash
jupyter notebook cric_stats.ipynb
```

The notebook includes:
- Data parsing examples
- Player-specific analysis
- Visualization
- MVP score calculations

## Project Structure

```
whcc_stats/
├── scorecards/          # PDF scorecards (input)
├── docs/                # Generated website (output)
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── stats.json
├── generate_website.py  # Main generator script
├── cric_stats.ipynb    # Analysis notebook
└── README.md
```

## Team Information

- **Team**: Warsaw Hussars
- **Team ID**: 2444976
- **CricHeroes Profile**: https://cricheroes.com/team-profile/2444976/warsaw-hussars/
