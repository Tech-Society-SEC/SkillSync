"""
Database Module for SkillSync
SQLite database for storing worker profiles, jobs, and analytics
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path


class SkillSyncDB:
    """Database manager for SkillSync application"""
    
    def __init__(self, db_path: str = "skillsync.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Worker Profiles Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS worker_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id TEXT UNIQUE NOT NULL,
                name TEXT,
                phone TEXT,
                language TEXT,
                job_title TEXT,
                experience_years INTEGER,
                skills TEXT,  -- JSON array
                location TEXT,
                audio_file_path TEXT,
                transcription TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Job Applications Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                job_title TEXT,
                match_score REAL,
                status TEXT DEFAULT 'pending',  -- pending, contacted, hired, rejected
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES worker_profiles(worker_id)
            )
        """)
        
        # Analytics Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id TEXT,
                event_type TEXT,  -- profile_created, job_viewed, skill_added, etc.
                event_data TEXT,  -- JSON
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Learning Progress Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                resource_title TEXT,
                resource_url TEXT,
                status TEXT DEFAULT 'recommended',  -- recommended, started, completed
                progress_percent INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES worker_profiles(worker_id)
            )
        """)
        
        self.conn.commit()
        print(f"✓ Database initialized: {self.db_path}")
    
    # ==================== WORKER PROFILES ====================
    
    def create_worker_profile(self, profile_data: Dict) -> str:
        """Create a new worker profile"""
        cursor = self.conn.cursor()
        
        worker_id = profile_data.get('worker_id') or f"WKR_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
            INSERT INTO worker_profiles 
            (worker_id, name, phone, language, job_title, experience_years, 
             skills, location, audio_file_path, transcription)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            worker_id,
            profile_data.get('name'),
            profile_data.get('phone'),
            profile_data.get('language'),
            profile_data.get('job_title'),
            profile_data.get('experience_years', 0),
            json.dumps(profile_data.get('skills', [])),
            profile_data.get('location'),
            profile_data.get('audio_file_path'),
            profile_data.get('transcription')
        ))
        
        self.conn.commit()
        
        # Log analytics
        self.log_analytics(worker_id, 'profile_created', profile_data)
        
        return worker_id
    
    def get_worker_profile(self, worker_id: str) -> Optional[Dict]:
        """Get worker profile by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM worker_profiles WHERE worker_id = ?", (worker_id,))
        row = cursor.fetchone()
        
        if row:
            profile = dict(row)
            profile['skills'] = json.loads(profile['skills']) if profile['skills'] else []
            return profile
        return None
    
    def update_worker_profile(self, worker_id: str, updates: Dict):
        """Update worker profile"""
        cursor = self.conn.cursor()
        
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [worker_id]
        
        cursor.execute(f"""
            UPDATE worker_profiles 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE worker_id = ?
        """, values)
        
        self.conn.commit()
    
    def search_workers(self, filters: Dict) -> List[Dict]:
        """Search workers by filters"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM worker_profiles WHERE 1=1"
        params = []
        
        if 'job_title' in filters:
            query += " AND job_title LIKE ?"
            params.append(f"%{filters['job_title']}%")
        
        if 'location' in filters:
            query += " AND location LIKE ?"
            params.append(f"%{filters['location']}%")
        
        if 'min_experience' in filters:
            query += " AND experience_years >= ?"
            params.append(filters['min_experience'])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        profiles = []
        for row in rows:
            profile = dict(row)
            profile['skills'] = json.loads(profile['skills']) if profile['skills'] else []
            profiles.append(profile)
        
        return profiles
    
    # ==================== JOB APPLICATIONS ====================
    
    def apply_for_job(self, worker_id: str, job_data: Dict) -> int:
        """Record job application"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO job_applications 
            (worker_id, job_id, job_title, match_score)
            VALUES (?, ?, ?, ?)
        """, (
            worker_id,
            job_data.get('job_id'),
            job_data.get('job_title'),
            job_data.get('match_score', 0)
        ))
        
        self.conn.commit()
        
        # Log analytics
        self.log_analytics(worker_id, 'job_applied', job_data)
        
        return cursor.lastrowid
    
    def get_worker_applications(self, worker_id: str) -> List[Dict]:
        """Get all applications for a worker"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM job_applications 
            WHERE worker_id = ?
            ORDER BY applied_at DESC
        """, (worker_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_application_status(self, application_id: int, status: str):
        """Update job application status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE job_applications 
            SET status = ?
            WHERE id = ?
        """, (status, application_id))
        self.conn.commit()
    
    # ==================== LEARNING PROGRESS ====================
    
    def add_learning_resource(self, worker_id: str, resource_data: Dict) -> int:
        """Add learning resource for worker"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO learning_progress 
            (worker_id, resource_id, resource_title, resource_url, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            worker_id,
            resource_data.get('resource_id'),
            resource_data.get('title'),
            resource_data.get('url'),
            'recommended'
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def update_learning_progress(self, resource_id: int, progress: int, status: str = None):
        """Update learning progress"""
        cursor = self.conn.cursor()
        
        if status:
            cursor.execute("""
                UPDATE learning_progress 
                SET progress_percent = ?, status = ?
                WHERE id = ?
            """, (progress, status, resource_id))
        else:
            cursor.execute("""
                UPDATE learning_progress 
                SET progress_percent = ?
                WHERE id = ?
            """, (progress, resource_id))
        
        self.conn.commit()
    
    def get_worker_learning(self, worker_id: str) -> List[Dict]:
        """Get learning resources for worker"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM learning_progress 
            WHERE worker_id = ?
            ORDER BY timestamp DESC
        """, (worker_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== ANALYTICS ====================
    
    def log_analytics(self, worker_id: str, event_type: str, event_data: Dict):
        """Log analytics event"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO analytics (worker_id, event_type, event_data)
            VALUES (?, ?, ?)
        """, (worker_id, event_type, json.dumps(event_data)))
        
        self.conn.commit()
    
    def get_analytics(self, worker_id: str = None, event_type: str = None, 
                     limit: int = 100) -> List[Dict]:
        """Get analytics data"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM analytics WHERE 1=1"
        params = []
        
        if worker_id:
            query += " AND worker_id = ?"
            params.append(worker_id)
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        analytics = []
        for row in cursor.fetchall():
            item = dict(row)
            item['event_data'] = json.loads(item['event_data']) if item['event_data'] else {}
            analytics.append(item)
        
        return analytics
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total workers
        cursor.execute("SELECT COUNT(*) as count FROM worker_profiles")
        stats['total_workers'] = cursor.fetchone()['count']
        
        # Total applications
        cursor.execute("SELECT COUNT(*) as count FROM job_applications")
        stats['total_applications'] = cursor.fetchone()['count']
        
        # Applications by status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM job_applications 
            GROUP BY status
        """)
        stats['applications_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Top skills
        cursor.execute("SELECT skills FROM worker_profiles")
        all_skills = []
        for row in cursor.fetchall():
            if row['skills']:
                all_skills.extend(json.loads(row['skills']))
        
        from collections import Counter
        stats['top_skills'] = dict(Counter(all_skills).most_common(10))
        
        # Recent activity
        cursor.execute("""
            SELECT event_type, COUNT(*) as count 
            FROM analytics 
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY event_type
        """)
        stats['recent_activity'] = {row['event_type']: row['count'] for row in cursor.fetchall()}
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# ==================== TESTING ====================

if __name__ == "__main__":
    print("="*70)
    print("Testing SkillSync Database")
    print("="*70)
    
    # Initialize database
    db = SkillSyncDB("test_skillsync.db")
    
    # Create test worker profile
    profile_data = {
        'name': 'Ravi Kumar',
        'phone': '+91-9876543210',
        'language': 'hindi',
        'job_title': 'Electrician',
        'experience_years': 5,
        'skills': ['Electrical Wiring', 'Fan Installation', 'Motor Winding'],
        'location': 'Mumbai',
        'transcription': 'I am electrician with 5 years experience'
    }
    
    worker_id = db.create_worker_profile(profile_data)
    print(f"\n✓ Created worker profile: {worker_id}")
    
    # Get profile
    profile = db.get_worker_profile(worker_id)
    print(f"✓ Retrieved profile: {profile['name']}")
    print(f"  Skills: {profile['skills']}")
    
    # Apply for job
    job_data = {
        'job_id': 'JOB001',
        'job_title': 'Maintenance Electrician',
        'match_score': 85.5
    }
    app_id = db.apply_for_job(worker_id, job_data)
    print(f"\n✓ Applied for job: {app_id}")
    
    # Get dashboard stats
    stats = db.get_dashboard_stats()
    print(f"\n✓ Dashboard Stats:")
    print(f"  Total Workers: {stats['total_workers']}")
    print(f"  Total Applications: {stats['total_applications']}")
    print(f"  Top Skills: {list(stats['top_skills'].keys())[:3]}")
    
    db.close()
    print("\n✓ Database test complete!")
