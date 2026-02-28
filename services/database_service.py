from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DB_URL
from datetime import datetime

Base = declarative_base()

class Video(Base):
    __tablename__ = 'videos'
    video_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    published_at = Column(DateTime)
    view_count = Column(Integer)
    like_count = Column(Integer)
    comment_count = Column(Integer)

class DatabaseService:
    def __init__(self):
        self.engine = create_engine(DB_URL, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_videos(self, videos):
        session = self.Session()
        for v in videos:
            if not v.get('video_id'):
                continue
            existing = session.get(Video, v['video_id'])
            if existing:
                existing.title = v.get('title') or existing.title
                existing.view_count = v.get('view_count', existing.view_count)
                existing.like_count = v.get('like_count', existing.like_count)
                existing.comment_count = v.get('comment_count', existing.comment_count)
            else:
                published = None
                if v.get('published_at'):
                    try:
                        published = datetime.fromisoformat(v['published_at'].replace('Z', '+00:00'))
                    except Exception:
                        published = None
                session.add(Video(
                    video_id=v['video_id'],
                    title=v.get('title'),
                    published_at=published,
                    view_count=v.get('view_count', 0),
                    like_count=v.get('like_count', 0),
                    comment_count=v.get('comment_count', 0)
                ))
        session.commit()
        session.close()

    def get_all_videos(self):
        session = self.Session()
        rows = session.query(Video).all()
        session.close()
        return rows
