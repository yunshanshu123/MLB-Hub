import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

class Config:
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')