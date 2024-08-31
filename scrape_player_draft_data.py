from typing import final
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException  # Add this line
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://fantasy.nfl.com/draftcenter/breakdown?leagueId=332843'

options = Options()
options.binary_location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"

driver = webdriver.Firefox(service=Service(), options=options)
driver.get(url)

# Read html from webpage 
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')



#create final_df with the columns for player name, position, team, and NFL ADP
final_df = pd.DataFrame(columns=['Player Name', 'Position', 'Team', 'NFL ADP'])
all_dfs = []


# Click the next button and scrape again, repeat 5 times.
for i in range(20):
  
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    player_names = soup.select('a[class^="playerCard"]')
    player_names = [name.text for name in player_names]
    player_names = soup.select('a[class^="playerCard"]')
    player_names = [name.text for name in player_names]
    player_positions = soup.find_all('em')
    cleaned_player_positions = []
    player_teams = []
    n = 0
    for player in player_positions:
        player_str = player.text
        print(player_str)
        if(player_str != "Standard Draft" and player_str != "Salary Cap Draft" and player_str != "DEF" and player_str != 'TE' and player_str != 'QB' and player_str != 'RB' and player_str != 'WR' and player_str != 'K'):
            player_team = player_str.split('-')[0]
            player_str = player.text
            player_pos = player_str.split('-')[1]
            player_teams.append(player_team)
            cleaned_player_positions.append(player_pos)
            n=n+1
            continue
        if(player_str == "DEF"):
            #make sure player_names[n] isnt out of index and do it if so, if not, player_team = 'ERROR'
            if(n >= len(player_names)):
                player_team = 'ERROR'
            else:
                player_team = player_names[n]
            player_pos = player_str
            player_teams.append(player_team)
            cleaned_player_positions.append(player_pos)
            n=n+1
        if (player_str == 'TE' or player_str == 'QB' or player_str == 'RB' or player_str == 'WR' or player_str == 'K'):
            player_pos = player_str
            player_teams.append(player_str)
            cleaned_player_positions.append(player_pos)
            n=n+1


            continue
        else:
            n=n+1
            pass
    player_adps = soup.select('td[class^="playerDraftAvgPick rank numeric sorted"]')
    player_adps = [adp.text for adp in player_adps]
    
    # print the length of each list to make sure they are the same
    print(len(player_names))
    print(len(cleaned_player_positions))
    print(len(player_teams))
    print(len(player_adps))

    #Create df with columns for player name, position, team, NFL_ADP
    df = pd.DataFrame(columns=['Player Name', 'Position', 'Team', 'NFL ADP'])
    df['Player Name'] = player_names
    df['Position'] = cleaned_player_positions
    df['Team'] = player_teams
    df['NFL ADP'] = player_adps
    print(df)
    

    
    #pause and ask user for input to continue
    input("Press Enter to continue...")

    all_dfs.append(df)

    
    n=0
    i=i+1


#save final dataframe in the decision models data section as a csv
final_df = pd.concat(all_dfs, ignore_index=True)
final_df.to_csv('live_draft_app/Decision_Model/data/player_data.csv', index=False)

# Close the driver
driver.quit()
