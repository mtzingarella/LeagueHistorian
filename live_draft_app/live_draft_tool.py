import os
from bs4 import BeautifulSoup
import pandas as pd
import time
import threading

class LiveDraftTool:
    def __init__(self, update_frequency, live_data_dir):
        self.update_frequency = update_frequency
        self.live_data_dir = live_data_dir
        self.running = True  # Control flag for the loop

    def process_draft_data(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        picknums = soup.find_all('div', {'class': 'css-146c3p1 r-dnmrzs r-1udh08x r-1udbk01 r-3s2u2q r-1iln25a r-1cvm98q r-jnhe0o r-10x49cs r-1dpkw9 r-1cwl3u0 r-1559e4e r-q4m81j'})
        players = soup.find_all('div', {'class': 'css-175oi2r r-1mlwlqe r-1udh08x r-417010'})
        cleaned_players = []
        teamposs = soup.find_all('div', {'class': 'css-146c3p1 r-1khnkhu r-jnhe0o r-10x49cs r-1dpkw9 r-1f529hi r-q4m81j'})
        fteams = soup.find_all('div', {'class': 'css-146c3p1 r-dnmrzs r-1udh08x r-1udbk01 r-3s2u2q r-1iln25a r-1cvm98q r-jnhe0o r-10x49cs r-1dpkw9 r-56xrmm r-q4m81j'})

        rounds = []
        picks = []
        overpicks = []
        teams = []
        positions = []

        # Split picknums into two lists delimited by .
        for picknum in picknums:
            pick = picknum.text.split('.')
            round_to_add = pick[0].strip('\n').strip(' ')
            rounds.append(round_to_add)
            picks.append(pick[1])
            overpicks.append(picknum.text.strip('()'))

        # Now split picks by the space to get picks on the left and overpick in parentheses on the right
        for i in range(len(picks)):
            pick = picks[i].split(' ')
            picks[i] = pick[0]
            # Ensure there is a second part to process
            if len(pick) > 1:
                # Strip the value stored at pick[1] of the parentheses and any trailing characters
                stripped_value = pick[1].strip('()').strip('\n').strip(' ').strip('()')
                overpicks[i] = stripped_value

        for teampos in teamposs:
            team = teampos.text.split('-')[0].strip()
            pos = teampos.text.split('-')[1].strip()
            teams.append(team)
            positions.append(pos)

        for i in range(len(players)):
            if 'Avatar' in players[i]['aria-label']:
                pass
            else:
                cleaned_players.append(players[i]['aria-label'])

        for i in range(len(fteams)):
            fteam = fteams[i].text
            fteam_str = str(fteam).strip('[\n').strip(' ').strip('\n')
            fteams[i] = fteam_str

        # Fill every list with 'TBD' until it has a length of 288
        while len(rounds) < 288:
            rounds.append('TBD')

        while len(picks) < 288:
            picks.append('TBD')

        while len(overpicks) < 288:
            overpicks.append('TBD')

        while len(teams) < 288:
            teams.append('TBD')

        while len(positions) < 288:
            positions.append('TBD')

        while len(cleaned_players) < 288:
            cleaned_players.append('TBD')

        while len(fteams) < 288:
            fteams.append('TBD')

        # Create a df with the columns Round, Pick, OvrPick, Team, Pos, Player, DraftedBy filled with the lists created above
        df = pd.DataFrame({'Round': rounds, 'Pick': picks, 'OvrPick': overpicks, 'Team': teams, 'Pos': positions, 'Player': cleaned_players, 'DraftedBy': fteams})

        return df

    def read_latest_file(self):
        list_of_files = os.listdir(self.live_data_dir)
        full_paths = [os.path.join(self.live_data_dir, file) for file in list_of_files]
        latest_file = max(full_paths, key=os.path.getctime)

        with open(latest_file, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return html_content

    def run(self):
        while self.running:
            try:
                html_content = self.read_latest_file()
                print("latest file read")
                df = self.process_draft_data(html_content)
                df.to_csv('output/current_draftboard.csv')
                print("df saved")
                time.sleep(self.update_frequency)
            except Exception as e:
                print(f"An error occurred: {e}")
                self.running = False

    def stop(self):
        self.running = False

# Example usage
if __name__ == "__main__":
    update_frequency = 10  # in seconds
    live_data_dir = 'output/html_content'
    live_draft_tool = LiveDraftTool(update_frequency, live_data_dir)

    # Run the tool in a separate thread to allow graceful stopping
    thread = threading.Thread(target=live_draft_tool.run)
    thread.start()

    # Let it run for a certain period or until a condition is met
    time.sleep(60)  # Run for 60 seconds
    live_draft_tool.stop()
    thread.join()
    print("Script finished")