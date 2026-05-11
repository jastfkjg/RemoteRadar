import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import contextmanager

from ..models.job_listing import JobListing


class Database:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self._init_database()
        self._migrate_database()
    
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
                    categories TEXT,
                    tech_stacks TEXT,
                    seniority TEXT,
                    UNIQUE(source, job_id)
                )
            ''')
            conn.commit()
    
    def _migrate_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(job_listings)")
            columns = [row[1] for row in cursor.fetchall()]
            
            migrations = [
                ('categories', 'TEXT'),
                ('tech_stacks', 'TEXT'),
                ('seniority', 'TEXT'),
            ]
            
            for column, column_type in migrations:
                if column not in columns:
                    try:
                        cursor.execute(f'ALTER TABLE job_listings ADD COLUMN {column} {column_type}')
                        print(f"数据库迁移: 添加列 {column}")
                    except Exception as e:
                        print(f"数据库迁移警告: {e}")
            
            conn.commit()
    
    def insert_or_update(self, job: JobListing) -> int:
        if not job.categories or not job.tech_stacks:
            job.auto_classify()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            existing = self.find_by_source_and_id(job.source, job.job_id)
            
            if existing:
                cursor.execute('''
                    UPDATE job_listings 
                    SET title=?, company=?, company_url=?, company_logo=?,
                        description=?, location=?, job_type=?, salary=?,
                        tags=?, job_url=?, posted_at=?, updated_at=?,
                        categories=?, tech_stacks=?, seniority=?
                    WHERE source=? AND job_id=?
                ''', (
                    job.title, job.company, job.company_url, job.company_logo,
                    job.description, job.location, job.job_type, job.salary,
                    job.tags, job.job_url,
                    job.posted_at.isoformat() if job.posted_at else None,
                    datetime.now().isoformat(),
                    job.categories, job.tech_stacks, job.seniority,
                    job.source, job.job_id
                ))
                job_id = existing.id
            else:
                cursor.execute('''
                    INSERT INTO job_listings (
                        source, job_id, title, company, company_url, company_logo,
                        description, location, job_type, salary, tags, job_url,
                        posted_at, created_at, updated_at,
                        categories, tech_stacks, seniority
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job.source, job.job_id, job.title, job.company, job.company_url,
                    job.company_logo, job.description, job.location, job.job_type,
                    job.salary, job.tags, job.job_url,
                    job.posted_at.isoformat() if job.posted_at else None,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    job.categories, job.tech_stacks, job.seniority,
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
    
    def get_existing_job_ids(self, source: str) -> set:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT job_id FROM job_listings WHERE source=?', (source,))
            return {row[0] for row in cursor.fetchall()}
    
    def delete_older_than(self, days: int = 30) -> int:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM job_listings WHERE posted_at < ?', (cutoff,))
            conn.commit()
            return cursor.rowcount

    def get_categories(self) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT categories FROM job_listings WHERE categories IS NOT NULL AND categories != ''"
            )
            rows = cursor.fetchall()
            result = set()
            for row in rows:
                if row[0]:
                    for cat in row[0].split(','):
                        stripped = cat.strip()
                        if stripped:
                            result.add(stripped)
            return sorted(list(result))
    
    def get_tech_stacks(self) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT tech_stacks FROM job_listings WHERE tech_stacks IS NOT NULL AND tech_stacks != ''"
            )
            rows = cursor.fetchall()
            result = set()
            for row in rows:
                if row[0]:
                    for tech in row[0].split(','):
                        stripped = tech.strip()
                        if stripped:
                            result.add(stripped)
            return sorted(list(result))
    
    def get_seniority_levels(self) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT seniority FROM job_listings WHERE seniority IS NOT NULL AND seniority != ''"
            )
            rows = cursor.fetchall()
            result = set()
            for row in rows:
                if row[0]:
                    for level in row[0].split(','):
                        stripped = level.strip()
                        if stripped:
                            result.add(stripped)
            return sorted(list(result))
    
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
            categories=row['categories'] if 'categories' in row.keys() and row['categories'] else '',
            tech_stacks=row['tech_stacks'] if 'tech_stacks' in row.keys() and row['tech_stacks'] else '',
            seniority=row['seniority'] if 'seniority' in row.keys() and row['seniority'] else '',
        )
    
    def close(self):
        pass
