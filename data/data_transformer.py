import pandas as pd
import os
import hashlib
from datetime import datetime
import sqlite3
import subprocess

def log(message):
    """Log messages to console and a daily log file."""
    timestamp = datetime.now()
    log_entry = f"{timestamp} | {message}"


    print(log_entry)

    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"output_log_{datetime.now().date()}.txt")

    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry + '\n')

def identify_structure(df):
    return 'codebook' if 'answer_codes' in df.columns else 'pdi'

def read_excel_files(input_dir):
    pdi_dfs, codebook_dfs = [], []

    for filename in os.listdir(input_dir):
        if filename.endswith(".xlsx"):
            try:
                path = os.path.join(input_dir, filename)
                log(f"Reading Excel file: {filename}")
                df = pd.read_excel(path)

                if identify_structure(df) == 'pdi':
                    pdi_dfs.append(df)
                else:
                    codebook_dfs.append(df)
            except Exception as e:
                log(f"[ERROR] Failed to load {filename}: {e}")

    return (
        pd.concat(pdi_dfs, ignore_index=True) if pdi_dfs else pd.DataFrame(),
        pd.concat(codebook_dfs, ignore_index=True) if codebook_dfs else pd.DataFrame()
    )

def save_to_csv(df, output_dir, filename):
    try:
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, filename)
        df.to_csv(path, index=False)
        log(f"Saved CSV: {path}")
    except Exception as e:
        log(f"[ERROR] Failed to save CSV {filename}: {e}")

def save_to_sqlite(df, db_path, table_name):
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        log(f"Saved to SQLite table: {table_name}")
    except Exception as e:
        log(f"[ERROR] Failed to write to SQLite ({table_name}): {e}")

def calculate_age(row, reference_date):
    try:
        birth_date = datetime(int(row['grs_birthyear']), int(row['grs_birthmonth']), 15)
        return int((reference_date - birth_date).days // 365.25)
        # age = int((reference_date - birth_date).days // 365.25)
        # if age < 0:
        #     return "Invalid"
        # elif age <= 10:
        #     return "0-10"
        # elif age <= 17:
        #     return "11-17"
        # elif age <= 24:
        #     return "18-24"
        # elif age <= 34:
        #     return "25-34"
        # elif age <= 44:
        #     return "35-44"
        # elif age <= 54:
        #     return "45-54"
        # elif age <= 64:
        #     return "55-64"
        # elif age <= 74:
        #     return "65-74"
        # elif age <= 84:
        #     return "75-84"
        # else:
        #     return "85+"
    except:
        return None

def process_silver_layer(df):
    if df.empty:
        log("Skipping silver/gold processing — input DataFrame is empty.")
        return df

    try:
        log("Starting transformation for Silver/Gold layer...")

        if 'respondentid' in df.columns:
            df['respondentid'] = df['respondentid'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:10])

        if 'grs_birthyear' in df.columns and 'grs_birthmonth' in df.columns:
            if 'gto_completion_time' in df.columns:
                df['gto_completion_time'] = pd.to_datetime(df['gto_completion_time'], errors='coerce')
                df['age'] = df.apply(lambda row: calculate_age(row, row['gto_completion_time']), axis=1)

        if 'gto_id_survey' not in df.columns:
            df['gto_id_survey'] = 'unknown'

        drop_cols = [
            'gto_id_relation', 'organizationid', 'consentcode', 'gto_start_time',
            'gto_valid_until', 'startlanguage', 'lastpage', 'gto_id_token',
            'grs_birthyear', 'grs_birthmonth', 'Geboortedatum'
        ]
        df.drop(columns=drop_cols, errors='ignore', inplace=True)

        rename_cols = {
            'gto_round_order': 'round_order',
            'gto_round_description': 'round_description',
            'gtr_track_name': 'track_name',
            'gr2t_track_info': 'track_info',
            'gto_completion_time': 'completion_time',
            'gto_valid_from': 'valid_from',
            'grs_gender': 'Gender',
            'gto_id_survey': 'id_survey',
            'gr2o_patient_nr': 'patient_nr'
        }
        df.rename(columns=rename_cols, inplace=True)

        keys = ['respondentid', 'resptrackid', 'round_description']
        if all(col in df.columns for col in keys):
            df = df.sort_values(by='completion_time', ascending=True)
            df = df.groupby(keys, as_index=False).tail(1)

        baseline = ['patient_nr', 'respondentid', 'resptrackid', 'track_name',
                    'track_info', 'round_description', 'age', 'Gender']
        rest = [col for col in df.columns if col not in baseline]
        ordered_cols = baseline + sorted(rest)
        df = df[[col for col in ordered_cols if col in df.columns]]

        log("Silver/Gold transformation completed.")
        return df

    except Exception as e:
        log(f"[ERROR] Silver/Gold transformation failed: {e}")
        return df

def process_gold_layer(df):
    df = process_silver_layer(df)

    score_columns = [f"V{i}_SQ001" for i in range(1, 8)]

    if all(col in df.columns for col in score_columns):
        try:
            for col in score_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df["PDIscore"] = df[score_columns].sum(axis=1, skipna=True)

            def interpret_score(score):
                if pd.isna(score): return None
                if score <= 23: return "Weinig beperking"
                elif 24 <= score <= 46: return "Redelijke beperking"
                else: return "Forse beperking"

            df["score_level"] = df["PDIscore"].apply(interpret_score)
            log("PDIscore and interpretation added to Gold layer.")
        except Exception as e:
            log(f"[ERROR] Failed during PDIscore calculation: {e}")
    else:
        log("[!] Missing V1_SQ001 to V7_SQ001 columns. PDIscore skipped.")

    return df

def save_tracks(df, output_dir, db_path=None):
    if 'track_name' not in df.columns:
        log("[!] 'track_name' column not found — skipping track export.")
        return

    unique_tracks = df['track_name'].dropna().unique()

    for track in unique_tracks:
        try:
            subset = df[df['track_name'] == track]
            safe_name = track.replace(" ", "_").replace("/", "_")
            filename = f"{safe_name}.csv"
            save_to_csv(subset, output_dir, filename)

            if db_path:
                save_to_sqlite(subset, db_path, safe_name)
                log(f"Track '{track}' saved to SQLite.")
        except Exception as e:
            log(f"[ERROR] Failed to export track '{track}': {e}")

def transform_to_wide_format(df):
    if df.empty or 'respondentid' not in df.columns or 'track_name' not in df.columns or 'PDIscore' not in df.columns:
        log("Wide format skipped — missing required columns.")
        return pd.DataFrame()

    try:
        log("Starting wide format transformation...")

        df = df.sort_values(by='completion_time', ascending=True)
        wide_rows = []

        
        for respondent_id, group in df.groupby('respondentid'):
            row = {
                'respondentid': respondent_id,
                'Gender': group['Gender'].iloc[0] if 'Gender' in group.columns else None,
                'age': group['age'].iloc[0] if 'age' in group.columns else None
            }

           
            for i, (_, record) in enumerate(group.iterrows(), start=1):
                row[f'traject_{i}'] = record.get('track_name', '')
                row[f'score_{i}'] = record.get('PDIscore', '')

            wide_rows.append(row)

        wide_df = pd.DataFrame(wide_rows)
        log("Wide format transformation completed.")
        return wide_df

    except Exception as e:
        log(f"[ERROR] Wide format transformation failed: {e}")
        return pd.DataFrame()


