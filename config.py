import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    PIXABAY_API_KEY: str = os.getenv("PIXABAY_API_KEY")
    API_URL: str = os.getenv("API_URL")

    if not BOT_TOKEN or not PIXABAY_API_KEY or not API_URL:
        raise ValueError("Please set BOT_TOKEN, PIXABAY_API_KEY, and API_URL in your .env file")
