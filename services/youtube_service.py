import os, pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import SCOPES, CLIENT_SECRET_FILE, TOKEN_FILE

class YouTubeService:
    def __init__(self, api_key=None, client_secret_path=None, token_file=None):
        self.client_secret = client_secret_path or CLIENT_SECRET_FILE
        self.token_file = token_file or TOKEN_FILE
        self.api_key = api_key or os.environ.get('YT_API_KEY')
        self.youtube = None

    def _authenticate_oauth(self):
        if not os.path.exists(self.client_secret):
            raise FileNotFoundError(f'OAuth client_secret.json not found at {self.client_secret}')
        creds = None
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as f:
                creds = pickle.load(f)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, 'wb') as f:
                pickle.dump(creds, f)
        self.youtube = build('youtube', 'v3', credentials=creds)

    def _authenticate_apikey(self):
        if not self.api_key:
            raise RuntimeError('No API key set. Export YT_API_KEY or provide client_secret.json for OAuth.')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def ensure_auth(self, require_oauth=False):
        if self.youtube:
            return
        if require_oauth:
            self._authenticate_oauth()
            return
        if os.path.exists(self.client_secret):
            self._authenticate_oauth()
        elif self.api_key:
            self._authenticate_apikey()
        else:
            raise RuntimeError('No credentials available. Place client_secret.json in credentials/ or set YT_API_KEY env variable.')

    def fetch_videos_for_my_channel(self, maxResults=50):
        self.ensure_auth(require_oauth=True)
        req = self.youtube.search().list(part='snippet', forMine=True, maxResults=maxResults, type='video', order='date')
        res = req.execute()
        return self._parse_search_items(res.get('items', []))

    def fetch_videos_by_channel(self, channel_id, maxResults=50):
        self.ensure_auth(require_oauth=False)
        req = self.youtube.search().list(part='snippet', channelId=channel_id, maxResults=maxResults, type='video', order='date')
        res = req.execute()
        return self._parse_search_items(res.get('items', []))

    def _parse_search_items(self, items):
        videos = []
        for item in items:
            vid = item.get('id', {}).get('videoId')
            snippet = item.get('snippet', {})
            videos.append({
                'video_id': vid,
                'title': snippet.get('title'),
                'published_at': snippet.get('publishedAt'),
                'view_count': 0,
                'like_count': 0,
                'comment_count': 0
            })
        return videos
