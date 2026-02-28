import os
try:
    import pandas as pd
    HAS_PANDAS = True
except Exception:
    HAS_PANDAS = False
import csv

class ExportService:
    @staticmethod
    def _rows_to_list_of_dicts(rows):
        data = []
        for r in rows:
            data.append({
                'video_id': getattr(r, 'video_id', None),
                'title': getattr(r, 'title', None),
                'published_at': getattr(r, 'published_at', None),
                'view_count': getattr(r, 'view_count', 0),
                'like_count': getattr(r, 'like_count', 0),
                'comment_count': getattr(r, 'comment_count', 0)
            })
        return data

    @staticmethod
    def export_to_csv(rows, filename='youtube_export.csv'):
        data = ExportService._rows_to_list_of_dicts(rows)
        os.makedirs('data', exist_ok=True)
        path = os.path.join('data', filename)
        if HAS_PANDAS:
            import pandas as pd
            pd.DataFrame(data).to_csv(path, index=False)
        else:
            keys = ['video_id','title','published_at','view_count','like_count','comment_count']
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for row in data:
                    writer.writerow({k: row.get(k, '') for k in keys})
        return os.path.abspath(path)

    @staticmethod
    def export_to_sheets(rows,
                         spreadsheet_id='1ODxXvbMMggcRKEH2jWBGWHDadgJC-WW2HfPyZhHoTTQ',
                         worksheet_name='Sheet1',
                         service_account_json_path=None):
        """
        Export rows to an existing spreadsheet (by spreadsheet_id).
        This version uses open_by_key() to avoid creating new spreadsheets,
        which can trigger Drive quota errors.
        """
        import os
        import gspread
        from google.oauth2.service_account import Credentials

        # default service account path
        if service_account_json_path is None:
            service_account_json_path = os.path.join('credentials', 'service_account.json')

        if not os.path.exists(service_account_json_path):
            raise FileNotFoundError(f"Service account JSON not found at {service_account_json_path}")

        scopes = ['https://www.googleapis.com/auth/spreadsheets',
                  'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(service_account_json_path, scopes=scopes)
        client = gspread.authorize(creds)

        # format rows to list of dicts
        data = ExportService._rows_to_list_of_dicts(rows)

        # open existing spreadsheet by ID
        sh = client.open_by_key(spreadsheet_id)

        # ensure worksheet exists
        try:
            worksheet = sh.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sh.add_worksheet(title=worksheet_name, rows="100", cols="20")

        # if no data just clear and exit
        if not data:
            worksheet.clear()
            return 'no_data'

        # build header + rows
        headers = list(data[0].keys())
        values = [headers] + [[str(row.get(h, '')) for h in headers] for row in data]

        # clear old data and update
        worksheet.clear()
        worksheet.update(values)
        return 'updated_sheet'
