#!/usr/bin/env python3
"""
Warsaw Hussars Cricket Club - Static Website Stats Generator

This script parses PDF scorecards and generates a static HTML website
that can be hosted on GitHub Pages.
"""

import pdfplumber
import re
import pandas as pd
from pathlib import Path
from datetime import datetime
import json


class ScorecardParser:
    """Parse PDF scorecards and extract cricket statistics."""
    
    def __init__(self, scorecards_folder="scorecards"):
        self.scorecards_folder = Path(scorecards_folder)
        self.batting_records = []
        self.bowling_records = []
        
    def parse_all_scorecards(self):
        """Parse all PDF scorecards in the folder."""
        pdf_files = list(self.scorecards_folder.glob("*.pdf"))
        
        if not pdf_files:
            print(f"⚠️ No PDF files found in {self.scorecards_folder}")
            return
        
        print(f"Found {len(pdf_files)} scorecard(s) to process...")
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            self.parse_scorecard(pdf_file)
        
        print(f"\n✓ Parsed {len(self.batting_records)} batting records")
        print(f"✓ Parsed {len(self.bowling_records)} bowling records")
    
    def parse_scorecard(self, pdf_file):
        """Parse a single PDF scorecard."""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                text = "\n".join(page.extract_text() for page in pdf.pages)
                
                match_datetime = self.extract_match_date(text)
                self.extract_batting_records(text, pdf_file.name, match_datetime)
                self.extract_bowling_records(text, pdf_file.name, match_datetime)
                
        except Exception as e:
            print(f"  ✗ Error parsing {pdf_file.name}: {e}")
    
    def extract_match_date(self, text):
        """Extract match date from scorecard text."""
        date_match = re.search(r"Date\s+(\d{4}-\d{2}-\d{2}),\s+([\d:]+\s+[APM]+ UTC)", text)
        if date_match:
            match_date_str = date_match.group(1)
            try:
                return pd.to_datetime(match_date_str)
            except:
                return None
        return None
    
    def extract_batting_records(self, text, filename, match_datetime):
        """Extract batting records for Warsaw Hussars."""
        headers = list(re.finditer(
            r"(Warsaw Hussars)\s+\d+/\d+d?\s+\([\d.]+\s*Ov\)\s+\((\d+(?:st|nd))\s+Innings\)",
            text
        ))
        
        for i, hdr in enumerate(headers):
            team_name = hdr.group(1)
            innings_label = hdr.group(2)
            
            start = hdr.start()
            end = headers[i+1].start() if i + 1 < len(headers) else len(text)
            innings_text = text[start:end]
            
            stop_match = re.search(r"Extras:|Total:", innings_text)
            if stop_match:
                innings_text = innings_text[:stop_match.start()]
            
            for line in innings_text.splitlines():
                line = line.strip()
                
                if re.match(r".+\s+\d+/\d+d?\s+\([\d.]+\s*Ov\)\s+\(\d+(?:st|nd)\s+Innings\)", line) and "Warsaw Hussars" not in line:
                    break
                
                pattern = re.compile(
                    r"^(\d+)\s+"
                    r"([A-Za-z\s&'.()'-]+?)\s+"
                    r"\(.*?\)\s+"
                    r"(.+?)\s+"
                    r"(\d+)\s+"
                    r"(\d+)\s+"
                    r"(\d+)\s+"
                    r"(\d+)\s+"
                    r"(\d+)\s+"
                    r"([\d.]+)$"
                )
                
                m = pattern.match(line)
                if m:
                    pos, name, status, runs, balls, mins, fours, sixes, sr = m.groups()
                    
                    self.batting_records.append({
                        "file": filename,
                        "team": team_name,
                        "innings": innings_label,
                        "batsman": name.strip(),
                        "status": status.strip(),
                        "runs": int(runs),
                        "balls": int(balls),
                        "fours": int(fours),
                        "sixes": int(sixes),
                        "sr": float(sr),
                        "position": int(pos),
                        "match_date": match_datetime.isoformat() if match_datetime else None
                    })
    
    def extract_bowling_records(self, text, filename, match_datetime):
        """Extract bowling records for Warsaw Hussars."""
        all_innings = list(re.finditer(
            r"(.+?)\s+\d+/\d+d?\s+\([\d.]+\s*Ov\)\s+\((\d+(?:st|nd))\s+Innings\)",
            text
        ))
        
        for i, hdr in enumerate(all_innings):
            batting_team = hdr.group(1).strip()
            
            if "Warsaw Hussars" in batting_team:
                continue
            
            start = hdr.start()
            end = all_innings[i+1].start() if i + 1 < len(all_innings) else len(text)
            innings_text = text[start:end]
            
            bowling_match = re.search(r"Bowling\s+O\s+M\s+R\s+W\s+Econ", innings_text)
            if not bowling_match:
                continue
            
            bowling_section = innings_text[bowling_match.end():]
            
            stop_match = re.search(r"(Fall of wickets|Extras:|Total:)", bowling_section)
            if stop_match:
                bowling_section = bowling_section[:stop_match.start()]
            
            for line in bowling_section.splitlines():
                line = line.strip()
                
                bowling_pattern = re.compile(
                    r"^(\d+)\s+"
                    r"([A-Za-z\s&'.()'-]+?)\s+"
                    r"\(.*?\)\s+"
                    r"([\d.]+)\s+"
                    r"(\d+)\s+"
                    r"(\d+)\s+"
                    r"(\d+)\s+"
                    r"([\d.]+)$"
                )
                
                m = bowling_pattern.match(line)
                if m:
                    pos, name, overs, maidens, runs, wickets, econ = m.groups()
                    
                    overs_float = float(overs)
                    complete_overs = int(overs_float)
                    partial_balls = int((overs_float - complete_overs) * 10)
                    balls = complete_overs * 6 + partial_balls
                    
                    self.bowling_records.append({
                        "file": filename,
                        "bowler": name.strip(),
                        "overs": float(overs),
                        "maidens": int(maidens),
                        "runs": int(runs),
                        "wickets": int(wickets),
                        "economy": float(econ),
                        "balls": balls,
                        "match_date": match_datetime.isoformat() if match_datetime else None
                    })
    
    def get_batting_dataframe(self):
        """Get batting records as DataFrame."""
        if not self.batting_records:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.batting_records)
        df["match_date"] = pd.to_datetime(df["match_date"])
        df = df.sort_values(by="match_date")
        df["out"] = df["status"].apply(lambda s: 0 if "not out" in s.lower() else 1)
        df["is_duck"] = (df["runs"] == 0) & (df["out"] == 1)
        return df
    
    def get_bowling_dataframe(self):
        """Get bowling records as DataFrame."""
        if not self.bowling_records:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.bowling_records)
        df["match_date"] = pd.to_datetime(df["match_date"])
        df = df.sort_values(by="match_date")
        return df


