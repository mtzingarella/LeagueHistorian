import pandas as pd
import matplotlib.pyplot as plt

class DraftReader:
    def __init__(self, draft_data):
        """
        Initialize the DraftReader with draft data.

        Parameters:
        - draft_data: DataFrame containing the draft data.
        """
        self.draft_df = draft_data

    def plots_positions(self):
        """
        Create a figure with 6 rectangles, each containing a specified number of dots colored based on the draft data.
        """
        fig, ax = plt.subplots(1, 6, figsize=(12, 6), subplot_kw={'aspect': 'equal'})
        fig.patch.set_facecolor('#2E2E2E')  # Dark background for the figure

        labels = ["QB", "RB", "WR", "TE", "DEF", "K"]
        dots_per_side_x = 16
        dots_per_side_y = 18

        for i in range(6):
            ax[i].set_facecolor('#2E2E2E')  # Dark background for the axes
            ax[i].set_title(labels[i], color='white', fontsize=14)

            # Calculate the positions of the dots
            for x in range(dots_per_side_x):
                for y in range(dots_per_side_y):
                    dot_index = y * dots_per_side_x + x
                    color = 'grey'  # Default color
                    if dot_index < len(self.draft_df):
                        round_num = y + 1
                        pick_num = x + 1
                        player_pos = labels[i]
                        # Check if the position matches the round and picknum
                        if ((self.draft_df['Round'] == round_num) & (self.draft_df['PickNum'] == pick_num) & (self.draft_df['PlayerPos'] == player_pos)).any():
                            color = 'green'
                    ax[i].plot(x, y, 'o', color=color, markersize=4, alpha=0.8)

            # Set limits and label the vertical axis
            ax[i].set_xlim(-0.5, dots_per_side_x - 0.5)
            ax[i].set_ylim(-0.5, dots_per_side_y - 0.5)
            ax[i].set_xticks(range(dots_per_side_x))
            ax[i].set_yticks(range(dots_per_side_y))
            ax[i].set_xticklabels(range(1, dots_per_side_x + 1))
            ax[i].set_yticklabels(range(1, dots_per_side_y + 1))
            ax[i].invert_yaxis()  # Invert the y-axis
        
        plt.tight_layout()
        plt.subplots_adjust(wspace=0.4)  # Adjust the width space between subplots
        plt.show()