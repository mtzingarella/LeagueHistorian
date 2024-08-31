class PotPick:
    def __init__(self, pick_data, depth, cur_roster):
        """
        Initialize a PotentialDraftPick instance.

        :param pick_data: Data related to the draft pick (e.g., player name, position, etc.)
        """
        self.pick_data = pick_data # What players are left
        self.cur_roster = cur_roster # What players are already on the roster
        self.depth = depth # How many additional paths should stem from this pick
        
        

    def add_potential_pick(self, potential_pick):
        """
        Add a potential pick to the list of potential picks.

        :param potential_pick: An instance of PotentialDraftPick representing a potential pick.
        """
        self.potential_picks.append(potential_pick)
    
    def remove_potential_pick(self, potential_pick):
        """
        Remove a potential pick from the list of potential picks.

        :param potential_pick: An instance of PotentialDraftPick representing a potential pick.
        """
        self.potential_picks.remove(potential_pick)

    def generate_next_pick(self):
        """
        Generate the next potential pick based on the current list of potential picks.

        :return: An instance of PotentialDraftPick representing the next potential pick.
        """
        pass
    

    def __repr__(self):
        """
        Return a string representation of the PotentialDraftPick instance.

        :return: String representation of the pick data.
        """