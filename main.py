from api.Api_Calls import get_data_from_api
import config

def main():
    raw_data = get_data_from_api('posts')
    print(raw_data)

if __name__ == "__main__":
    main()
