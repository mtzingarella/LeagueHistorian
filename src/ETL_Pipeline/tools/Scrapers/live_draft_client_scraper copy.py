import html
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

url = 'https://fantasy.nfl.com/draftclient?leagueId=12479210&teamId=5'

response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')
soup_text = soup.get_text()

print("Soup text:")
print(soup_text)
