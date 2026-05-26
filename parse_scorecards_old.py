#!/usr/bin/env python3
"""
Warsaw Hussars Cricket Club - Scorecard Parser and Stats Generator

This script parses PDF scorecards and generates comprehensive cricket statistics
in an Excel file format similar to the reference statistics file.
"""

import pdfplumber
import re
import pandas as pd
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment


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
                
                # Extract match date/time
                match_datetime = self.extract_match_date(text)
                
                # Extract batting records
                self.extract_batting_records(text, pdf_file.name, match_datetime)
                
                # Extract bowling records
                self.extract_bowling_records(text, pdf_file.name, match_datetime)
                
        except Exception as e:
            print(f"  ✗ Error parsing {pdf_file.name}: {e}")
    
    def extract_match_date(self, text):
        """Extract match date from scorecard text."""
        date_match = re.search(r"Date\s+(\d{4}-\d{2}-\d{2}),\s+([\d:]+\s+[APM]+ UTC)", text)
        if date_match:
            match_date_str = date_match.group(1)
            match_time_str = date_match.group(2)
            match_time_str = re.sub(r'\s*[APM]+\s+UTC', ' UTC', match_time_str)
            try:
                return pd.to_datetime(f"{match_date_str} {match_time_str}")
            except:
                return pd.to_datetime(match_date_str)
        return None
    
    def extract_batting_records(self, text, filename, match_datetime):
        """Extract batting records for Warsaw Hussars."""
        # Find all Warsaw Hussars innings headers
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
            
            # Stop parsing at "Extras" or "Total"
            stop_match = re.search(r"Extras:|Total:", innings_text)
            if stop_match:
                innings_text = innings_text[:stop_match.start()]
            
            # Parse batting lines
            for line in innings_text.splitlines():
                line = line.strip()
                
                # Skip other team headers
                if re.match(r".+\s+\d+/\d+d?\s+\([\d.]+\s*Ov\)\s+\(\d+(?:st|nd)\s+Innings\)", line) and "Warsaw Hussars" not in line:
                    break
                
                # Batting line regex
                pattern = re.compile(
                    r"^(\d+)\s+"                        # Position
                    r"([A-Za-z\s&'.()'-]+?)\s+"         # Batsman Name
                    r"\(.*?\)\s+"                        # Handedness (RHB/LHB)
                    r"(.+?)\s+"                          # Status (dismissal)
                    r"(\d+)\s+"                          # Runs
                    r"(\d+)\s+"                          # Balls
                    r"(\d+)\s+"                          # Minutes
                    r"(\d+)\s+"                          # Fours
                    r"(\d+)\s+"                          # Sixes
                    r"([\d.]+)$"                         # Strike Rate
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
                        "match_date": match_datetime
                    })
    
    def extract_bowling_records(self, text, filename, match_datetime):
        """Extract bowling records for Warsaw Hussars."""
        # Find bowling sections (opponent innings where WH bowled)
        # This is a simplified version - you may need to adjust based on actual format
        
        # Look for bowling lines that match typical format:
        # Position Name Overs Maidens Runs Wickets Econ
        bowling_pattern = re.compile(
            r"^(\d+)\s+"                        # Position
            r"([A-Za-z\s&'.()'-]+?)\s+"         # Bowler Name
            r"\(.*?\)\s+"                        # Handedness
            r"([\d.]+)\s+"                       # Overs
            r"(\d+)\s+"                          # Maidens
            r"(\d+)\s+"                          # Runs
            r"(\d+)\s+"                          # Wickets
            r"([\d.]+)$"                         # Economy
        )
        
        # Extract opponent innings where Warsaw Hussars bowled
        # This needs more sophisticated parsing based on actual PDF structure
        # For now, we'll skip bowling as it requires more context
        pass
    
    def get_batting_dataframe(self):
        """Get batting records as DataFrame."""
        if not self.batting_records:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.batting_records)
        df = df.sort_values(by="match_date")
        df["out"] = df["status"].apply(lambda s: 0 if "not out" in s.lower() else 1)
        return df


