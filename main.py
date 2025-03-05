from api_connect.Api_Calls import get_data_from_api
from api_connect.config import API_BASE_URL

def main():
    raw_data = get_data_from_api('posts')
    print(raw_data)

if __name__ == "__main__":
    main()
