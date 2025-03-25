#data_transformer.py
import pandas as pd
import os
import datetime
from datetime import datetime
import hashlib

def read_excel_to_dataframe(file_path):
    """
    Reads an Excel file and returns a DataFrame.
    """
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"{datetime.now()} | Error reading Excel file: {str(e)}")
        raise

def save_to_csv(data, destination_folder, filename="output.csv"):
    """
    Saves data to a CSV file in the specified folder.
    """
    try:
        os.makedirs(destination_folder, exist_ok=True)
        file_path = os.path.join(destination_folder, filename)
        data.to_csv(file_path, index=False)
        print(f'{datetime.now()} | Success. Data written to file in "{file_path}".')
    except Exception as e:
        print(f"{datetime.now()} | Error saving data to CSV: {str(e)}")
        raise





def anonymize_data(df):
    """Anonymizes respondent IDs and converts birth dates into correct age (month-sensitive)"""
    print(f'{datetime.now()} | Data anonymization started...')

    # Hash respondent ID
    if 'respondentid' in df.columns:
        df['respondentid'] = df['respondentid'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:10])
        # print(f"{df['respondentid']}")

    # Calculate age based on year and month
    current_year = datetime.now().year
    current_month = datetime.now().month

    if 'grs_birthyear' in df.columns and 'grs_birthmonth' in df.columns:
        df['age'] = df.apply(lambda row: 
            (current_year - row['grs_birthyear'] - 1) if row['grs_birthmonth'] > current_month else
            (current_year - row['grs_birthyear']), axis=1)
        
        
        # Remove birth year and birth month after calculation
        df.drop(columns=['grs_birthyear', 'grs_birthmonth'], inplace=True, errors='ignore')

    print(f'{datetime.now()} | Anonymization completed.')
    return df



def transform_to_wide_format(df):
    # An example of transforming data from long format to wide format (gold)
    # wide_df = df.pivot(index='respondentid', columns='variable', values='value')
    # return wide_df
    return df

def transform_data_for_analysis(df):
    # logic to transform the data for analysis (gold).
    # Dit is een placeholder voor eventuele transformatieprocessen.
    return df

def process_silver_layer(df):
   # delete irrelivant variables for the Silver layer
    columns_to_exclude = ['gto_id_relation', 'organizationid', 'consentcode', 'gto_start_time', 'gto_valid_until', 'startlanguage', 'lastpage', 'gto_id_token']
    df = df.drop(columns=columns_to_exclude, errors='ignore')
    return df

def process_gold_layer(df):
    # Process the data for the Gold layer including wide format transformation
    columns_to_exclude = ['gto_id_relation', 'organizationid', 'consentcode', 'gto_start_time', 'gto_valid_until', 'startlanguage', 'lastpage', 'gto_id_token']
    df = df.drop(columns=columns_to_exclude, errors='ignore')
    df = transform_to_wide_format(df)
    return df
