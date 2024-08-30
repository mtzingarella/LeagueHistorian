from io import StringIO
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from owner_id_mapper import OwnerIDMapper

# Scrapes the final scores of a matchup as well as the individual points scored by players in matchup/on bench for entirety of leagues history
# except the current year 

# Essentially works by scraping info about the league from a 
# few key pages then using the info gathered to construct matchup urls
# which was much faster than scraping the hrefs but might also make this
# module more vulnerable to breaking from changes in nfl.com web design

# Must run AFTER historical_owners_id_scraper

# Function to build the url where the data of itnerest is stored
def construct_matchup_url(year, week,teamID):
    url_stem = 'https://fantasy.nfl.com'
    url = f'{url_stem}/league/332843/history/{year}/teamgamecenter?teamId={teamID}&week={week}'
    return url

#Initialize mapper, relies on data scraped by historical_owners_id_scraper.py to work correctly
mapper = OwnerIDMapper('SavedData/most_recent_scrapes/owners_by_year_and_ids.csv')

# START Scraping basic league data

# Find years to process
url = 'https://fantasy.nfl.com/league/332843/history'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
season_menu = soup.find('div', class_='st-menu')
years = re.findall(r'\D(\d{4})(?:\D|$)', season_menu.text) #Regex to find all 4 digit numbers in the season menu text
years_to_process = []
years_to_process.append(season_menu.text[:4]) #Code above fails to get most recent year due to webpage formatting inconsistency so I sloppily append it in here
#Append remaining years
for year in years:
    years_to_process.append(year)

# Find weeks to process for each year, store in dict of lists
# Key: Year, Value: List of week numbers 
weeks_to_process = {}

# Create a dictionary to hold number of weeks for each season (Not a constant value for the nfl or fantasy leagues, which sometimes draft mid season)
for year in years_to_process:
    url = f'https://fantasy.nfl.com/league/332843/history/{year}/schedule'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    raw_weeklist = [] #the webpage has some extra elements with the class 'title' which makes it annoying to get the weeks for the year being processed
    filtered_weeklist = []
    for week in soup.find_all('span', class_ = 'title'):
        raw_weeklist.append(week.text)
    for e in raw_weeklist:
        try:
            week_number = int(e)
            filtered_weeklist.append(week_number)
        except ValueError:
            # Handle the case where week.text is not a digit (ignore)
            pass
    weeks_to_process[year] = filtered_weeklist


# Find the teamIDs present in each year, needed for gamecenter urls
teamIds_byyear = {}
for year in years_to_process:
    team_ids_in_year = []
    teamIds_byyear[year] = mapper.get_all_teams_for_year(int(year))

# END Scraping basic league data

#START Matchup scraping functions

# General function that attempts to scrapes tables form a webpage and make them dataframes.
# This function is called on every page then the results are sculpted into finalized dataframes by other funtions
# Returns a messy list of dataframes that need to be cleaned and parsed
def get_tables_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table')
    dataframes = []
    for table in tables:
        df = pd.read_html(StringIO(str(table)))[0]
        dataframes.append(df)
    return dataframes

