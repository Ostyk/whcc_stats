#!/usr/bin/env python3
"""
Custom web scraper for Warsaw Hussars Cricket Club statistics.

Scrapes data from: https://cricheroes.com/team-profile/2444976/warsaw-hussars/leaderboard
Uses Selenium for JavaScript-rendered content.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time


class WarsawHussarsScraper:
    """Custom scraper for Warsaw Hussars cricket team data using Selenium."""
    
    def __init__(self, headless=True):
        self.base_url = "https://cricheroes.com/team-profile/2444976/warsaw-hussars"
        self.headless = headless
        self.driver = None
        
    def initialize_driver(self):
        """Initialize the Selenium WebDriver."""
        print("Initializing Chrome WebDriver...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✓ WebDriver initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing WebDriver: {e}")
            print("\nTrying Firefox as alternative...")
            try:
                from selenium.webdriver.firefox.service import Service as FirefoxService
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                from webdriver_manager.firefox import GeckoDriverManager
                
                firefox_options = FirefoxOptions()
                if self.headless:
                    firefox_options.add_argument('--headless')
                
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
                print("✓ Firefox WebDriver initialized successfully")
            except Exception as e2:
                print(f"✗ Error initializing Firefox WebDriver: {e2}")
                raise
    
    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            print("✓ WebDriver closed")
    
    def scrape_leaderboard(self):
        """Scrape the team leaderboard page."""
        url = f"{self.base_url}/leaderboard"
        print(f"\nFetching leaderboard from: {url}")
        
        try:
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for content to load (adjust selector as needed)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                pass
            
            # Get page source after JavaScript rendering
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Save raw HTML for inspection
            with open('leaderboard_raw.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("✓ Raw HTML saved to leaderboard_raw.html")
            
            # Extract leaderboard data
            leaderboard_data = {
                'batting': [],
                'bowling': [],
                'fielding': [],
                'timestamp': datetime.now().isoformat(),
                'raw_html_saved': True
            }
            
            # Look for tables
            tables = soup.find_all('table')
            print(f"  Found {len(tables)} tables")
            
            # Look for player links
            player_links = soup.find_all('a', href=lambda x: x and '/player-profile/' in x if x else False)
            print(f"  Found {len(player_links)} player profile links")
            
            if player_links:
                leaderboard_data['players_found'] = []
                for link in player_links:
                    player_name = link.get_text(strip=True)
                    if player_name:
                        leaderboard_data['players_found'].append({
                            'name': player_name,
                            'profile_url': link.get('href', '')
                        })
            
            # Extract page title
            leaderboard_data['page_title'] = soup.title.string if soup.title else "No title"
            
            return leaderboard_data
            
        except Exception as e:
            print(f"✗ Error fetching leaderboard: {e}")
            return None
    
    def scrape_team_stats(self):
        """Scrape the team stats page."""
        url = f"{self.base_url}/stats"
        print(f"\nFetching team stats from: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(3)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Save raw HTML
            with open('stats_raw.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("✓ Raw HTML saved to stats_raw.html")
            
            stats_data = {
                'page_title': soup.title.string if soup.title else "No title",
                'timestamp': datetime.now().isoformat(),
                'raw_html_saved': True
            }
            
            return stats_data
            
        except Exception as e:
            print(f"✗ Error fetching stats: {e}")
            return None
    
    def scrape_matches(self):
        """Scrape the team matches page."""
        url = f"{self.base_url}/matches"
        print(f"\nFetching matches from: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(3)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Save raw HTML
            with open('matches_raw.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("✓ Raw HTML saved to matches_raw.html")
            
            matches_data = {
                'page_title': soup.title.string if soup.title else "No title",
                'timestamp': datetime.now().isoformat(),
                'raw_html_saved': True
            }
            
            return matches_data
            
        except Exception as e:
            print(f"✗ Error fetching matches: {e}")
            return None


def main():
    """Main function to scrape Warsaw Hussars team data."""
    
    print("=" * 60)
    print("Warsaw Hussars Cricket Club - Web Scraper (Selenium)")
    print("=" * 60)
    
    scraper = WarsawHussarsScraper(headless=True)
    
    try:
        scraper.initialize_driver()
        
        # Scrape leaderboard
        leaderboard_data = scraper.scrape_leaderboard()
        if leaderboard_data:
            with open('warsaw_hussars_leaderboard.json', 'w') as f:
                json.dump(leaderboard_data, f, indent=2)
            print("✓ Leaderboard data saved to warsaw_hussars_leaderboard.json")
        
        # Scrape stats
        stats_data = scraper.scrape_team_stats()
        if stats_data:
            with open('warsaw_hussars_stats.json', 'w') as f:
                json.dump(stats_data, f, indent=2)
            print("✓ Stats data saved to warsaw_hussars_stats.json")
        
        # Scrape matches
        matches_data = scraper.scrape_matches()
        if matches_data:
            with open('warsaw_hussars_matches.json', 'w') as f:
                json.dump(matches_data, f, indent=2)
            print("✓ Matches data saved to warsaw_hussars_matches.json")
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
    
    finally:
        scraper.close_driver()
    
    print("\n" + "=" * 60)
    print("Scraping complete!")
    print("\nNext steps:")
    print("1. Check the *_raw.html files to see the page structure")
    print("2. Refine the scraper to extract specific data elements")
    print("3. Update the parsing logic based on HTML structure")
    print("=" * 60)


if __name__ == "__main__":
    main()

