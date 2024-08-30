import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from owner_id_mapper import OwnerIDMapper

# Scrapes the final scores of a matchup as well as the individual points scored by players in matchup/on bench for entirety of leagues history
# except the current year 

# Essentially works by scraping info about the league from a 
# few key pages then using the info gathered to construct a set of matchup urls
# which are iterated over to extract the data of interest

# Must run AFTER historical_owners_id_scraper because the mapper depends on the csv created by that script


#------------------------------------------------------------------
#------------------------------------------------------------------
# START Functions for scraping general league data
#------------------------------------------------------------------
#------------------------------------------------------------------
#--The following functions scrape the info that varies from league to
#--league such as the number of teams, the number of weeks the league was
#--active each season, etc.


# Function that returns a list of the years the league has data for
# Returns a list of strings
def create_years_to_process_list(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    season_menu = soup.find('div', class_='st-menu')
    years = re.findall(r'\D(\d{4})(?:\D|$)', season_menu.text) #Regex to find all 4 digit numbers in the season menu text
    years_to_process = []
    years_to_process.append(season_menu.text[:4]) #Code above fails to get most recent year due to webpage formatting inconsistency so I sloppily append it in here
    #Append remaining years
    for year in years:
        years_to_process.append(year)
    
    return years_to_process

# Function that finds the weeks where the league had matchups in each year
# Returns a dictionary: Key: Year, Value: List of week numbers 
def create_weeks_to_process_by_year_dict(years_to_process):
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
    return weeks_to_process

# Function to find the teamIDs present in each year, needed for gamecenter urls
# Returns a dictionary of teamIDs present for each: 
def create_teamIds_by_year_dict(years_to_process, mapper):
    teamIds_byyear = {}
    for year in years_to_process:
        teamIds_byyear[year] = mapper.get_all_teams_for_year(int(year))
    return teamIds_byyear

#------------------------------------------------------------------
#------------------------------------------------------------------
# END Functions for scraping general league data
#------------------------------------------------------------------
#------------------------------------------------------------------

#------------------------------------------------------------------
#------------------------------------------------------------------
# START Functions for scraping matchups data
#------------------------------------------------------------------
#------------------------------------------------------------------
#--The following functions are used for processing the gamecenter pages
#--which contain data on the lineup of each fantasy team owner and the points scored
#--by those players for the week.
#--Some of the functions listed last depend upon the functions defined before them.


# Function to build the url where the data of itnerest is stored
# Returns url as a string
def construct_matchup_url(year, week,teamID):
    url_stem = 'https://fantasy.nfl.com'
    url = f'{url_stem}/league/332843/history/{year}/teamgamecenter?teamId={teamID}&week={week}'
    return url

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

# Function to scrape 'POS' column (position in FANTASY lineup)
# Returns a list
def create_pos_list(soup):
    pos_list = []
    for ele in soup.find_all('tr'):
        attr_string = str(ele.attrs)
        position_split = [part.split("-") for part in attr_string.split("'")]
        if(len(position_split[3]) > 1):
            position = str(position_split[3][1])
            pos_list.append(position)
    return pos_list

# Function that scrapes ids of players started at each lineup position on page, including empty slots
# which are reported as '--empty--'
# Returns a list
def create_id_list(soup):
    id_list = []
    for ele in soup.find_all('tr'):
        for sub_ele in ele.findChildren('td', class_='playerNameAndInfo'):
            if(sub_ele.text == '--empty--'):
                id_list.append('--empty--')
            else:
                player_id = str(sub_ele.findChildren('a',class_='playerCard')[0].attrs['href']).split('=')[-1]
                id_list.append(player_id)
    return id_list

# Function that returns a list of the names of players started at each position on page, including empty slots 
# which are reported as '--empty--'
def create_player_name_list(soup):
    player_name_list = []
    # Create a list of lists which contain some combination of the following elements:
        # Player name with first intitial at index 0, last name at index 1
        # '--empty--' at index 0 with no other elements (player not started at lineup position)
        # Defense with the team name at index 0 and 'DEF' at index 1
    for ele in soup.find_all('tr'):
        player_name_list_split = []
        player_name_info = ele.findChildren('td', class_ = 'playerNameAndInfo')

        # Process the list made above into a simpler format
        for ele in player_name_info:
            player_name_list_split.append(str(ele.text).split(' ')[0:2])
        for ele in player_name_list_split:
            if((len(ele) == 2) and (ele[1] != 'DEF')):
                name = ele[0] + ' ' + ele[1]
                player_name_list.append(name)
            elif((len(ele) == 2) and (ele[1] == 'DEF')):
                player_name_list.append(ele[0])
            else:
                player_name_list.append(ele[0])
    return player_name_list

# Function that extracts total fantasy points scored by each player
# Returns a list of strings
def create_fantasy_points_list(soup):
    fantasy_points_list = []
    for ele in soup.find_all('tr'):
        for sub_ele in ele.findChildren('td', class_='stat'):
            fantasy_points = sub_ele.text
            fantasy_points_list.append(fantasy_points)
    return fantasy_points_list

# Function that extracts a long string of stats for each player to be parsed in a later module
# Returns a list of strings (with stats separated by commas in the string)
def create_statline_list(soup):
    # These stats could be parsed now, but to keep the scraper fast it is done later when refining the scraped data
    statline_list = []

    for ele in soup.find_all('td', class_='playerStats'): 
        statline_list.append(ele.text)
        
    return statline_list

# Function that gets the owner ids for specified team involved in matchup
# Returns the team owner's id or 'No Opponent' if team2 is requested where there is no opponent
def get_ownerid(team_number, soup):

    owner_id_list = []

    for ele in soup.find_all('span', class_='userName'):
        owner_id_list.append(str(ele.attrs).split('-')[-1].split("'")[0])

    if team_number == 1:
        ownerid = owner_id_list[0]

    elif team_number == 2 and len(owner_id_list) > 1:
        ownerid = owner_id_list[1]
    else:
        ownerid = 'No Opponent'

    
    return ownerid

# Function that gets the owner names for specified team involved in matchup
# Returns the team owner's name or 'No Opponent' if team2 is requested where there is no opponent
def get_matchup_owner_names(team_number, soup):

    owner_name_list = []

    for ele in soup.find_all('span', class_='userName'):
        owner_name_list.append(str(ele.text))
    
    if team_number == 1:
        owner_name = owner_name_list[0]
    elif team_number == 2 and len(owner_name_list) > 1:
        owner_name = owner_name_list[1]
    else:
        owner_name = 'No Opponent'

    return owner_name

# Function that gets the total score for a specified team involved in matchup
# Returns the total score for the team or 'No Opponent' if team2 is requested where there is no opponent
def get_matchup_total_scores(team_number, soup):
    team_scores = []

    for ele in soup.find_all('div', class_='teamTotal'):
        team_scores.append(str(ele.text))
    
    if team_number == 1:
        total_score = team_scores[0]
    elif team_number == 2 and len(team_scores) > 1:
        total_score = team_scores[1]
    else:
        total_score = 'No Opponent'

    return total_score

# Function that processes a single matchup
# Returns two dataframes,one with matchup data the other with player data
def process_matchup(url,week,year):
# Extracts the data from the matchup url into a dict of lists, then creates dataframes

    # Brewing the soup
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # ===========START: PLAYER DATA SCRAPING==================== 
    pos_list = create_pos_list(soup)
    player_name_list = create_player_name_list(soup)
    id_list = create_id_list(soup)
    fantasy_points_list = create_fantasy_points_list(soup)
    statline_list = create_statline_list(soup)
    owner_id = get_ownerid(1, soup)
    opponent_owner_id = get_ownerid(2, soup)

    # Also contains the week and year which are added to df by the process week/year functions prior to merging
    player_data_dict = {
        'POS': pos_list,
        'PlayerName': player_name_list,
        'PlayerID': id_list,
        'FantasyPoints': fantasy_points_list,
        'StatLine': statline_list,
        'OwnerID': owner_id,
        'OpponentOwnerID': opponent_owner_id
    }

    single_matchup_player_df = pd.DataFrame(player_data_dict)
    #===========END: PLAYER DATA SCRAPING====================

    # ===========START: MATCHUP DATA SCRAPING====================
    owner_name_list = []
    owner_name_list.append(get_matchup_owner_names(1, soup)) #Should only be one value but keeping a list to make dataframe construction more readable
    owner_id_list = []
    owner_id_list.append(get_ownerid(1, soup))
    opponent_id_list = []
    opponent_id_list.append(get_ownerid(2, soup))
    opponent_name_list = []
    opponent_name_list.append(get_matchup_owner_names(2, soup))
    team_score_list = []
    team_score_list.append(get_matchup_total_scores(1, soup))
    opponent_score_list = []
    opponent_score_list.append(get_matchup_total_scores(2, soup))

    matchup_data_dict = {
        'TeamName': owner_name_list,
        'OwnerID': owner_id_list,
        'OpponentName': opponent_name_list,
        'OpponentID': opponent_id_list,
        'TeamScore': team_score_list,
        'OpponentScore': opponent_score_list,
        'Week': week,
        'Year': year
    }

    single_matchup_results_df = pd.DataFrame(matchup_data_dict)
    # ===========END: MATCHUP DATA SCRAPING====================



    return single_matchup_results_df, single_matchup_player_df

# Function that iterates through matchups in a week and calls process_matchup
def process_week(year, week, team_list):
    local_team_list = team_list.copy()
    single_week_player_df = pd.DataFrame()
    single_week_results_df = pd.DataFrame()
        
    # Iterate through the list of teamIDs that need to be processed
    while len(local_team_list) != 0:
        print(f'Processing team {local_team_list[0]} for Week {week} in Year {year}')
        curr_matchup_url = construct_matchup_url(year, week, local_team_list[0])
        print('URL is: ' + curr_matchup_url)

    
        single_matchup_results_df, single_matchup_player_df = process_matchup(curr_matchup_url,week, year)

        # merge the matchup dataframes with the weekly dataframes
        single_week_player_df = pd.concat([single_week_player_df, single_matchup_player_df], ignore_index=True)
        single_week_results_df = pd.concat([single_week_results_df, single_matchup_results_df], ignore_index=True)

        # Remove processed teams from list
        opposing_teamid = get_opposing_teamid(curr_matchup_url)
        # Handle the case when there is no opponent
        if (opposing_teamid is not None) and (opposing_teamid != 'No Opponent This Week'):
            if int(opposing_teamid) in local_team_list:
                local_team_list.remove(int(opposing_teamid))
            else:
                print(f"WARNING: Opposing team ID {opposing_teamid} not found in the team list for Week {week} in Year {year}")

        # Remove processed 'home' team
        local_team_list.pop(0)
    
    single_week_player_df['Week'] = week
    single_week_results_df['Week'] = week
        

    return single_week_results_df, single_week_player_df

# Function that iterates through weeks in a year and calls process_week
# Returns two dataframes, one for matchup overall results, and one with the individual player data
def process_year(year, weeks_to_process, teamIds_byyear):

    # Declaring dataframes which will be concatinated/reassigned as necessary as the function iterates 
    single_year_results_df = pd.DataFrame()
    single_year_player_df = pd.DataFrame()

    week_list = weeks_to_process[year]

    single_week_results_df = pd.DataFrame()
    single_week_player_df = pd.DataFrame()

    
    for week in week_list:
        team_list = teamIds_byyear[year]  # Create a copy of team_list for each week
        print('\n\n\n')
        print(f'Processing Week {week} in Year {year}')
        print(f'Teams to process: {team_list}')
        print(f'weeks to process: {week_list}')
        print('\n\n\n')
        single_week_results_df, single_week_player_df = process_week(year, week, team_list)

        single_year_results_df = pd.concat([single_week_results_df, single_year_results_df], ignore_index=True)
        single_year_player_df = pd.concat([single_week_player_df, single_year_player_df], ignore_index=True)
    
    
    single_year_results_df['Year'] = year
    single_year_player_df['Year'] = year

    return single_year_results_df, single_year_player_df


#------------------------------------------------------------------
#------------------------------------------------------------------
# END Functions for scraping matchups data
#------------------------------------------------------------------
#------------------------------------------------------------------

# START Calling the scraper functions

mapper = OwnerIDMapper('SavedData/most_recent_scrapes/complete_owners_by_year_and_ids.csv')
complete_historical_results_df = pd.DataFrame()
complete_historical_player_df = pd.DataFrame()

years_to_process = create_years_to_process_list('https://fantasy.nfl.com/league/332843/history')

weeks_to_process_by_year = create_weeks_to_process_by_year_dict(years_to_process)

teamIds_byyear = create_teamIds_by_year_dict(years_to_process, mapper)

for year in years_to_process:

    results_df, player_df = process_year(year, weeks_to_process_by_year, teamIds_byyear)
    complete_historical_results_df = pd.concat([complete_historical_results_df, results_df], ignore_index=True)
    complete_historical_player_df = pd.concat([complete_historical_player_df, player_df], ignore_index=True)
    complete_historical_results_df.to_csv('SavedData/most_recent_scrapes/historical_results_data.csv', index=False)
    complete_historical_player_df.to_csv('SavedData/most_recent_scrapes/historical_player_data.csv', index=False)

complete_historical_results_df.to_csv('SavedData/most_recent_scrapes/historical_results_data.csv', index=False)
complete_historical_player_df.to_csv('SavedData/most_recent_scrapes/historical_player_data.csv', index=False)





print('Done.')

# END















