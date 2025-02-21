import os

from dotenv import load_dotenv

load_dotenv()

FRONTEND_URL = os.getenv('FRONTEND_URL')

ORIGINS = [
    FRONTEND_URL,
]