import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'data', 'youtube_data.db')}")

# YouTube API config
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "credentials", "client_secret.json")
TOKEN_FILE = os.path.join(BASE_DIR, "credentials", "token.pickle")

# Google Sheets service account path
SHEETS_SERVICE_ACCOUNT = os.path.join(BASE_DIR, "credentials", "service_account.json")
