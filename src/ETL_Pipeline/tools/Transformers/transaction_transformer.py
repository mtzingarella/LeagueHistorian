

import pandas as pd


def parse_transactions(data):
    
    # Add a unique transaction ID
    data['trans_id'] = pd.factorize(data['trans_date'] + data['trans_type'] + data['trans_by_owner_id'].astype(str))[0] + 1

    # Identifying columns that contain lists (assuming they are stored as strings)
    list_columns = [col for col in data.columns if data[col].apply(lambda x: isinstance(x, str) and x.startswith('[') and x.endswith(']')).any()]

    # Expanding rows for each item in the list for the identified columns
    for col in list_columns:
        # Convert string representation of list to actual list
        data[col] = data[col].apply(lambda x: eval(x) if isinstance(x, str) and x.startswith('[') and x.endswith(']') else [x])

        # Explode the DataFrame on this column
        data = data.explode(col)

    return data


    return data

def main():
    # Load the CSV file
    file_path = 'src\\ETL_Pipeline\\data\\staged_extracted_data\\complete_transaction_data.csv'  # Replace with your actual file path
    data = pd.read_csv(file_path)

    # Parse the transactions
    parsed_results = parse_transactions(data)

    # Save the modified data to a new CSV file
    output_file_path = 'src\\ETL_Pipeline\\data\\trans_data\\trans_transaction_data.csv'  # Replace with your desired output path
    parsed_results.to_csv(output_file_path, index=False)

    return parsed_results

output_csv = main()

output_csv