class WebsiteGenerator:
    """Generate static HTML website with statistics."""
    
    def __init__(self, batting_df=None, bowling_df=None, stats_by_year=None):
        # Support both old single-year and new multi-year format
        if stats_by_year is not None:
            self.stats_by_year = stats_by_year
            self.multi_year = True
        else:
            # Legacy single-year format
            self.batting_df = batting_df
            self.bowling_df = bowling_df
            self.multi_year = False
        self.output_dir = Path("docs")  # GitHub Pages serves from docs/ folder
        
    def generate_website(self):
        """Generate complete website."""
        print(f"\nGenerating static website...")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        if self.multi_year:
            # Generate statistics for each year
            all_stats = {}
            for year, data in self.stats_by_year.items():
                print(f"  Generating stats for {year}...")
                stats_data = self.generate_stats_data(data['batting_df'], data['bowling_df'])
                all_stats[year] = stats_data
            
            # Save combined data
            with open(self.output_dir / "stats.json", "w") as f:
                json.dump(all_stats, f, indent=2)
        else:
            # Legacy single-year
            stats_data = self.generate_stats_data(self.batting_df, self.bowling_df)
            with open(self.output_dir / "stats.json", "w") as f:
                json.dump(stats_data, f, indent=2)
        
        # Generate HTML
        self.generate_html()
        
        # Generate CSS
        self.generate_css()
        
        # Generate JavaScript
        self.generate_js()
        
        print(f"✓ Website generated in {self.output_dir}/")
        print(f"  - index.html")
        print(f"  - style.css")
        print(f"  - script.js")
        print(f"  - stats.json")
    
    def generate_stats_data(self, batting_df, bowling_df):
        """Generate comprehensive statistics data."""
        stats = {
            "last_updated": datetime.now().isoformat(),
            "summary": {},
            "batting": {},
            "bowling": {}
        }
        
        if not batting_df.empty:
            # Overall summary
            stats["summary"] = {
                "total_matches": int(batting_df['file'].nunique()),
                "total_innings": len(batting_df),
                "total_runs": int(batting_df['runs'].sum()),
                "total_players": int(batting_df['batsman'].nunique()),
                "date_range": {
                    "start": batting_df['match_date'].min().strftime("%Y-%m-%d"),
                    "end": batting_df['match_date'].max().strftime("%Y-%m-%d")
                }
            }
            
            # Batting statistics
            season_stats = batting_df.groupby('batsman').agg({
                'runs': 'sum',
                'balls': 'sum',
                'fours': 'sum',
                'sixes': 'sum',
                'out': 'sum',
                'is_duck': 'sum',
                'file': 'nunique'
            }).reset_index()
            
            season_stats['sr'] = season_stats.apply(
                lambda row: round(row['runs'] / row['balls'] * 100, 2) if row['balls'] > 0 else 0,
                axis=1
            )
            # Calculate average, handling division by zero (no outs = use total runs)
            season_stats['average'] = season_stats.apply(
                lambda row: round(row['runs'] / row['out'], 2) if row['out'] > 0 else round(row['runs'], 2),
                axis=1
            )
            season_stats['innings'] = season_stats['file']
            
            # Replace any remaining NaN or Infinity with 0
            season_stats = season_stats.replace([float('inf'), float('-inf')], 0).fillna(0)
            
            # Top players
            top_run_scorers = season_stats.nlargest(10, 'runs')[['batsman', 'runs', 'innings', 'average', 'sr']].to_dict('records')
            highest_scores = batting_df.nlargest(10, 'runs')[['batsman', 'runs', 'balls', 'sr']].to_dict('records')
            best_averages = season_stats[season_stats['out'] > 0].nlargest(10, 'average')[['batsman', 'average', 'runs', 'innings']].to_dict('records')
            best_sr = season_stats[season_stats['balls'] >= 20].nlargest(10, 'sr')[['batsman', 'sr', 'runs', 'balls']].to_dict('records')
            most_fours = season_stats.nlargest(10, 'fours')[['batsman', 'fours', 'runs', 'innings']].to_dict('records')
            most_sixes = season_stats.nlargest(10, 'sixes')[['batsman', 'sixes', 'runs', 'innings']].to_dict('records')
            
            stats["batting"] = {
                "season_stats": season_stats.to_dict('records'),
                "leaderboards": {
                    "top_run_scorers": top_run_scorers,
                    "highest_scores": highest_scores,
                    "best_averages": best_averages,
                    "best_strike_rates": best_sr,
                    "most_fours": most_fours,
                    "most_sixes": most_sixes
                }
            }
        
        if not bowling_df.empty:
            # Bowling statistics
            bowling_stats = bowling_df.groupby('bowler').agg({
                'wickets': 'sum',
                'runs': 'sum',
                'balls': 'sum',
                'overs': 'sum',
                'maidens': 'sum',
                'economy': 'mean',
                'file': 'nunique'
            }).reset_index()
            
            # Calculate averages, handling division by zero
            bowling_stats['average'] = bowling_stats.apply(
                lambda row: round(row['runs'] / row['wickets'], 2) if row['wickets'] > 0 else 0,
                axis=1
            )
            bowling_stats['strike_rate'] = bowling_stats.apply(
                lambda row: round(row['balls'] / row['wickets'], 2) if row['wickets'] > 0 else 0,
                axis=1
            )
            bowling_stats['economy'] = bowling_stats['economy'].round(2)
            
            # Replace any remaining NaN or Infinity with 0
            bowling_stats = bowling_stats.replace([float('inf'), float('-inf')], 0).fillna(0)
            
            top_wicket_takers = bowling_stats.nlargest(10, 'wickets')[['bowler', 'wickets', 'average', 'economy']].to_dict('records')
            best_figures = bowling_df.nlargest(10, 'wickets')[['bowler', 'wickets', 'runs', 'overs']].to_dict('records')
            best_economy = bowling_stats[bowling_stats['overs'] >= 2].nsmallest(10, 'economy')[['bowler', 'economy', 'overs', 'wickets']].to_dict('records')
            
            stats["bowling"] = {
                "season_stats": bowling_stats.to_dict('records'),
                "leaderboards": {
                    "top_wicket_takers": top_wicket_takers,
                    "best_figures": best_figures,
                    "best_economy": best_economy
                }
            }
        
        return stats
    
    def generate_html(self):
        """Generate HTML file with embedded stats data."""
        
        # Read the generated stats JSON
        with open(self.output_dir / "stats.json", "r") as f:
            stats_json = f.read()
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Warsaw Hussars Cricket Club - Statistics</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- Embedded stats data for offline viewing -->
    <script id="statsData" type="application/json">
{stats_json}
    </script>
    
    <header>
        <div class="container">
            <h1>🏏 Warsaw Hussars Cricket Club</h1>
            <p class="subtitle">Season Statistics Dashboard</p>
            <p class="last-updated">Last updated: <span id="lastUpdated"></span></p>
        </div>
    </header>

    <main class="container">
        <!-- Summary Cards -->
        <section class="summary-cards">
            <div class="card">
                <h3>Total Matches</h3>
                <p class="stat-value" id="totalMatches">-</p>
            </div>
            <div class="card">
                <h3>Total Runs</h3>
                <p class="stat-value" id="totalRuns">-</p>
            </div>
            <div class="card">
                <h3>Total Players</h3>
                <p class="stat-value" id="totalPlayers">-</p>
            </div>
            <div class="card">
                <h3>Season</h3>
                <p class="stat-value" id="dateRange">-</p>
            </div>
        </section>

        <!-- Year Selector -->
        <div class="year-selector">
            <label for="yearSelect">Season:</label>
            <select id="yearSelect" onchange="changeYear(this.value)">
                <option value="2026">2026</option>
                <option value="2025">2025</option>
            </select>
        </div>

        <!-- Tabs Navigation -->
        <div class="tabs">
            <button class="tab-button active" onclick="showTab('batting')">Batting</button>
            <button class="tab-button" onclick="showTab('bowling')">Bowling</button>
            <button class="tab-button" onclick="showTab('allPlayers')">All Players</button>
        </div>

        <!-- Batting Tab -->
        <div id="batting" class="tab-content active">
            <h2>Batting Statistics</h2>
            
            <div class="leaderboards">
                <div class="leaderboard">
                    <h3>🏆 Top Run Scorers</h3>
                    <table id="topRunScorers">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Player</th>
                                <th>Runs</th>
                                <th>Inn</th>
                                <th>Avg</th>
                                <th>SR</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>

                <div class="leaderboard">
                    <h3>⚡ Highest Scores</h3>
                    <table id="highestScores">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Player</th>
                                <th>Runs</th>
                                <th>Balls</th>
                                <th>SR</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>

                <div class="leaderboard">
                    <h3>📊 Best Averages</h3>
                    <table id="bestAverages">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Player</th>
                                <th>Avg</th>
                                <th>Runs</th>
                                <th>Inn</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>

                <div class="leaderboard">
                    <h3>🚀 Best Strike Rates</h3>
                    <table id="bestStrikeRates">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Player</th>
                                <th>SR</th>
                                <th>Runs</th>
                                <th>Balls</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>

                <div class="leaderboard">
                    <h3>🎯 Most Fours</h3>
                    <table id="mostFours">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Player</th>
                                <th>4s</th>
                                <th>Runs</th>
                                <th>Inn</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>

                <div class="leaderboard">
                    <h3>💥 Most Sixes</h3>
                    <table id="mostSixes">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Player</th>
                                <th>6s</th>
                                <th>Runs</th>
                                <th>Inn</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Bowling Tab -->
        <div id="bowling" class="tab-content">
            <h2>Bowling Statistics</h2>
            
            <div class="leaderboards">
                <div class="leaderboard">
                    <h3>🎯 Top Wicket Takers</h3>
                    <table id="topWicketTakers">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Player</th>
                                <th>Wkts</th>
                                <th>Avg</th>
                                <th>Econ</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>

                <div class="leaderboard">
                    <h3>🔥 Best Figures</h3>
                    <table id="bestFigures">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Player</th>
                                <th>Wkts</th>
                                <th>Runs</th>
                                <th>Overs</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>

                <div class="leaderboard">
                    <h3>💰 Best Economy</h3>
                    <table id="bestEconomy">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Player</th>
                                <th>Econ</th>
                                <th>Overs</th>
                                <th>Wkts</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- All Players Tab -->
        <div id="allPlayers" class="tab-content">
            <h2>All Players - Season Statistics</h2>
            
            <div class="search-box">
                <input type="text" id="playerSearch" placeholder="Search player..." onkeyup="filterPlayers()">
            </div>

            <div class="player-table-container">
                <table id="allPlayersTable">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)">Player</th>
                            <th onclick="sortTable(1)">Mat</th>
                            <th onclick="sortTable(2)">Runs</th>
                            <th onclick="sortTable(3)">Avg</th>
                            <th onclick="sortTable(4)">SR</th>
                            <th onclick="sortTable(5)">Balls</th>
                            <th onclick="sortTable(6)">4s</th>
                            <th onclick="sortTable(7)">6s</th>
                        </tr>
                    </thead>
                    <tbody id="allPlayersList"></tbody>
                </table>
            </div>
        </div>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025-2026 Warsaw Hussars Cricket Club | Generated from CricHeroes scorecards</p>
            <p><a href="https://github.com/Ostyk/whcc_stats" target="_blank">View on GitHub</a></p>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>