# Function that cleans a single dataframe from the get_tables_from_url function. 
# Returnes a clean, parsed dataframe
def clean_and_parse_single_df(dataframe):

    dataframe.columns = dataframe.columns.droplevel(0)
    dataframe.drop('Unnamed: 5_level_1', axis=1, inplace=True)
    
    pattern = r'(?:(?P<name>[A-Z]\.\s?[A-Za-z]+)|(?P<name_def>[A-Za-z]+))\s+(?P<position>[A-Z]{1,3})\s*(?:-\s*(?P<team>[A-Z]{2,3}))?'
    
    def extract_player_info(player):
        match = re.search(pattern, player)
        if match:
            name = match.group('name') or match.group('name_def')
            position = match.group('position')
            team = match.group('team') or None
            return pd.Series({'Name': name, 'Position': position, 'Team': team})
        else:
            return pd.Series({'Name': None, 'Position': None, 'Team': None})

    def extract_stats(stats):
        stats_dict = {'Rec Yds': 0, 'Rec TD': 0, 'Fum': 0, 'Rush Yds': 0, 'Rush TD': 0, 'Pass Yds': 0, 'Pass TD': 0, 'Int': 0}
        if isinstance(stats, str):
            for stat in stats.split(', '):
                parts = stat.split(' ', 1)
                if len(parts) == 2:
                    value, category = parts
                    if value.isdigit() and category in stats_dict:
                        stats_dict[category] = int(value)
                else:
                    # Handle unexpected format here (e.g., log the error, skip the stat, etc.)
                    pass
        return pd.Series(stats_dict)

    player_info = dataframe['Player'].apply(extract_player_info)
    stats_info = dataframe['Stats'].apply(extract_stats)
    dataframe = pd.concat([dataframe, player_info, stats_info], axis=1)
    dataframe = dataframe.drop(['Player', 'Stats'], axis=1)
    
    return dataframe

# Function that iterates through a list of dataframes, calling appropriate cleaning/parsing functions
def clean_matchup_dataframes(dataframe_list):
    # Check if the list is empty
    if not dataframe_list:
        return None, None, None, None
    
    # Check if the list has only 2 items, which means the team has no opponent
    if len(dataframe_list) == 2:
        team1_starter_df, team1_bench_df = dataframe_list
        team2_starter_df, team2_bench_df = None, None
    elif len(dataframe_list) == 4:
        team1_starter_df, team1_bench_df, team2_starter_df, team2_bench_df = dataframe_list
    else:
        raise ValueError("dataframe_list must have either 2 or 4 items")

    # Clean the dataframes
    team1_starter_df = clean_and_parse_single_df(team1_starter_df)
    team1_bench_df = clean_and_parse_single_df(team1_bench_df)
    
    if team2_starter_df is not None and team2_bench_df is not None:
        team2_starter_df = clean_and_parse_single_df(team2_starter_df)
        team2_bench_df = clean_and_parse_single_df(team2_bench_df)

    return team1_starter_df, team1_bench_df, team2_starter_df, team2_bench_df

# Takes a gamecenter url and gets the teamID of the opposing team (hometeamid is in url)
# Returns TeamID as a string
def get_opposing_teamid(url):
    local_response = requests.get(url)
    local_soup = BeautifulSoup(local_response.text, 'html.parser')
    opp_teamids = local_soup.find_all('a', class_='teamName')
    opp_teamids.append('No Opponent This Week')  # Necessary for bye weeks/teams that are out of playoffs
    opp_teamid = None

    if len(opp_teamids) >= 2:
        opp_teamid_element = opp_teamids[1]
        if isinstance(opp_teamid_element, str):
            opp_teamid = opp_teamid_element
        else:
            opp_teamid = opp_teamid_element.get('class')[1].split('-')[1]

    return opp_teamid

