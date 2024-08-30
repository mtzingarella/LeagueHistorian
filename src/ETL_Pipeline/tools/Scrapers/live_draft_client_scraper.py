import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

class LiveDraftScraper:
    def __init__(self, url):
        self.url = url

    def scrape(self):
        # Fetch HTML content from the URL
        response = requests.get(self.url)
        html_content = response.text

        # Create a BeautifulSoup object from the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract all text from the soup
        soup_text = soup.get_text()

        # Print the soup text to verify its content
        print("Soup text:")
        print(soup_text)

        pattern = self.generate_regex_pattern()

        # Print the regex pattern to verify it
        print("Regex pattern:", pattern)

        # Find all matches in the soup text
        matches = re.findall(pattern, soup_text)

        # Create a DataFrame with the matches
        df = pd.DataFrame(matches, columns=['Match'])

        # Print the DataFrame
        print("Matches:")
        print(df)

    def generate_regex_pattern(self):
        # Pattern: 3 numerical characters followed by an uppercase letter, a period, a space, an uppercase letter, followed by between 1 and 20 characters that are letters of any case, symbols, and spaces, followed by 3 numerical characters
        pattern = r'\d{3}[A-Z]\. [A-Z][a-zA-Z .\'\-]*(?=\d{3}|\s|$)'
        return pattern

# Create an instance of LiveDraftScraper and scrape the data
scraper = LiveDraftScraper('https://fantasy.nfl.com/draftclient?leagueId=12479210&teamId=5')
scraper.scrape()
