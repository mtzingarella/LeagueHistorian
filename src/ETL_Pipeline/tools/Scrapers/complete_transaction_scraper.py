import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys

sys.path.append('D:\GitRepos\LeagueHistorian\src\Misc_Tools')
from owner_id_mapper import OwnerIDMapper


#------------------------------------------------------------------
#------------------------------------------------------------------
# START Functions for scraping general league data
#------------------------------------------------------------------
#------------------------------------------------------------------

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
    
    current_year = int(years_to_process[0]) + 1
    years_to_process.insert(0, str(current_year)) # History menu does not show current year, but url works the same for draft
    
    return years_to_process

#------------------------------------------------------------------
#------------------------------------------------------------------
# END Functions for scraping general league data
#------------------------------------------------------------------
#------------------------------------------------------------------

#------------------------------------------------------------------
#------------------------------------------------------------------
# START Functions for scraping league transaction pages
#------------------------------------------------------------------
#------------------------------------------------------------------


# Function to build the url where the data of interest is stored
# Returns url as a string
def construct_page_url(year,pagenum):
    offset = (20 * (pagenum - 1)) + 1
    url = f'https://fantasy.nfl.com/league/332843/history/{year}/transactions?offset={offset}'
    print('url is: ' + url )
    return url

# Function to create a list of the transaction dates (formatted as: MMM DD, 00:00 AM/PM)
# Returns a list of strings
def create_trans_date_list(soup):
    trans_date_list = []
    for ele in soup.find_all('td', class_="transactionDate"):
        trans_date = ele.text
        trans_date_list.append(trans_date)
    return trans_date_list

# Function to create a list of the transaction weeks
# Returns a list of strings
def create_trans_week_list(soup):
    trans_week_list = []
    for ele in soup.find_all('td', class_="transactionWeek"):
        trans_week = ele.text
        trans_week_list.append(trans_week)
    return trans_week_list

# Function to create a list of the transaction types
# Returns a list of strings
def create_trans_type_list(soup):
    trans_type_list = []
    for ele in soup.find_all('td', class_="transactionType"):
        trans_type = ele.text
        trans_type_list.append(trans_type)
    return trans_type_list

# Function that helps handle the annoying instances where nfl.com developers decided to insert data into their table in a completely inconsistent format
# Returns a list of booleans stating whether the datapoint needs to be handled differently or not
def create_exception_bool_list(soup):
    # Checks if the transaction type is LM, which puts a long comment as the data for the  PlayerNameandInfo" column
    type_list = create_trans_type_list(soup)
    bool_list = [item == 'LM' for item in type_list]

    return bool_list

# Function to put together a list of names involved in any transaction that includes multiple players (Trades and drops that happen as result of trades)
# Returns a list of lists of strings
def extract_names(soup):
    name_list_list = []
    raw_names_list = []
    class_list = []

    # Pulling names and their associated class from the page (class indicates whether they are the first or last play)
    
    for ele in soup.find_all('td', class_="playerNameAndInfo"):
        if ele.find('li'):
            for subele in ele.find_all('li'):
                for subele2 in subele.find_all('a'):
                    if 'class' in subele2.attrs and 'playerName' in subele2['class']:
                        name = subele2.text
                        raw_names_list.append(name)

                        li_parents = subele2.fetchParents()
                        li_parent = li_parents[1]
              
                        
                        if 'class' in li_parent.attrs:
                            li_class = ''
                            for item in li_parent['class']:
                                li_class = li_class + str(item)
                            class_list.append(li_class)
                        else:
                            class_list.append('None')
                            

    # Parsing the info pulled from page
    
    nm_list = []

    for index, cl in enumerate(class_list):
        
        if cl == 'firstlast':
            nm_list.append(raw_names_list[index])
            name_list_list.insert(index,nm_list)
            nm_list = []
        if cl == 'first':
            nm_list.append(raw_names_list[index])
        if cl == 'None':
            nm_list.append(raw_names_list[index])
        if cl == 'last':
            nm_list.append(raw_names_list[index])
            name_list_list.insert(index,nm_list)
            nm_list = []

    
    # Check if there are any remaining names in the last group

    
    return name_list_list
