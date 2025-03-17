# main.py
from api_connect.Api_Calls import get_data_from_api
from api_connect.config import API_BASE_URL
from data.data_transformer import read_excel_to_dataframe, save_to_csv
# , anonymize_data

import datetime
from datetime import datetime
import pandas as pd


def main():
    try:
        # Paths to the Excel files
        excel_file_path1 = 'input_data/PDI.xlsx'
        excel_file_path2 = 'input_data/PDI-code-book.xlsx'
        
        print(f'{datetime.now()} | Reading Excel data from PDI.xlsx...')
        raw_data = read_excel_to_dataframe(excel_file_path1)
        
        # Save to CSV in the 'output' directory
        print(f'{datetime.now()} | Saving data to CSV...')
        save_to_csv(raw_data, 'output', filename="PDI.csv")

        # # anonymize
        # raw_data = anonymize_data(raw_data)

        # # Save to CSV in the 'output' directory
        # print(f'{datetime.now()} | Saving anonymized data to CSV...')
        # save_to_csv(raw_data, 'output', filename="PDI_anonymized.csv")
        
        print(f'{datetime.now()} | Reading Excel data from PDI-code-book.xlsx...')
        raw_data2 = read_excel_to_dataframe(excel_file_path2)
        
        # Save to CSV in the 'output' directory
        print(f'{datetime.now()} | Saving data to CSV...')
        save_to_csv(raw_data2, 'output', filename="PDI-code-book.csv")
        
        print(f'{datetime.now()} | Process completed successfully.')
    except Exception as e:
        print(f"{datetime.now()} | An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
