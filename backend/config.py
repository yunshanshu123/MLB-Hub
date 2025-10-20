import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class Config:
    """应用程序的配置类"""
    # 从环境变量中获取 API 密钥
    API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')
    # API-Football 的基础 URL 和主机名
    API_FOOTBALL_HOST = 'v1.baseball.api-sports.io'
    API_FOOTBALL_BASE_URL = f'https://{API_FOOTBALL_HOST}'