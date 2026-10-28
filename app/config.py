import os
from dotenv import load_dotenv

load_dotenv()

PORTAL_BASE_URL = os.getenv("PORTAL_BASE_URL")
PORTAL_EMAIL = os.getenv("PORTAL_EMAIL")
PORTAL_PASSWORD = os.getenv("PORTAL_PASSWORD")