# Function to create lists of player first and last names
# Returns TWO lists of lists of strings
def create_player_name_list(soup):
    
    multiple_names_list = extract_names(soup) # If any transaction on page contains multiple players, this extarcts it

    fn_list_list = []
    ln_list_list = []

    for ele in soup.find_all('td', class_="playerNameAndInfo"):
        full_name_list = []
        fn_list = []
        ln_list = []
        
        multiple_names = False
        
        if(ele.find('li')):
            multiple_names = True

        if multiple_names:
            full_name_list = multiple_names_list.pop()
            
            for name in full_name_list:
                firstname = str(name).split(' ')[0]
                lastname = str(name).split(' ')[1]
                fn_list.append(firstname)
                ln_list.append(lastname)
            fn_list_list.append(fn_list)
            ln_list_list.append(ln_list)
            
        else:
            firstname = str(ele.text).split(' ')[0]
            lastname = str(ele.text).split(' ')[1]
            fn_list.append(firstname)
            ln_list.append(lastname)
            fn_list_list.append(fn_list)
            ln_list_list.append(ln_list)
                                 

    return fn_list_list, ln_list_list

# Function to create a list of player ids fo0r players on page
# Returns a list of lists of strings
def create_player_id_list(soup):
    player_id_list_list = []

    for ele in soup.find_all('td', class_="playerNameAndInfo"):
        full_name_list = []
        id_list = []  # Create a new id_list for each set of player IDs
        
        multiple_names = False
        
        if ele.find('li'):
            multiple_names = True

        if multiple_names:        
            for subele in ele.find_all('li'):
                for player in subele.find_all('a'):
                    raw_player_id = str(player['class'])
                    if 'playerNameId' in raw_player_id:
                        parse_1_id = raw_player_id.split('-')[1]
                        parse_2_id = parse_1_id.split("'")[0]
                        id_list.append(parse_2_id)
            player_id_list_list.append(id_list)   

        else:
            for player in ele.find_all('a'):
                raw_player_id = str(player['class'])
                if 'playerNameId' in raw_player_id:
                    parse_1_id = raw_player_id.split('-')[1]
                    parse_2_id = parse_1_id.split("'")[0]
                    id_list.append(parse_2_id)
            player_id_list_list.append(id_list)
            
    print(player_id_list_list)
    return player_id_list_list

# Function to create a list of the position the relevant players play
# Returns a list of strings
def create_nfl_pos_list(soup):
    nfl_pos_list = []
    for ele in soup.find_all('td', class_="playerNameAndInfo"):
        pos = str(ele.text).split(' ')[2]
        nfl_pos_list.append(pos)
    return nfl_pos_list

# Function to create a list of the position the player was moved from
# Returns a list of strings
def create_moving_from_list(soup):
    exception_list = create_exception_bool_list(soup)
    moving_from_elements = [ele.text for ele in soup.find_all('td', class_='transactionFrom')]
    
    moving_from_list = []
    
    index = 0
    for is_exception in exception_list:
        if is_exception:
            moving_from_list.append("NA")
        else:
            if index < len(moving_from_elements):  # Safeguard to ensure we don't exceed the list's boundaries
                moving_from_list.append(moving_from_elements[index])
                index += 1
            else:
                moving_from_list.append("NA")  # Append "NA" for missing data
                
    return moving_from_list

