import pandas as pd

# Create sample data
data = {
    'round': [i // 16 + 1 for i in range(288)],
    'picknum': [i % 16 + 1 for i in range(288)],
    'roundpick': [i + 1 for i in range(288)],
    'username': [f'User{i % 16 + 1}' for i in range(288)],
    'playername': [f'Player{i + 1}' for i in range(288)],
    'playerpos': ['WR', 'RB', 'QB', 'TE', 'DEF', 'K'] * 48,
    'nflteam': [f'Team{i % 32 + 1}' for i in range(288)]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save DataFrame as CSV
df.to_csv('draft_data.csv', index=False)