import pandas as pd
import sys
sys.path.append('src/Analytics/classes')
from draftreader import DraftReader
from yearlydatagetter import YearlyDataGetter








# Load the draft data
draft_data = pd.read_csv('SavedData/most_recent_scrapes/complete_draft_data.csv')


# Create an instance of YearComparer with the range of years and method
datagetter = YearlyDataGetter(2018, 2023)


df = datagetter.load_data_for_year(2023)
draft_reader = DraftReader(df)
draft_reader.plots_positions()

