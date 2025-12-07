import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://trafficpanda.net")
DB_PATH = os.getenv("DB_PATH", "trafficpanda.db")

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8100"))

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecret")

STARS_PROVIDER_TOKEN = os.getenv("STARS_PROVIDER_TOKEN", "")
