import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


# Initializing a list to hold dictionaries for each row
owners_data = []

# Get the number of seasons the league has existed
url = 'https://fantasy.nfl.com/league/332843/history'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
season_menu = soup.find('div', class_='st-menu')

years = re.findall(r'\D(\d{4})(?:\D|$)', season_menu.text)
years_to_process = []
years_to_process.append(season_menu.text[:4]) #Code above fails to get most recent year due to webpage formatting inconsistency so I sloppily append it in here
#Append remaining years
for year in years:
    years_to_process.append(year)
current_year = int(years_to_process[0]) + 1
years_to_process.insert(0, str(current_year)) # History menu does not show current year, but url works the same

#Function gets owners data for a given year
def get_ids_for_year(year):
    url = f'https://fantasy.nfl.com/league/332843/history/{year}/owners'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    owner_data = []
    for owner, team_name, in zip(soup.find_all('span', class_='userName'), soup.find_all('a', class_='teamName')):
        if 'userName' in owner.get('class', []):
            user_id_class = [c for c in owner.get('class', []) if 'userId' in c][0]
            user_id = user_id_class.split('-')[1]
            owner_data.append({'Year': year, 'Owner': owner.text, 'OwnerID': user_id, 'OwnerTeamName': team_name.text})
    
    # Get team ids (IMPORTANT: TeamIDs are recycled and only unique within a given year)
    team_ids_raw = []
    for ele in soup.find_all('a', class_='teamName'):
        team_ids_raw.append(ele['class'][1])
    team_ids_filtered = ([int(team_id.split('-')[1]) for team_id in team_ids_raw])

    #Append team ids to owner data
    for owner, team_id in zip(owner_data, team_ids_filtered):
        owner['OwnerTeamID'] = team_id
    return owner_data

#Loop through years and scrape
for year in years_to_process:
    owners_data += get_ids_for_year(year) #SsSssSscrape

#Create df
owners_df = pd.DataFrame(owners_data)

#Write to csv, future modules will write df from csv
owners_df.to_csv('SavedData/most_recent_scrapes/complete_owners_by_year_and_ids.csv', index=False)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print(owners_df)






