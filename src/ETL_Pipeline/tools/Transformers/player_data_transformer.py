import pandas as pd

def parse_statline_extended(statline, stat_types):
    """
    Parse the statline string into a dictionary of stats, ensuring all stat types are included.
    """
    # Ensure statline is a string
    statline = str(statline)

    # Split the statline by commas and then by spaces
    stats = statline.split(',')
    parsed_stats = {stat_type: 0 for stat_type in stat_types}  # Initialize all stats with 0

    for stat in stats:
        # Split each stat into its value and type
        parts = stat.strip().split(' ')
        if len(parts) >= 2:
            stat_type = ' '.join(parts[1:])  # Join all parts except the first as stat type
            stat_value = parts[0].strip()

            # Handle cases where stat_value is not a number
            try:
                stat_value = float(stat_value)
            except ValueError:
                stat_value = 0

            parsed_stats[stat_type] = stat_value

    return parsed_stats

def main():
    # Load the CSV file
    file_path = 'src\\ETL_Pipeline\\data\\staged_extracted_data\\historical_player_data.csv'
    data = pd.read_csv(file_path)

    # Identify all unique stat types in the 'StatLine' column
    unique_stats = set()
    for statline in data['StatLine']:
        statline = str(statline)
        stats = statline.split(',')
        for stat in stats:
            parts = stat.strip().split(' ')
            if len(parts) >= 2:
                stat_type = ' '.join(parts[1:])  # Join all parts except the first as stat type
                unique_stats.add(stat_type)

    unique_stats_list = list(unique_stats)
    unique_stats_list.sort()

    # Apply the extended parsing function to the 'StatLine' column
    parsed_statlines_extended = data['StatLine'].apply(lambda x: parse_statline_extended(x, unique_stats_list))

    # Convert the parsed statlines into a DataFrame
    stats_df_extended = pd.DataFrame(parsed_statlines_extended.tolist())

    # Merge the new stats DataFrame with the original data
    merged_data_extended = pd.concat([data, stats_df_extended], axis=1)

    # Drop the original 'StatLine' column
    final_data_extended = merged_data_extended.drop('StatLine', axis=1)

    # Save the modified data to a new CSV file
    output_file_path = 'src\\ETL_Pipeline\\data\\trans_data\\trans_player_data.csv'
    final_data_extended.to_csv(output_file_path, index=False)

    return output_file_path

output_csv = main()
output_csv
