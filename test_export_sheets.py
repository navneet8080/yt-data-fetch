# test_export_sheets.py
import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from services.database_service import DatabaseService
from services.export_service import ExportService

# ensure service_account.json is in credentials/
service_account_path = os.path.join('credentials', 'service_account.json')
if not os.path.exists(service_account_path):
    print("service_account.json not found at", service_account_path)
    sys.exit(1)

# choose the spreadsheet id (your sheet)
SPREADSHEET_ID = "1ODxXvbMMggcRKEH2jWBGWHDadgJC-WW2HfPyZhHoTTQ"

db = DatabaseService()
rows = db.get_all_videos()  # if DB empty, script still tries to open sheet

res = ExportService.export_to_sheets(rows,
                                    spreadsheet_id=SPREADSHEET_ID,
                                    worksheet_name='Sheet1',
                                    service_account_json_path=service_account_path)
print("Result:", res)
