import requests
import os
from dotenv import load_dotenv

# Environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
load_dotenv(dotenv_path)

base_url = 'https://app.socialbicycles.com/api'
headers = {
    'Authorization': f'Bearer {os.getenv("SOCIAL_BICYCLES_ACCESS_TOKEN")}'
}


r = requests.get(f'{base_url}/bikes.json', headers=headers)
print(r.json())
