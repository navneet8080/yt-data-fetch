from flask import Flask, jsonify, request, send_file, render_template
from services.youtube_service import YouTubeService
from services.database_service import DatabaseService
from services.analytics_service import AnalyticsService
from services.export_service import ExportService
from config import DB_URL
import os

def create_app():
    app = Flask(__name__)
    
    # Initialize services
    yt = YouTubeService(api_key=None)
    db = DatabaseService()  # Single instance reused across routes

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/refresh', methods=['GET'])
    def refresh():
        """Fetch videos from a channel or from 'my channel' via OAuth"""
        channel_id = request.args.get('channelId')
        try:
            if channel_id:
                videos = yt.fetch_videos_by_channel(channel_id)
            else:
                videos = yt.fetch_videos_for_my_channel()
            db.insert_videos(videos)
            return jsonify({'status': 'success', 'fetched': len(videos)})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    @app.route('/videos', methods=['GET'])
    def videos():
        """Return all videos from the database"""
        try:
            rows = db.get_all_videos()
            out = [{
                'video_id': r.video_id,
                'title': r.title,
                'published_at': r.published_at.isoformat() if r.published_at else None,
                'view_count': r.view_count,
                'like_count': r.like_count,
                'comment_count': r.comment_count
            } for r in rows]
            return jsonify(out)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/analytics', methods=['GET'])
    def analytics():
        """Return analytics/trending data"""
        try:
            rows = db.get_all_videos()
            df = AnalyticsService.calculate_trending(rows)
            return df.to_json(orient='records')
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/export', methods=['GET'])
    def export():
        """Export video data as CSV"""
        try:
            rows = db.get_all_videos()
            path = ExportService.export_to_csv(rows, filename='youtube_export.csv')
            return send_file(path, as_attachment=True)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/export_sheets', methods=['GET'])
    def export_sheets():
        """Export video data to Google Sheets using service account"""
        try:
            rows = db.get_all_videos()
            result = ExportService.export_to_sheets(
                rows,
                spreadsheet_id='1ODxXvbMMggcRKEH2jWBGWHDadgJC-WW2HfPyZhHoTTQ',
                worksheet_name='Sheet1',
                service_account_json_path=os.path.join('credentials', 'service_account.json')
            )
            return jsonify({"status": "success", "message": result})
        except FileNotFoundError as e:
            return jsonify({"status": "error", "message": str(e)}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
