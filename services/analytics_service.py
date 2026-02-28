import pandas as pd

class AnalyticsService:
    @staticmethod
    def _rows_to_df(rows):
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
        df = pd.DataFrame(data)
        return df

    @staticmethod
    def calculate_trending(rows):
        df = AnalyticsService._rows_to_df(rows)
        if df.empty:
            return df
        df['engagement'] = df['like_count'].fillna(0) + df['comment_count'].fillna(0)
        return df.sort_values(by='engagement', ascending=False)