'''
        
        with open(self.output_dir / "index.html", "w") as f:
            f.write(html_content)
    
    def generate_css(self):
        """Generate CSS file."""
        css_content = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

header {
    background: rgba(255, 255, 255, 0.95);
    padding: 30px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 30px;
}

header h1 {
    color: #667eea;
    font-size: 2.5em;
    margin-bottom: 10px;
}

.subtitle {
    color: #666;
    font-size: 1.2em;
}

.last-updated {
    color: #888;
    font-size: 0.9em;
    margin-top: 10px;
}

main {
    background: white;
    border-radius: 15px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
}

.card h3 {
    font-size: 0.9em;
    opacity: 0.9;
    margin-bottom: 10px;
}

.stat-value {
    font-size: 2em;
    font-weight: bold;
}

.year-selector {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 10px;
}

.year-selector label {
    font-size: 1.1em;
    color: #667eea;
    font-weight: bold;
    margin-right: 10px;
}

.year-selector select {
    padding: 10px 20px;
    font-size: 1em;
    border: 2px solid #667eea;
    border-radius: 8px;
    background: white;
    color: #667eea;
    cursor: pointer;
    transition: all 0.3s;
}

.year-selector select:hover {
    background: #667eea;
    color: white;
}

.year-selector select:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
    border-bottom: 2px solid #eee;
}

.tab-button {
    padding: 12px 24px;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1em;
    color: #666;
    border-bottom: 3px solid transparent;
    transition: all 0.3s;
}

.tab-button:hover {
    color: #667eea;
}

.tab-button.active {
    color: #667eea;
    border-bottom-color: #667eea;
}

.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
    animation: fadeIn 0.3s;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.leaderboards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    margin-top: 20px;
}

.leaderboard {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
}

.leaderboard h3 {
    color: #667eea;
    margin-bottom: 15px;
    font-size: 1.2em;
}

table {
    width: 100%;
    border-collapse: collapse;
}

thead th {
    background: #667eea;
    color: white;
    padding: 10px;
    text-align: left;
    font-weight: 600;
    font-size: 0.9em;
}

tbody tr {
    border-bottom: 1px solid #eee;
    transition: background 0.2s;
}

tbody tr:hover {
    background: #f0f0f0;
}

tbody td {
    padding: 10px;
}

tbody td:first-child {
    font-weight: bold;
    color: #667eea;
}

.search-box {
    margin-bottom: 20px;
}

.search-box input {
    width: 100%;
    padding: 12px;
    border: 2px solid #eee;
    border-radius: 8px;
    font-size: 1em;
}

.search-box input:focus {
    outline: none;
    border-color: #667eea;
}

.player-table-container {
    overflow-x: auto;
}

footer {
    text-align: center;
    padding: 20px;
    color: white;
}

footer a {
    color: white;
    text-decoration: underline;
}

@media (max-width: 768px) {
    header h1 {
        font-size: 1.8em;
    }
    
    .summary-cards {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .leaderboards {
        grid-template-columns: 1fr;
    }
}
'''
        
        with open(self.output_dir / "style.css", "w") as f:
            f.write(css_content)
    
    def generate_js(self):
        """Generate JavaScript file."""
        js_content = '''let allStatsData = null;
let currentYear = '2026'; // Default to 2026

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    // Try to load from embedded script tag first (for offline/file:// access)
    const embeddedData = document.getElementById('statsData');
    if (embeddedData && embeddedData.textContent) {
        try {
            allStatsData = JSON.parse(embeddedData.textContent);
            console.log('✓ Stats loaded from embedded data');
            initializeYearSelector();
            displayStats(currentYear);
            return;
        } catch (e) {
            console.log('Failed to parse embedded data:', e);
        }
    }
    
    // Fallback to fetch (for server/GitHub Pages)
    loadStats();
});

async function loadStats() {
    try {
        const response = await fetch('stats.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        allStatsData = await response.json();
        console.log('✓ Stats loaded from fetch');
        initializeYearSelector();
        displayStats(currentYear);
    } catch (error) {
        console.error('Error loading stats:', error);
        // Show error message to user
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.innerHTML = `
                <div style="text-align: center; padding: 50px; color: #666;">
                    <h2>⚠️ Unable to Load Statistics</h2>
                    <p style="margin: 20px 0;">Could not load cricket statistics.</p>
                    <p><strong>Error:</strong> ${error.message}</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                    <div style="text-align: left; max-width: 600px; margin: 0 auto; background: #f5f5f5; padding: 20px; border-radius: 8px;">
                        <p><strong>If viewing locally:</strong></p>
                        <ol>
                            <li>Make sure you're in the docs folder</li>
                            <li>Start a local server: <code style="background: white; padding: 2px 8px; border-radius: 4px;">python3 -m http.server 8000</code></li>
                            <li>Visit: <a href="http://localhost:8000">http://localhost:8000</a></li>
                        </ol>
                        <p style="margin-top: 15px;"><strong>Or:</strong> Open the browser console (F12) to see detailed errors.</p>
                    </div>
                </div>
            `;
        }
    }
}

function initializeYearSelector() {
    const yearSelect = document.getElementById('yearSelect');
    if (yearSelect && allStatsData) {
        // Set default to current year
        yearSelect.value = currentYear;
        
        // Disable years with no data
        const options = yearSelect.querySelectorAll('option');
        options.forEach(option => {
            const year = option.value;
            if (!allStatsData[year] || !allStatsData[year].summary || !allStatsData[year].summary.total_matches) {
                option.disabled = true;
                option.textContent += ' (No data)';
            }
        });
    }
}

function changeYear(year) {
    currentYear = year;
    displayStats(year);
    console.log(`Switched to ${year} season`);
}

function displayStats(year) {
    const statsData = allStatsData[year];
    
    if (!statsData || !statsData.summary) {
        console.warn(`No data available for ${year}`);
        showNoDataMessage(year);
        return;
    }
    
    // Update summary
    document.getElementById('lastUpdated').textContent = new Date(statsData.last_updated).toLocaleDateString();
    document.getElementById('totalMatches').textContent = statsData.summary.total_matches || '-';
    document.getElementById('totalRuns').textContent = statsData.summary.total_runs || '-';
    document.getElementById('totalPlayers').textContent = statsData.summary.total_players || '-';
    
    if (statsData.summary.date_range) {
        const start = new Date(statsData.summary.date_range.start).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
        const end = new Date(statsData.summary.date_range.end).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
        document.getElementById('dateRange').textContent = `${start} - ${end}`;
    } else {
        document.getElementById('dateRange').textContent = '-';
    }
    
    // Display batting leaderboards
    if (statsData.batting && statsData.batting.leaderboards) {
        displayLeaderboard('topRunScorers', statsData.batting.leaderboards.top_run_scorers, 
            ['batsman', 'runs', 'innings', 'average', 'sr']);
        displayLeaderboard('highestScores', statsData.batting.leaderboards.highest_scores, 
            ['batsman', 'runs', 'balls', 'sr']);
        displayLeaderboard('bestAverages', statsData.batting.leaderboards.best_averages, 
            ['batsman', 'average', 'runs', 'innings']);
        displayLeaderboard('bestStrikeRates', statsData.batting.leaderboards.best_strike_rates, 
            ['batsman', 'sr', 'runs', 'balls']);
        displayLeaderboard('mostFours', statsData.batting.leaderboards.most_fours, 
            ['batsman', 'fours', 'runs', 'innings']);
        displayLeaderboard('mostSixes', statsData.batting.leaderboards.most_sixes, 
            ['batsman', 'sixes', 'runs', 'innings']);
        
        // Display all players
        displayAllPlayers(statsData.batting.season_stats);
    } else {
        clearLeaderboards();
    }
    
    // Display bowling leaderboards
    if (statsData.bowling && statsData.bowling.leaderboards) {
        displayLeaderboard('topWicketTakers', statsData.bowling.leaderboards.top_wicket_takers, 
            ['bowler', 'wickets', 'average', 'economy']);
        displayLeaderboard('bestFigures', statsData.bowling.leaderboards.best_figures, 
            ['bowler', 'wickets', 'runs', 'overs']);
        displayLeaderboard('bestEconomy', statsData.bowling.leaderboards.best_economy, 
            ['bowler', 'economy', 'overs', 'wickets']);
    }
}

function showNoDataMessage(year) {
    const tables = document.querySelectorAll('table tbody');
    tables.forEach(tbody => {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align: center; padding: 20px; color: #888;">
                    No data available for ${year} season yet
                </td>
            </tr>
        `;
    });
    
    document.getElementById('dateRange').textContent = 'No matches yet';
}

function clearLeaderboards() {
    const tables = ['topRunScorers', 'highestScores', 'bestAverages', 'bestStrikeRates', 
                    'mostFours', 'mostSixes', 'topWicketTakers', 'bestFigures', 'bestEconomy'];
    tables.forEach(tableId => {
        const tbody = document.querySelector(`#${tableId} tbody`);
        if (tbody) tbody.innerHTML = '';
    });
}

function displayLeaderboard(tableId, data, columns) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    if (!tbody) return;
    
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: #888;">No data</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    data.forEach((row, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            ${columns.map(col => `<td>${formatValue(row[col], col)}</td>`).join('')}
        `;
        tbody.appendChild(tr);
    });
}

function displayAllPlayers(players) {
    const tbody = document.getElementById('allPlayersList');
    if (!tbody) return;
    
    if (!players || players.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: #888;">No players</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    players.forEach(player => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${player.batsman}</td>
            <td>${formatValue(player.innings, 'innings')}</td>
            <td>${formatValue(player.runs, 'runs')}</td>
            <td>${formatValue(player.average, 'average')}</td>
            <td>${formatValue(player.sr, 'sr')}</td>
            <td>${formatValue(player.balls, 'balls')}</td>
            <td>${formatValue(player.fours, 'fours')}</td>
            <td>${formatValue(player.sixes, 'sixes')}</td>
        `;
        tbody.appendChild(tr);
    });
}

function formatValue(val, columnName) {
    if (val === null || val === undefined) return '-';
    if (typeof val === 'number') {
        if (isNaN(val)) return '-';
        
        // Integer fields - no decimal places
        const integerFields = ['runs', 'innings', 'balls', 'fours', 'sixes', 'wickets', 'overs', 'maidens'];
        if (columnName && integerFields.includes(columnName)) {
            return Math.round(val).toString();
        }
        
        // Decimal fields (average, sr, economy)
        return val.toFixed(2);
    }
    return val;
}

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

function filterPlayers() {
    const searchTerm = document.getElementById('playerSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#allPlayersList tr');
    
    rows.forEach(row => {
        const playerName = row.cells[0].textContent.toLowerCase();
        row.style.display = playerName.includes(searchTerm) ? '' : 'none';
    });
}

function sortTable(columnIndex) {
    // Simple table sorting (can be enhanced)
    const table = document.getElementById('allPlayersTable');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.cells[columnIndex].textContent;
        const bVal = b.cells[columnIndex].textContent;
        
        // Try numeric comparison first
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return bNum - aNum;
        }
        
        // String comparison
        return aVal.localeCompare(bVal);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}
'''
        
        with open(self.output_dir / "script.js", "w") as f:
            f.write(js_content)