# Function that scrapes matchup data (fantasy team names/final scores), as well as
# individual players in the temas lineup/on bench.
# Returns two dataframes,one with matchup data the other with player data
def get_matchup_results_data(url, year):

    # Setting the url and brewing the soup
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # START: MATCHUP DATA SCRAPING
    # Get teams playing and final total scores
    teams_playing_teamnames = []
    for ele in soup.find_all('a', class_='teamName'):
        teams_playing_teamnames.append(ele.text)
    teams_playing_teamnames.append('No Opponent This Week')#Necessary for bye weeks/teams that are out of playoffs
    
    teams_playing_ownerids = []
    for team in teams_playing_teamnames:
        teams_playing_ownerids.append(mapper.get_owner_id(int(year), team))
    
    teams_playing_ownerids.append('No Opponent This Week')#Necessary for bye weeks/teams that are out of playoffs
    
    final_total_scores = []
    for ele in soup.find_all('div', class_='teamTotal'):
        final_total_scores.append(ele.text)
    final_total_scores.append('No Opponent This Week')#Necessary for bye weeks/teams that are out of playoffs

    
    overall_matchup_data = []
         
    overall_matchup_data.append({'team1_Name': teams_playing_teamnames[0], 'team1_Score': final_total_scores[0], 'team1_OwnerID': teams_playing_ownerids[0], 'team2_Name': teams_playing_teamnames[1], 'team2_score': final_total_scores[1], 'team2_OwnerID': teams_playing_ownerids[1]}) 
    
    overall_matchup_df = pd.DataFrame(overall_matchup_data)

    # END: MATCHUP DATA SCRAPING

    # START: PLAYER DATA SCRAPING
    raw_tables = get_tables_from_url(url)
    team1_starter_df, team1_bench_df, team2_starter_df, team2_bench_df = clean_matchup_dataframes(raw_tables)
    player_dataframe = pd.concat([team1_starter_df, team1_bench_df, team2_starter_df, team2_bench_df], ignore_index=True)

    # END: PLAYER DATA SCRAPING



    return overall_matchup_df, player_dataframe
# Function that iterates through years/weeks to process lists and calls construct_url to create master list
# Returns two dataframes, one for matchup overall results, and one with the individual player data
def process_year(year):
    combined_results = []
    combineed_player_data = []
    week_list = weeks_to_process[year]

    for week in week_list:
        team_list = list(teamIds_byyear[year])  # Create a copy of team_list for each week
        print('\n\n\n')
        print(f'Processing Week {week} in Year {year}')
        print(f'Teams to process: {team_list}')
        print(f'weeks to process: {week_list}')
        print('\n\n\n')

        while len(team_list) != 0:
            print(f'Processing team {team_list[0]} for Week {week} in Year {year}')
            local_url = construct_matchup_url(year, week, team_list[0])
            print('URL is: ' + local_url)

            matchup_data = get_matchup_results_data(local_url, year)[0]
            matchup_data['Week'] = week
            matchup_data['Year'] = year
            combined_results.append(matchup_data)
            opposing_teamid = get_opposing_teamid(local_url)

            player_data = get_matchup_results_data(local_url, year)[1]
            player_data['Week'] = week
            player_data['Year'] = year
            combineed_player_data.append(player_data)

             # Handle the case when there is no opponent
            if (opposing_teamid is not None) and (opposing_teamid != 'No Opponent This Week'):
                if int(opposing_teamid) in team_list:
                    team_list.remove(int(opposing_teamid))
                else:
                    print(f"WARNING: Opposing team ID {opposing_teamid} not found in the team list for Week {week} in Year {year}")

            # Remove processed 'home' team
            team_list.pop(0)


    combined_matchup_df = pd.concat(combined_results, ignore_index=True)
    combined_player_df = pd.concat(combineed_player_data, ignore_index=True)
    return combined_matchup_df, combined_player_df


# END Matchup scraping functions

# START Scraping

combined_results_df = pd.DataFrame()
combined_player_df = pd.DataFrame()

for year in years_to_process:
    print(f'Processing Year {year}')
    yearly_results_df, yearly_player_df = process_year(year)

    combined_results_df = pd.concat([combined_results_df, yearly_results_df], ignore_index=True)
    combined_player_df = pd.concat([combined_player_df, yearly_player_df], ignore_index=True)


    combined_results_df.to_csv('SavedData/most_recent_scrapes/historical_results_data.csv', index=False)  
    combined_player_df.to_csv('SavedData/most_recent_scrapes/historical_player_data.csv', index=False)


combined_results_df.to_csv('SavedData/most_recent_scrapes/historical_results_data.csv', index=False)
combined_player_df.to_csv('SavedData/most_recent_scrapes/historical_player_data.csv', index=False)





print('Done.')















