from api_connect.Api_Calls import get_data_from_api
from api_connect.config import API_BASE_URL
from data.data_transformer import read_excel_to_dataframe, save_to_csv, anonymize_data, process_silver_layer, process_gold_layer, transform_data_for_analysis

import datetime
from datetime import datetime
import pandas as pd


def process_data_layer(layer):
    if layer == "bronze":
        # Read raw data and save without processing
        print(f'{datetime.now()} | Reading Excel data from PDI.xlsx for Bronze layer...')
        raw_data = read_excel_to_dataframe('input_data/PDI.xlsx')
        save_to_csv(raw_data, 'output', filename="PDI_bronze.csv")
        print(f'{datetime.now()} | Bronze layer data saved.')
    elif layer == "silver":
        # Perform light cleaning and anonymization and drop some of the columns
        print(f'{datetime.now()} | Reading Excel data from PDI.xlsx for Silver layer...')
        raw_data = read_excel_to_dataframe('input_data/PDI.xlsx')
        processed_data = anonymize_data(raw_data)
        processed_data = process_silver_layer(processed_data)
        save_to_csv(processed_data, 'output', filename="PDI_silver.csv")
        print(f'{datetime.now()} | Silver layer data saved.')
    elif layer == "gold":
        # Optimize data for analysis
        print(f'{datetime.now()} | Reading Excel data from PDI.xlsx for Gold layer...')
        raw_data = read_excel_to_dataframe('input_data/PDI.xlsx')
        processed_data = anonymize_data(raw_data)
        # optimized_data = transform_to_wide_format(processed_data)
        # optimized_data = transform_data_for_analysis(optimized_data)
        # optimized_data = process_gold_layer(optimized_data)

        optimized_data = process_gold_layer(processed_data)
        save_to_csv(optimized_data, 'output', filename="PDI_gold.csv")
        print(f'{datetime.now()} | Gold layer data saved.')



def main():
    while True:
        layer_to_process = input("Enter data layer to process (bronze, silver, gold) or 'exit' to quit: ")
        if layer_to_process.lower() in ['bronze', 'silver', 'gold']:
            process_data_layer(layer_to_process.lower())
        elif layer_to_process.lower() == 'exit':
            print("Exiting program...")
            break
        else:
            print("Invalid input, try again.")

if __name__ == "__main__":
    main()