import os
from dotenv import load_dotenv

# class to handle id and key
class Credentials():
    def __init__(self):
        load_dotenv()
        self.spac_api_id = os.getenv("SPAC_API_ID")
        self.spac_api_key = os.getenv("SPAC_API_KEY")

    # # get key to api from local .env file
    # def get_SPAC_API_tokens(self):
    #     # bearer format: 
    #     # Authorization: Bearer {id}:{key}
    #     #return f"{spac_id}:{spac_key}"

    #     return self.spac_api_id, self.spac_api_key
