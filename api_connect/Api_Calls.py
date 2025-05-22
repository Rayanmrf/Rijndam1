#Api_Calls.py
import requests
from api_connect.config import API_BASE_URL

def get_data_from_api(endpoint):
    # Get  data from api
    response = requests.get(f"{API_BASE_URL}/{endpoint}")
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