class StatsGenerator:
    """Generate cricket statistics and create Excel output."""
    
    def __init__(self, batting_df):
        self.batting_df = batting_df
        self.output_file = f"Warsaw_Hussars_Stats_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    def generate_excel(self):
        """Generate Excel file with all statistics sheets."""
        if self.batting_df.empty:
            print("⚠️ No data to generate statistics")
            return
        
        print(f"\nGenerating statistics Excel file...")
        
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            # Generate each sheet
            self.create_batting_sheet(writer)
            self.create_bowling_sheet(writer)
            self.create_fielding_sheet(writer)
            self.create_wicketkeeping_sheet(writer)
            self.create_individual_sheet(writer)
            self.create_team_sheet(writer)
        
        print(f"✓ Statistics saved to: {self.output_file}")
    
    def create_batting_sheet(self, writer):
        """Create batting statistics sheet."""
        # Aggregate batting stats
        summary = (
            self.batting_df.groupby("batsman")
            .agg(
                innings=("file", "count"),
                runs=("runs", "sum"),
                balls=("balls", "sum"),
                fours=("fours", "sum"),
                sixes=("sixes", "sum"),
                outs=("out", "sum"),
                avg_position=("position", "mean"),
                highest_score=("runs", "max")
            )
            .reset_index()
        )
        
        # Calculate derived stats
        summary["strike_rate"] = (summary["runs"] / summary["balls"]) * 100
        summary["average"] = summary.apply(
            lambda r: r["runs"] / r["outs"] if r["outs"] > 0 else r["runs"],
            axis=1
        )
        
        # Round values
        summary = summary.round({
            "avg_position": 2,
            "strike_rate": 2,
            "average": 2
        })
        
        # Create leaderboards
        most_runs_innings = self.batting_df.nlargest(10, 'runs')[['batsman', 'runs', 'file']].copy()
        most_runs_season = summary.nlargest(10, 'runs')[['batsman', 'runs']].copy()
        most_balls_season = summary.nlargest(10, 'balls')[['batsman', 'balls']].copy()
        highest_sr_season = summary[summary['balls'] >= 10].nlargest(10, 'strike_rate')[['batsman', 'strike_rate']].copy()
        
        # Combine into sheet format
        max_rows = max(len(most_runs_innings), len(most_runs_season), len(most_balls_season), len(highest_sr_season))
        
        batting_sheet = pd.DataFrame()
        batting_sheet['Rank_1'] = range(1, max_rows + 1)
        batting_sheet = pd.concat([
            batting_sheet,
            most_runs_innings.reset_index(drop=True).add_prefix('most_runs_innings_'),
            most_runs_season.reset_index(drop=True).add_prefix('most_runs_season_'),
            most_balls_season.reset_index(drop=True).add_prefix('most_balls_season_'),
            highest_sr_season.reset_index(drop=True).add_prefix('highest_sr_season_')
        ], axis=1)
        
        batting_sheet.to_excel(writer, sheet_name='Batting', index=False)
    
    def create_bowling_sheet(self, writer):
        """Create bowling statistics sheet (placeholder)."""
        # Placeholder - will need bowling data from scorecards
        bowling_data = pd.DataFrame({
            'Note': ['Bowling data extraction coming soon...']
        })
        bowling_data.to_excel(writer, sheet_name='Bowling', index=False)
    
    def create_fielding_sheet(self, writer):
        """Create fielding statistics sheet (placeholder)."""
        fielding_data = pd.DataFrame({
            'Note': ['Fielding data extraction coming soon...']
        })
        fielding_data.to_excel(writer, sheet_name='Fielding', index=False)
    
    def create_wicketkeeping_sheet(self, writer):
        """Create wicketkeeping statistics sheet (placeholder)."""
        wk_data = pd.DataFrame({
            'Note': ['Wicketkeeping data extraction coming soon...']
        })
        wk_data.to_excel(writer, sheet_name='Wicketkeeping', index=False)
    
    def create_individual_sheet(self, writer):
        """Create individual statistics sheet."""
        # Most matches
        matches_played = self.batting_df.groupby('batsman')['file'].nunique().reset_index()
        matches_played.columns = ['Player', 'Matches']
        matches_played = matches_played.sort_values('Matches', ascending=False).head(10)
        
        individual_data = pd.DataFrame()
        individual_data['Rank'] = range(1, len(matches_played) + 1)
        individual_data = pd.concat([individual_data, matches_played.reset_index(drop=True)], axis=1)
        
        individual_data.to_excel(writer, sheet_name='Individual', index=False)
    
    def create_team_sheet(self, writer):
        """Create team statistics sheet."""
        # Basic team stats
        total_matches = self.batting_df['file'].nunique()
        total_innings = len(self.batting_df)
        
        team_data = pd.DataFrame({
            'Statistic': ['Total Matches', 'Total Innings', 'Total Runs'],
            'Value': [
                total_matches,
                self.batting_df.groupby('file')['innings'].nunique().sum(),
                self.batting_df['runs'].sum()
            ]
        })
        
        team_data.to_excel(writer, sheet_name='Team', index=False)


def main():
    """Main function to parse scorecards and generate statistics."""
    print("=" * 60)
    print("Warsaw Hussars Cricket Club - Scorecard Parser")
    print("=" * 60)
    
    # Parse all scorecards
    parser = ScorecardParser("scorecards")
    parser.parse_all_scorecards()
    
    # Get batting dataframe
    batting_df = parser.get_batting_dataframe()
    
    if batting_df.empty:
        print("\n⚠️ No batting records found. Check scorecard format.")
        return
    
    # Display summary
    print(f"\n📊 Data Summary:")
    print(f"  Total innings: {len(batting_df)}")
    print(f"  Unique players: {batting_df['batsman'].nunique()}")
    print(f"  Total runs: {batting_df['runs'].sum()}")
    print(f"  Date range: {batting_df['match_date'].min()} to {batting_df['match_date'].max()}")
    
    # Generate statistics Excel
    stats_gen = StatsGenerator(batting_df)
    stats_gen.generate_excel()
    
    # Also save raw data as CSV for reference
    batting_df.to_csv("batting_records_raw.csv", index=False)
    print(f"✓ Raw batting data saved to: batting_records_raw.csv")
    
    print("\n" + "=" * 60)
    print("Statistics generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