# Function to create a list of the ownerid of the team moving player, if applicable
# Returns a list of strings
def create_moving_from_owner_id_list(year, soup):
    exception_list = create_exception_bool_list(soup) # 'LM' type transactions break this code, so we need to handle them differently
   
    moving_from_owner_id_list = []
    moving_from_owner_id_elements = []
    for ele in soup.find_all('td', class_='transactionFrom'):
        moving_from_owner_id_elements.append(ele.text)
    
    ownerids_list = []
    for ele in moving_from_owner_id_elements:
        ownerid = mapper.get_owner_id(int(year),str(ele))
        ownerids_list.append(ownerid)
    
    index = 0
    
    for is_exception in exception_list:
        if is_exception:
            moving_from_owner_id_list.append("NA")
        else:
            if index < len(ownerids_list):  # Safeguard to ensure we don't exceed the list's boundaries
                moving_from_owner_id_list.append(ownerids_list[index])
                index += 1
            else:
                moving_from_owner_id_list.append("NA")  # Append "NA" for missing data
                
    return moving_from_owner_id_list

# Function to create a list of position the player was moved to``
# Returns a list of strings
def create_moving_to_list(soup):
    exception_list = create_exception_bool_list(soup)
    moving_to_elements = [ele.text for ele in soup.find_all('td', class_='transactionTo')]
    
    moving_to_list = []
    
    index = 0
    for is_exception in exception_list:
        if is_exception:
            moving_to_list.append("NA")
        else:
            if index < len(moving_to_elements):
                moving_to_list.append(moving_to_elements[index])
                index += 1
            else:
                moving_to_list.append("NA")
                
    return moving_to_list
# Function to create a list of the ownerid of the team receiving player, if applicable
# Returns a list of strings
def create_moving_to_owner_id_list(year, soup):
    exception_list = create_exception_bool_list(soup) # 'LM' type transactions break this code, so we need to handle them differently
    
    moving_to_owner_id_list = []
    moving_to_owner_id_elements = []
    for ele in soup.find_all('td', class_='transactionTo'):
        moving_to_owner_id_elements.append(ele.text)
    
    ownerids_list = []
    for ele in moving_to_owner_id_elements:
        ownerid = mapper.get_owner_id(int(year),str(ele))
        ownerids_list.append(ownerid)
    
    index = 0
    for is_exception in exception_list:
        if is_exception:
            moving_to_owner_id_list.append("NA")
        else:
            if index < len(moving_to_owner_id_elements):
                moving_to_owner_id_list.append(ownerids_list[index])
                index += 1
            else:
                moving_to_owner_id_list.append("NA")
                
    return moving_to_owner_id_list

# Function to create a list of the ownername of the team executing transaction
# Returns a list of strings
def create_trans_by_owner_name_list(soup):
    trans_by_owner_name_list = []
    for ele in soup.find_all('td', class_='transactionOwner'):
        trans_by_owner_name = ele.find('span').text
        trans_by_owner_name_list.append(trans_by_owner_name)
    return trans_by_owner_name_list

# Function to create a list of the ownerid of the team executing transaction
# Returns a list of strings
def create_trans_by_owner_id_list(year,soup):
    trans_by_owner_id_list = []
    for ele in soup.find_all('td', class_='transactionOwner'):
        trans_by_owner_id = str(ele.find('span').attrs['class']).split('-')[1].split("'")[0]
        trans_by_owner_id_list.append(trans_by_owner_id)
    return trans_by_owner_id_list

#------------------------------------------------------------------
#------------------------------------------------------------------
# END Functions for scraping league transaction pages
#------------------------------------------------------------------
#------------------------------------------------------------------




#------------------------------------------------------------------
#------------------------------------------------------------------
# START Functions for iterating over league history
#------------------------------------------------------------------
#------------------------------------------------------------------


# Function to check whether a page has transactions or not (so the iterator knows when to stop processing a year)
# Returns a boolean
def page_has_content_bool(soup):
    page_status = soup.find('div', class_='statusWrap')

    if page_status is None:
        page_has_transactions = True
    else:
        page_has_transactions = False

    return page_has_transactions