def main():
    """Main function to parse scorecards and generate website."""
    print("=" * 60)
    print("Warsaw Hussars Cricket Club - Website Generator")
    print("=" * 60)
    
    # Parse scorecards for each year
    years = ["2025", "2026"]
    stats_by_year = {}
    
    for year in years:
        print(f"\n{'='*60}")
        print(f"Processing {year} scorecards...")
        print(f"{'='*60}")
        
        year_folder = f"scorecards/{year}"
        parser = ScorecardParser(year_folder)
        parser.parse_all_scorecards()
        
        batting_df = parser.get_batting_dataframe()
        bowling_df = parser.get_bowling_dataframe()
        
        if batting_df.empty and year == "2026":
            print(f"\n⚠️ No records found for {year} (this is normal if the season hasn't started)")
            stats_by_year[year] = {"batting_df": batting_df, "bowling_df": bowling_df}
            continue
        elif batting_df.empty:
            print(f"\n⚠️ No batting records found for {year}.")
            continue
        
        # Display summary
        print(f"\n📊 {year} Data Summary:")
        print(f"  Total batting innings: {len(batting_df)}")
        print(f"  Unique players: {batting_df['batsman'].nunique()}")
        print(f"  Total runs: {batting_df['runs'].sum()}")
        print(f"  Total bowling records: {len(bowling_df)}")
        if not batting_df['match_date'].isna().all():
            print(f"  Date range: {batting_df['match_date'].min().strftime('%Y-%m-%d')} to {batting_df['match_date'].max().strftime('%Y-%m-%d')}")
        
        stats_by_year[year] = {"batting_df": batting_df, "bowling_df": bowling_df}
    
    if not stats_by_year:
        print("\n⚠️ No records found for any year.")
        return
    
    # Generate website with multi-year support
    website_gen = WebsiteGenerator(stats_by_year=stats_by_year)
    website_gen.generate_website()
    
    print("\n" + "=" * 60)
    print("Website generation complete!")
    print("\nNext steps:")
    print("1. Test locally: open docs/index.html in your browser")
    print("2. Commit and push to GitHub")
    print("3. Enable GitHub Pages in repository settings")
    print("   - Go to Settings > Pages")
    print("   - Source: Deploy from a branch")
    print("   - Branch: main, folder: /docs")
    print("4. Your site will be live at:")
    print("   https://ostyk.github.io/whcc_stats/")
    print("=" * 60)


if __name__ == "__main__":
    main()
