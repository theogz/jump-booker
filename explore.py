import dotenv
import os
import requests

# Environment variables
dotenv_path: str = os.path.join(os.path.dirname(__file__), './.env')
dotenv.load_dotenv(dotenv_path)
