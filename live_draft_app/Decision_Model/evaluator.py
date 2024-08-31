class Evaluator:
    def __init__(self, pick_data, cur_roster):
        """
        Initialize a PotentialDraftPick instance.

        :param pick_data: Data related to the draft pick (e.g., player name, position, etc.)
        """
        self.pick_data = pick_data # What players are left
        self.cur_roster = cur_roster # What players are already on the roster      
        

    def rank_remaining_players(self):
        """
        Rank the remaining players based on some criteria.

        :return: A list of player names in ranked order.
        """
        pass
       
