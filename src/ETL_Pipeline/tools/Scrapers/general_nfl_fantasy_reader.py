# General tool for analyzing pages of NFL.com

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys


url = 'https://fantasy.nfl.com/draftclient?leagueId=12470023&teamId=8'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')







print()