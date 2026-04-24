import sqlite3
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager

from ..models.job_listing import JobListing


class Database:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    job_id TEXT NOT NULL,
                    title TEXT,
                    company TEXT,
                    company_url TEXT,
                    company_logo TEXT,
                    description TEXT,
                    location TEXT,
                    job_type TEXT,
                    salary TEXT,
                    tags TEXT,
                    job_url TEXT,
                    posted_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source, job_id)
                )
            ''')
            conn.commit()
    
    def insert_or_update(self, job: JobListing) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            existing = self.find_by_source_and_id(job.source, job.job_id)
            
            if existing:
                cursor.execute('''
                    UPDATE job_listings 
                    SET title=?, company=?, company_url=?, company_logo=?,
                        description=?, location=?, job_type=?, salary=?,
                        tags=?, job_url=?, posted_at=?, updated_at=?
                    WHERE source=? AND job_id=?
                ''', (
                    job.title, job.company, job.company_url, job.company_logo,
                    job.description, job.location, job.job_type, job.salary,
                    job.tags, job.job_url,
                    job.posted_at.isoformat() if job.posted_at else None,
                    datetime.now().isoformat(),
                    job.source, job.job_id
                ))
                job_id = existing.id
            else:
                cursor.execute('''
                    INSERT INTO job_listings (
                        source, job_id, title, company, company_url, company_logo,
                        description, location, job_type, salary, tags, job_url,
                        posted_at, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.source, job.job_id, job.title, job.company, job.company_url,
                    job.company_logo, job.description, job.location, job.job_type,
                    job.salary, job.tags, job.job_url,
                    job.posted_at.isoformat() if job.posted_at else None,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                job_id = cursor.lastrowid
            
            conn.commit()
            return job_id
    
    def insert_many(self, jobs: List[JobListing]) -> int:
        count = 0
        for job in jobs:
            self.insert_or_update(job)
            count += 1
        return count
    
    def find_by_source_and_id(self, source: str, job_id: str) -> Optional[JobListing]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM job_listings WHERE source=? AND job_id=?', (source, job_id))
            row = cursor.fetchone()
            return self._row_to_job(row) if row else None
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[JobListing]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM job_listings 
                ORDER BY posted_at DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            rows = cursor.fetchall()
            return [self._row_to_job(row) for row in rows]
    
    def find_by_source(self, source: str, limit: int = 100) -> List[JobListing]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM job_listings 
                WHERE source=? 
                ORDER BY posted_at DESC 
                LIMIT ?
            ''', (source, limit))
            rows = cursor.fetchall()
            return [self._row_to_job(row) for row in rows]
    
    def count_all(self) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM job_listings')
            return cursor.fetchone()[0]
    
    def count_by_source(self, source: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM job_listings WHERE source=?', (source,))
            return cursor.fetchone()[0]
    
    def get_sources(self) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT source FROM job_listings')
            return [row[0] for row in cursor.fetchall()]
    
    def _row_to_job(self, row) -> JobListing:
        return JobListing(
            id=row['id'],
            source=row['source'],
            job_id=row['job_id'],
            title=row['title'],
            company=row['company'],
            company_url=row['company_url'],
            company_logo=row['company_logo'],
            description=row['description'],
            location=row['location'],
            job_type=row['job_type'],
            salary=row['salary'],
            tags=row['tags'],
            job_url=row['job_url'],
            posted_at=datetime.fromisoformat(row['posted_at']) if row['posted_at'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
        )
    
    def close(self):
        pass
