# YouTube Analytics Flask API (SQLite, Flask production-ready)

## Quickstart (local dev)
1. Create virtualenv and activate:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `credentials/` and place your credentials:
   - `credentials/client_secret.json` (OAuth client for YouTube, if using /refresh without channelId)
   - `credentials/service_account.json` (optional, for Google Sheets export)
4. Set env and run (production-ready style):
   ```bash
   cp .env.example .env
   export FLASK_APP=app.py
   export FLASK_ENV=production
   flask run --host=0.0.0.0 --port=5000
   ```
5. Endpoints:
   - `GET /refresh` (uses OAuth if credentials present; or use `/refresh?channelId=CH_ID` with API key fallback)
   - `GET /videos`
   - `GET /analytics`
   - `GET /export` (download CSV)
   - `GET /export_sheets` (if service account JSON present)
