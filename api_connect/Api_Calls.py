import requests
from api_connect.config import API_BASE_URL

def get_data_from_api(endpoint):
    # haalt data op van api
    response = requests.get(f"{API_BASE_URL}/{endpoint}")
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()