# Function to extract data from single page
# Returns a dataframe
def process_page(year,soup):

    # Extract relevant data from soup into lists
    trans_date_list = create_trans_date_list(soup)
    trans_week_list = create_trans_week_list(soup)
    trans_type_list = create_trans_type_list(soup)
    fn_list, ln_list = create_player_name_list(soup)
    pid_list = create_player_id_list(soup)
    nfl_pos_list = create_nfl_pos_list(soup)
    moving_from_list = create_moving_from_list(soup)
    moving_from_owner_id_list = create_moving_from_owner_id_list(year,soup)
    moving_to_list = create_moving_to_list(soup)
    moving_to_owner_id_list = create_moving_to_owner_id_list(year,soup)
    trans_by_owner_name_list = create_trans_by_owner_name_list(soup)
    trans_by_owner_id_list = create_trans_by_owner_id_list(year,soup)


    # Create a dictionary to hold lists
    data_dict = {
        'trans_date': trans_date_list,
        'trans_week': trans_week_list,
        'trans_type': trans_type_list,
        'first_name': fn_list,
        'last_name': ln_list,
        'player_id': pid_list,
        'nfl_pos': nfl_pos_list,
        'moving_from': moving_from_list,
        'moving_from_owner_id': moving_from_owner_id_list,
        'moving_to': moving_to_list,
        'moving_to_owner_id': moving_to_owner_id_list,
        'trans_by_owner_name': trans_by_owner_name_list,
        'trans_by_owner_id': trans_by_owner_id_list
    }

    # Stick it in a dataframe
    page_df = pd.DataFrame(data_dict)

    time.sleep(0.25) # Be polite to the server

    return page_df

# Function to extract data from entire year
# Returns a dataframe
def process_year(year):

    # Initial values
    curr_page = 1
    curr_url = construct_page_url(year, curr_page)
    response = requests.get(curr_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    year_df = pd.DataFrame()

    # Iterate through pages until they have no content
    while(page_has_content_bool(soup)):
        print('Processing page ' + str(curr_page) + ' of year ' + year)
        curr_url = construct_page_url(year, curr_page)
        response = requests.get(curr_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_df = process_page(year,soup)
        year_df = pd.concat([year_df, page_df])
        curr_page += 1

    year_df['season'] = year

    return year_df

# I will eventually have the leagueid be a variable rather than hardcoded as my personal league
def process_league():

    years_to_process = create_years_to_process_list('https://fantasy.nfl.com/league/332843/history')
    league_df = pd.DataFrame()

    for year in years_to_process:
        year_df = process_year(year)
        league_df = pd.concat([league_df, year_df])
        league_df = league_df.reset_index(drop=True)
        league_df.to_csv(f'SavedData/most_recent_scrapes/complete_transaction_data.csv', index=False)

#------------------------------------------------------------------
#------------------------------------------------------------------
# END Functions for iterating over league history
#------------------------------------------------------------------
#------------------------------------------------------------------

# Call Scraper

#initialize mapper (used by one of scraper functions)
mapper = OwnerIDMapper('SavedData/most_recent_scrapes/owners_by_year_and_ids.csv')

process_league()


print('Done.')




#Troubleshooting code I will probably need again later
'''
curr_url = construct_page_url(2023, 49)
response = requests.get(curr_url)
soup = BeautifulSoup(response.text, 'html.parser')

pil = create_player_id_list(soup)

print(pil)

'''

'''
for ele in soup.find_all('td', class_="playerNameAndInfo"):
    print('FULL STRING: ' + str(ele.text))
    firstname_sublist = []
    lastname_sublist = []
    firstname_sublist.append(str(ele.text).split(' ')[0])
    lastname_sublist.append(str(ele.text).split(' ')[1])
    fn_list.append(firstname_sublist)
    ln_list.append(lastname_sublist)

for ele1, ele2 in zip(fn_list, ln_list):
    print(ele1[0] + ' ' + ele2[0])

'''

