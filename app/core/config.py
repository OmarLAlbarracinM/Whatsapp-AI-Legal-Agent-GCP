import os
from dotenv import load_dotenv

load_dotenv() 

class Settings:
    PROJECT_ID = os.getenv("PROJECT_ID")
    LOCATION = os.getenv("LOCATION", "us-central1")
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    DATA_STORE_ID = os.getenv("DATA_STORE_ID")

settings = Settings()