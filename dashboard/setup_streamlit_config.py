#setup_streamlit_config.py
import os

def configure_streamlit():
    config_dir = os.path.join(os.path.expanduser("~"), ".streamlit")
    os.makedirs(config_dir, exist_ok=True)
    config_path =os.path.join(config_dir, "config.toml")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write("[browser]\ngatherUsageStats = false\n")
    print(f"Streamlit AVG-config created: {config_path}")
