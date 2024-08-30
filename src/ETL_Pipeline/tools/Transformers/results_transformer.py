import pandas as pd

def parse_results(data):
    """
    Placeholder, will write in future if necessary 
    """

    parsed_results = pd.DataFrame()

    return parsed_results

def main():
    # Load the CSV file
    file_path = 'src\\ETL_Pipeline\\data\\staged_extracted_data\\historical_results_data.csv'
    data = pd.read_csv(file_path)
    parsed_results = parse_results(data)

    # Save the modified data to a new CSV file
    output_file_path = 'src\\ETL_Pipeline\\data\\trans_data\\trans_results_data.csv'
    data.to_csv(output_file_path, index=False)

    return parsed_results

output_csv = main()
output_csv
