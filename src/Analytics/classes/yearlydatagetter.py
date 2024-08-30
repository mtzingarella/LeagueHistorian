import pandas as pd
from draftreader import DraftReader  # Assuming DraftReader is in a module named draftreader

class YearlyDataGetter:
    def __init__(self, start_year, end_year):
        """
        Initialize the YearComparer with a range of years and a method to run.

        Parameters:
        - start_year: The starting year of the range.
        - end_year: The ending year of the range.
        - method: The method to run on the draft data for each year.
        """
        self.start_year = start_year
        self.end_year = end_year
       

    def load_data_for_year(self, year):
        """
        Load the draft data for a specific year.

        Parameters:
        - year: The year for which to load the draft data.

        Returns:
        - DataFrame containing the draft data for the specified year.
        """
        # Assuming the data is stored in a CSV file named 'complete_draft_data.csv'
        df = pd.read_csv('SavedData/most_recent_scrapes/complete_draft_data.csv')
        print(f"Data for year {year} loaded with columns: {df.columns}")
        return df[df['Year'] == year]
    
    def load_data_for_multiple_years(self, start_year, end_year):
        """
        Load the draft data for a range of years.

        Parameters:
        - start_year: The starting year of the range.
        - end_year: The ending year of the range.

        Returns:
        - DataFrame containing the draft data for the specified range of years.
        """
        # Assuming the data is stored in a CSV file named 'complete_draft_data.csv'
        df = pd.read_csv('SavedData/most_recent_scrapes/complete_draft_data.csv')
        print(f"Data for years {start_year}-{end_year} loaded with columns: {df.columns}")
        return df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]



            

