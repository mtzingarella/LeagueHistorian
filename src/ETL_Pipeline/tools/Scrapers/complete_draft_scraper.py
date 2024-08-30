import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import re

# Add path to owner id mapper file
sys.path.append('src/Misc_Tools')
from owner_id_mapper import OwnerIDMapper

# Finding the number of years the league has existed
url = 'https://fantasy.nfl.com/league/332843/history'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
season_menu = soup.find('div', class_='st-menu')
years = re.findall(r'\D(\d{4})(?:\D|$)', season_menu.text)
years_to_process = [season_menu.text[:4]] + years
current_year = int(years_to_process[0]) + 1
years_to_process.insert(0, str(current_year))  # History menu does not show current year, but url works the same for draft

# Exclude the year 2024 from processing
years_to_process = [year for year in years_to_process if year != '2024']

# Create a mapper for owner ids/names
mapper = OwnerIDMapper('SavedData/most_recent_scrapes/owners_by_year_and_ids.csv')

def analyze_season_draft(year):
    url = f'https://fantasy.nfl.com/league/332843/history/{year}/draftresults?draftResultsDetail=0&draftResultsTab=round&draftResultsType=results'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    drafted_players = soup.find_all('a', class_='playerName')
    drafted_players_names = [ele.text for ele in drafted_players]
    drafted_players_ids = [ele['class'][-2].split('-')[1] for ele in drafted_players]
    drafted_players_pos_teams =  [ele.find_next('em').text for ele in drafted_players]
    draft_order_ownerteam_names = [ele.text.split(',')[0] for ele in soup.find_all('a', class_='teamName')]
    draft_order_owner__names = [ele.text.split(',')[0] for ele in soup.find_all('li', class_='first last')]
    draft_order_owner_ids = [str(mapper.get_owner_id(int(year), name)) for name in draft_order_ownerteam_names]


    data = {
        'Year': [year] * len(drafted_players_names),
        'PlayerName': drafted_players_names,
        'PlayerID': drafted_players_ids,
        'Pos_Team': drafted_players_pos_teams,
        'OwnerTeamName': draft_order_ownerteam_names,
        'OwnerName': draft_order_owner__names,
        'OwnerID': draft_order_owner_ids,
        
    }
    df = pd.DataFrame(data).reset_index(drop=True)
    return df

# Initialize dataframe with same columns as one returned by function
draft_data = {
    'Year': [],
    'PlayerName': [],
    'PlayerID': [],
    'OwnerName': [],
    'OwnerID': [],
    'OwnerTeamName': []
}

all_draft_data = pd.DataFrame(draft_data)

# Iterate through years to process calling the analyze_season_draft function and adding the returned dataframe to the dataframe initialized above
for year in years_to_process:
    all_draft_data = pd.concat([all_draft_data, analyze_season_draft(year)], ignore_index=True)

# Calculate num_teams for each year and store it in a dictionary
num_teams_by_year = {}
for year in years_to_process:
    unique_teams = all_draft_data[all_draft_data['Year'] == str(year)].OwnerTeamName.nunique()
    num_teams_by_year[year] = unique_teams

# Create a new column 'NumTeams' based on the 'Year' column
all_draft_data['NumTeams'] = all_draft_data['Year'].map(num_teams_by_year)

# Calculate num_picks_by_year and num_rounds_by_year
num_picks_by_year = {}
num_rounds_by_year = {}
for year in years_to_process:
    num_picks_by_year[year] = all_draft_data[all_draft_data['Year'] == str(year)].shape[0]
    if num_teams_by_year[year] != 0:
        num_rounds_by_year[year] = num_picks_by_year[year] / num_teams_by_year[year]
    else:
        print(f"Warning: Number of teams for year {year} is zero. Skipping division.")

# Add a column that stores which round each pick is in
round_list = []
for year in years_to_process:
    for i in range(1, int(num_rounds_by_year[year]) + 1):
        round_list += [i] * int(num_teams_by_year[year])

all_draft_data['Round'] = round_list

# Add a column for the pick number as determined by the round and the index at which the year falls in the years_to_be_processed list
all_draft_data['PickNum'] = (all_draft_data.index % all_draft_data['NumTeams']) + 1

# Add a column for overall pick number (with regards to year of draft)
all_draft_data['OverallPickNum'] = (all_draft_data['Round'] - 1) * all_draft_data['NumTeams'] + all_draft_data['PickNum']

# Add a column for player position that takes the first word of the 'Pos_Team' column
all_draft_data['PlayerPos'] = all_draft_data['Pos_Team'].apply(lambda x: x.split()[0])



# Save the dataframe to a CSV file
all_draft_data.to_csv('SavedData/most_recent_scrapes/complete_draft_data.csv', index=False)
all_draft_data.to_csv('src/ETL_Pipeline/data/staged_extracted_data/complete_draft_data.csv', index=False)