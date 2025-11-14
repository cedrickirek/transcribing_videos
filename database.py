import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class VideoDatabase:
    def __init__(self, db_path: str = "learning_repo.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create videos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_url TEXT UNIQUE NOT NULL,
                video_id TEXT NOT NULL,
                title TEXT,
                channel TEXT,
                transcript TEXT,
                summary TEXT,
                keywords TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_video(self, video_url: str, video_id: str, title: str, 
                  channel: str, transcript: str, summary: str, keywords: str) -> bool:
        """Add a new video to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO videos (video_url, video_id, title, channel, transcript, summary, keywords)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (video_url, video_id, title, channel, transcript, summary, keywords))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Video already exists
            return False
    
    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """Search videos by keyword in title, summary, or keywords"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        search_term = f"%{keyword}%"
        cursor.execute('''
            SELECT id, video_url, title, channel, summary, keywords, date_added
            FROM videos
            WHERE title LIKE ? OR summary LIKE ? OR keywords LIKE ?
            ORDER BY date_added DESC
        ''', (search_term, search_term, search_term))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'video_url': row[1],
                'title': row[2],
                'channel': row[3],
                'summary': row[4],
                'keywords': row[5],
                'date_added': row[6]
            })
        
        conn.close()
        return results
    
    def get_all_videos(self, limit: int = 50) -> List[Dict]:
        """Get all videos, most recent first"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, video_url, title, channel, summary, keywords, date_added
            FROM videos
            ORDER BY date_added DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'video_url': row[1],
                'title': row[2],
                'channel': row[3],
                'summary': row[4],
                'keywords': row[5],
                'date_added': row[6]
            })
        
        conn.close()
        return results
    
    def get_video_by_url(self, video_url: str) -> Optional[Dict]:
        """Get a specific video by URL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, video_url, title, channel, transcript, summary, keywords, date_added
            FROM videos
            WHERE video_url = ?
        ''', (video_url,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'video_url': row[1],
                'title': row[2],
                'channel': row[3],
                'transcript': row[4],
                'summary': row[5],
                'keywords': row[6],
                'date_added': row[7]
            }
        return None
