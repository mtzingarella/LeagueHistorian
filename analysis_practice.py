import os
import pandas as pd

save_path = os.path.join(os.getcwd(), 'SavedData', 'most_recent_scrapes')

# Read all csv's from save path into dataframes
dfs = {}
for file in os.listdir(save_path):
    if file.endswith('.csv'):
        name = file.split('.')[0]
        dfs[name] = pd.read_csv(os.path.join(save_path, file))

owners_df = dfs['complete_owners_by_year_and_ids']
draft_df = dfs['complete_draft_data']
transactions_df = dfs['complete_transaction_data']
player_stats_df = dfs['historical_player_data']
results_df = dfs['historical_results_data']

trade_df = transactions_df[transactions_df['trans_type'] == 'Trade']
trade_df = trade_df[trade_df['season'] == 2019]


pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
print(trade_df[['season','trans_date','last_name','moving_from', 'moving_to',]])
print()

