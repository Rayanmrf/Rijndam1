#main.py
import pandas as pd
import os
from datetime import datetime
import subprocess
import webbrowser
from dashboard.setup_streamlit_config import configure_streamlit
from data.data_transformer import(
    read_excel_files,
    save_to_csv,
    save_to_sqlite,
    process_silver_layer,
    process_gold_layer,
    save_tracks,
    transform_to_wide_format,
    log)


def main():
    input_dir = 'input_data'
    output_dir_csv = 'output_csv'
    output_dir_db = 'output_database'
    db_path = os.path.join(output_dir_db, 'output_db.db')
    configure_streamlit()


    try:
        # Clear previous log (only once, at the beginning)
        log_dir = 'logs'
        log_path = os.path.join(log_dir, f"output_log_{datetime.now().date()}.txt")
        if os.path.exists(log_path):
            os.remove(log_path)

        log("ETL pipeline started.")

        # Step 1: Read Excel files
        try:
            pdi_data, codebook_data =read_excel_files(input_dir)
        except Exception as e:
            log(f"[ERROR] Failed to read Excel files: {e}")
            return

        # Step 2: Bronze layer
        try:
            save_to_csv(pdi_data, output_dir_csv, 'PDI_bronze.csv')
            save_to_csv(codebook_data, output_dir_csv, 'PDI_codebook_bronze.csv')
            save_to_sqlite(pdi_data, db_path, 'PDI_bronze')
            save_to_sqlite(codebook_data, db_path,'PDI_codebook_bronze')
            log("Bronze layer saved.")
        except Exception as e:
            log(f"[ERROR] Failed during Bronze layer: {e}")
            return

        # Step 3: Silver layer
        try:
            combined_data = pd.concat([pdi_data], ignore_index=True)
            silver_data = process_silver_layer(combined_data.copy())
            save_to_csv(silver_data, output_dir_csv, 'combined_silver.csv')
            save_to_sqlite(silver_data, db_path, 'combined_silver')
            log("Silver layer saved.")
        except Exception as e:
            log(f"[ERROR] Failed during Silver layer: {e}")
            return

        # Step 4: Gold layer
        try:
            gold_data = process_gold_layer(combined_data.copy())
            save_to_csv(gold_data, output_dir_csv, 'combined_gold.csv')
            save_to_sqlite(gold_data, db_path,'combined_gold')
            log("Gold layer saved.")
        except Exception as e:
            log(f"[ERROR] Failed during Gold layer: {e}")
            return

        # Step 5: Wide format
        try:
            wide_data = transform_to_wide_format(gold_data)
            save_to_csv(wide_data, output_dir_csv, 'combined_wide.csv')
            save_to_sqlite(wide_data, db_path, 'combined_wide')
            log("Wide format saved." )
        except Exception as e:
            log(f"[ERROR] Failed during Wide format: {e}")
            return

        # Step 6: Per track exports
        try:
            save_tracks(gold_data, output_dir_csv, db_path=db_path)
            log("Track-based exports completed.")
        except Exception as e:
            log(f"[ERROR] Failed during per-track exports: {e}")
            return

        log("ETL pipeline completed successfully.")
    

        dashboard_path = os.path.join("dashboard", "dashboard_app.py")
        subprocess.Popen(["python", "-m", "streamlit", "run", dashboard_path], shell=True)
        log(f"Streamlit dashboard started: {dashboard_path}")

        try:
            input("\n\nPress Enter to exit the ETL pipeline...")
        except KeyboardInterrupt:
            log("ETL pipeline stopped by user.")

        
    except Exception as e:
        log(f"[FATAL] Unexpected error in ETL pipeline: {e}")

if __name__ == '__main__':
    main()



