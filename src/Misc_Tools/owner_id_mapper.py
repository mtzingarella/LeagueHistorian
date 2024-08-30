import pandas as pd

# Handy dandy tool for converting between different identifiers for teams/owners

# I made this on the hefty assumption that NFL.com does not let people have multiple teams of the same name in their league. 
# If you are here because this is breaking it probably means that a team name is somehow associated with multiple ownerIDs in the csv (co-owners should not break it, though)

class OwnerIDMapper:

    def __init__(self, csv_path):
        # Read the CSV file into a DataFrame object
        self.df = pd.read_csv(csv_path)
        
        # Set the year and ownerteamname columns as the index
        self.df.set_index(['Year', 'OwnerTeamName'], inplace=True)
        
    def get_owner_id(self, year, ownerteamname):
        try:
            return str(int(self.df.loc[year, ownerteamname]['OwnerID']))
        except KeyError:     
            return None  
        
    #IMPORTANT: TeamIDs are recycled and only unique within a given year  
    def get_team_id_foryear(self, year, ownerteamname):
        try:
            return self.df.loc[year, ownerteamname]['OwnerTeamID']
        except KeyError:     
            return None
        
    #Returns list of teamIDs for a given year
    def get_all_teams_for_year(self, year):
        team_list = []
        for team in self.df.loc[year]['OwnerTeamID']:
            team_list.append(team)
        return team_list

        
    def get_data_frame(self):
        return self.df