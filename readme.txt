# 📘 README – Rijndam1 Project

## 🎯 Project Goal  
The goal of this project is to build a full ETL pipeline (Extract, Transform, Load) for processing questionnaire data from Rijndam Revalidatie. The pipeline processes raw Excel files (from dummy sources or a live test server via API), structures them using the Medallion architecture (Bronze → Silver → Gold), and prepares the data for analysis in a dynamic Streamlit dashboard.

-----


## 🏗️ Project Structure

Rijndam1/
├── api_connect/ # API authentication and data connection
│ ├── Api_Calls.py # Handles API requests
│ └── config.py # Contains API credentials and URLs
│
├── dashboard/ # Streamlit visualization
│ ├── dashboard_app.py # Main interactive dashboard
│ ├── setup_streamlit_config.py # Streamlit config writer
│ └── init.py
│
├── data/ # All ETL transformations
│ ├── data_transformer.py # Core ETL logic
│ └── init.py
│
├── input_data/ # Input Excel files (.xlsx)
├── logs/ # ETL logging folder (auto-generated)
├── output_csv/ # Processed CSV files per layer (auto-generated)
├── output_database/ # SQLite database files (auto-generated)
├── main.py # Orchestrates the full pipeline
└── readme.txt # This file

-----


## 🔄 ETL Pipeline – Overview

### 1️⃣ Bronze Layer  
- **What**: Raw Excel data ingestion (questionnaires + codebooks)  
- **Where**: `output_csv/PDI_bronze.csv`, `PDI_codebook_bronze.csv`  
- **Why**: Preserves raw untouched data for traceability  

---

### 2️⃣ Silver Layer  
- **What**: Cleaned & harmonized version of bronze data  
- **Includes**:
  - Dropping technical/noise columns  
  - Calculating `age` from birthdate fields  
  - Hashing `respondentid` for privacy  
  - Renaming critical columns for clarity  
- **Output**: `combined_silver.csv` and `combined_silver` SQLite table

---

### 3️⃣ Gold Layer  
- **What**: Fully enriched, analysis-ready data  
- **Enrichment Includes**:
  - Calculated `PDIscore` from 7 question fields  
  - Score classification: Low, Moderate, Severe limitation  
  - Only the most recent response per track & respondent kept  
- **Output**: `combined_gold.csv`, per-track CSVs, and database tables  

---

### 4️⃣ Wide Format  
- **What**: Pivoted table where each respondent has one row  
- **Why**: Enables per-person journey analysis across multiple tracks  
- **Output**: `combined_wide.csv` and SQLite table

---

### 5️⃣ Per-Traject Export  
- **What**: Automatically splits the Gold Layer into separate files/tables per rehabilitation track  
- **Why**: Enables individual departments (e.g. Pain, Balance, Cognition) to analyze only their relevant data  
- **Enrichment Includes**:  
  - Each track is saved as its own CSV and SQLite table  
  - Preserves full respondent history per track  
- **Output**:  
  - CSVs like `Pain_Rehab.csv`, `Balance_Rehab.csv` inside `output_csv/`  
  - Corresponding tables in `output_database/output_db.db` (e.g. `Pain_Rehab`)  

> These targeted outputs support focused analysis, clinical review, and modular dashboarding.

--

## 📊 Streamlit Dashboard  

The interactive dashboard (📍 `dashboard/dashboard_app.py`) provides insights like:

- ✅ Average PDI scores per track  
- 📈 Monthly score trends  
- 👥 Unique respondent counts  
- 🧠 Score severity breakdowns  
- 📈 Score averages by age group  
- 📉 Age vs PDIscore scatter plots  
- 🧾 Per-person history via wide format

The dashboard is **automatically launched** after the ETL pipeline completes.

-----


## ▶️ How to Use

1. Place `.xlsx` input files into the `input_data/` folder  
2. Run the ETL pipeline via:  
   ```bash
   python main.py
The dashboard opens automatically in your browser

Processed data will be saved to:
    -output_csv/ (as CSV)
    -output_database/output_db.db (SQLite)

--

🔍 Example – Gold Layer Output
respondentid	age	Gender	track_name	PDIscore	score_level
a12f3c8e9b	47	Female	Balance Rehab	42	Moderate limitation

----


🏗️ Why the Medallion Architecture?
Layer	Description	Purpose
Bronze	Raw, untouched data	For full audit/traceability
Silver	Cleaned & formatted	For standard analysis
Gold	Enriched, deduplicated	Dashboard & AI-ready insights

----


🛠️ First-Time Setup Notes
    When cloning the repository or running for the first time:
The following folders are created automatically if they do not exist yet:

-logs/ → for ETL logging
-output_csv/ → to store all exported CSV files
-output_database/ → to store the SQLite database

No manual setup is needed. This ensures compatibility with clean GitHub clones.

----


🚀 Future Extensions

📡 Live API data streaming
📊 Multi-questionnaire support
🧠 AI model training from gold layer
📤 Integration with Power BI, Snowflake, etc.

Developed for: Rijndam Revalidatie – AI & DataLab Hogeschool Rotterdam Internship

