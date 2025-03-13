#data handelen
import pandas as pd
import os
import datetime

def read_excel_to_dataframe(file_path):
    """
    Reads an Excel file and returns a DataFrame.
    """
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"{datetime.datetime.now()} | Error reading Excel file: {str(e)}")
        raise

def save_to_csv(data, destination_folder, filename="output.csv"):
    """
    Saves data to a CSV file in the specified folder.
    """
    try:
        os.makedirs(destination_folder, exist_ok=True)
        file_path = os.path.join(destination_folder, filename)
        data.to_csv(file_path, index=False)
        print(f'{datetime.datetime.now()} | Success. Data written to file in "{file_path}".')
    except Exception as e:
        print(f"{datetime.datetime.now()} | Error saving data to CSV: {str(e)}")
        raise
