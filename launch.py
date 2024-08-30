
from directed_continous_scraper import DirectedContinuousScraper
from live_draft_tool import LiveDraftTool


login_url = 'https://fantasy.nfl.com'
update_frequency = 10  # in seconds
output_dir = 'output'
live_data_dir = 'SavedData/draftclient/livedata'
live_draft_tool = LiveDraftTool(login_url, update_frequency, live_data_dir)
dcs = DirectedContinuousScraper(login_url, update_frequency, output_dir)
dcs.scrape(update_frequency, live_data_dir, output_dir, live_draft_tool)
