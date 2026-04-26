import sqlite3
import aiosqlite
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Set
from contextlib import asynccontextmanager

from api.schemas import JobSchema


class APIDatabaseService:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self._init_database_sync()
    
    def _init_database_sync(self):
        conn = sqlite3.connect(self.db_path)
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                categories TEXT,
                tech_stacks TEXT,
                seniority TEXT,
                locations TEXT,
                min_salary INTEGER,
                max_salary INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                job_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                duration_seconds INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_actions_user ON user_actions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_actions_job ON user_actions(job_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_actions_created ON user_actions(created_at)')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                job_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, job_id)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_saved_jobs_user ON saved_jobs(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_saved_jobs_job ON saved_jobs(job_id)')
        
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
        conn.close()
    
    @asynccontextmanager
    async def get_connection(self):
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            await conn.close()
    
    def _row_to_schema(self, row) -> JobSchema:
        return JobSchema(
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
    
    async def count_jobs(
        self,
        source: Optional[str] = None,
        job_type: Optional[str] = None,
        location: Optional[str] = None,
        days_ago: Optional[int] = None,
        search: Optional[str] = None,
        category: Optional[str] = None,
        tech_stack: Optional[str] = None,
        seniority: Optional[str] = None,
    ) -> int:
        conditions = []
        params = []
        
        if source:
            conditions.append("source = ?")
            params.append(source)
        
        if job_type:
            conditions.append("job_type LIKE ?")
            params.append(f"%{job_type}%")
        
        if location:
            conditions.append("location LIKE ?")
            params.append(f"%{location}%")
        
        if days_ago:
            since_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            conditions.append("posted_at >= ?")
            params.append(since_date)
        
        if search:
            search_conditions = [
                "title LIKE ?",
                "company LIKE ?",
                "description LIKE ?",
                "tags LIKE ?"
            ]
            search_param = f"%{search}%"
            conditions.append(f"({ ' OR '.join(search_conditions) })")
            params.extend([search_param] * 4)
        
        if category:
            conditions.append("categories LIKE ?")
            params.append(f"%{category}%")
        
        if tech_stack:
            conditions.append("tech_stacks LIKE ?")
            params.append(f"%{tech_stack}%")
        
        if seniority:
            conditions.append("seniority LIKE ?")
            params.append(f"%{seniority}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                f"SELECT COUNT(*) FROM job_listings WHERE {where_clause}",
                params
            )
            result = await cursor.fetchone()
            return result[0]
    
    async def get_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        source: Optional[str] = None,
        job_type: Optional[str] = None,
        location: Optional[str] = None,
        days_ago: Optional[int] = None,
        search: Optional[str] = None,
        category: Optional[str] = None,
        tech_stack: Optional[str] = None,
        seniority: Optional[str] = None,
        sort_by: str = "posted_at",
        sort_order: str = "desc",
    ) -> tuple[List[JobSchema], int, int]:
        conditions = []
        params = []
        
        if source:
            conditions.append("source = ?")
            params.append(source)
        
        if job_type:
            conditions.append("job_type LIKE ?")
            params.append(f"%{job_type}%")
        
        if location:
            conditions.append("location LIKE ?")
            params.append(f"%{location}%")
        
        if days_ago:
            since_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            conditions.append("posted_at >= ?")
            params.append(since_date)
        
        if search:
            search_conditions = [
                "title LIKE ?",
                "company LIKE ?",
                "description LIKE ?",
                "tags LIKE ?"
            ]
            search_param = f"%{search}%"
            conditions.append(f"({ ' OR '.join(search_conditions) })")
            params.extend([search_param] * 4)
        
        if category:
            conditions.append("categories LIKE ?")
            params.append(f"%{category}%")
        
        if tech_stack:
            conditions.append("tech_stacks LIKE ?")
            params.append(f"%{tech_stack}%")
        
        if seniority:
            conditions.append("seniority LIKE ?")
            params.append(f"%{seniority}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        valid_sort_columns = ['posted_at', 'created_at', 'updated_at', 'title', 'company']
        sort_by = sort_by if sort_by in valid_sort_columns else 'posted_at'
        sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
        
        offset = (page - 1) * page_size
        
        count_query = f"SELECT COUNT(*) FROM job_listings WHERE {where_clause}"
        data_query = f"""
            SELECT * FROM job_listings 
            WHERE {where_clause} 
            ORDER BY {sort_by} {sort_order} 
            LIMIT ? OFFSET ?
        """
        
        params_for_count = params.copy()
        params_for_data = params.copy()
        params_for_data.extend([page_size, offset])
        
        async with self.get_connection() as conn:
            cursor = await conn.execute(count_query, params_for_count)
            result = await cursor.fetchone()
            total = result[0]
            
            cursor = await conn.execute(data_query, params_for_data)
            rows = await cursor.fetchall()
            
            jobs = [self._row_to_schema(row) for row in rows]
            
            total_pages = (total + page_size - 1) // page_size
            
            return jobs, total, total_pages
    
    async def get_job_by_id(self, job_db_id: int) -> Optional[JobSchema]:
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM job_listings WHERE id = ?",
                (job_db_id,)
            )
            row = await cursor.fetchone()
            return self._row_to_schema(row) if row else None
    
    async def get_sources(self) -> List[str]:
        async with self.get_connection() as conn:
            cursor = await conn.execute("SELECT DISTINCT source FROM job_listings")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def get_job_types(self) -> List[str]:
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT DISTINCT job_type FROM job_listings WHERE job_type IS NOT NULL AND job_type != ''"
            )
            rows = await cursor.fetchall()
            result = []
            for row in rows:
                types = row[0].split(',') if row[0] else []
                for t in types:
                    stripped = t.strip()
                    if stripped and stripped not in result:
                        result.append(stripped)
            return result
    
    async def get_categories(self) -> List[str]:
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT DISTINCT categories FROM job_listings WHERE categories IS NOT NULL AND categories != ''"
            )
            rows = await cursor.fetchall()
            result: Set[str] = set()
            for row in rows:
                if row[0]:
                    for cat in row[0].split(','):
                        stripped = cat.strip()
                        if stripped:
                            result.add(stripped)
            return sorted(list(result))
    
    async def get_tech_stacks(self) -> List[str]:
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT DISTINCT tech_stacks FROM job_listings WHERE tech_stacks IS NOT NULL AND tech_stacks != ''"
            )
            rows = await cursor.fetchall()
            result: Set[str] = set()
            for row in rows:
                if row[0]:
                    for tech in row[0].split(','):
                        stripped = tech.strip()
                        if stripped:
                            result.add(stripped)
            return sorted(list(result))
    
    async def get_seniority_levels(self) -> List[str]:
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT DISTINCT seniority FROM job_listings WHERE seniority IS NOT NULL AND seniority != ''"
            )
            rows = await cursor.fetchall()
            result: Set[str] = set()
            for row in rows:
                if row[0]:
                    for level in row[0].split(','):
                        stripped = level.strip()
                        if stripped:
                            result.add(stripped)
            return sorted(list(result))
    
    async def get_locations(self) -> List[str]:
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT DISTINCT location FROM job_listings WHERE location IS NOT NULL AND location != '' LIMIT 100"
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def get_stats(self) -> Dict[str, Any]:
        async with self.get_connection() as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM job_listings")
            row = await cursor.fetchone()
            total = row[0]
            
            cursor = await conn.execute("SELECT source, COUNT(*) FROM job_listings GROUP BY source")
            rows = await cursor.fetchall()
            by_source = {row[0]: row[1] for row in rows}
            
            cursor = await conn.execute(
                "SELECT MAX(updated_at) FROM job_listings"
            )
            row = await cursor.fetchone()
            latest_update = datetime.fromisoformat(row[0]) if row[0] else None
            
            sources = await self.get_sources()
            job_types = await self.get_job_types()
            categories = await self.get_categories()
            tech_stacks = await self.get_tech_stacks()
            seniority_levels = await self.get_seniority_levels()
            
            return {
                "total_jobs": total,
                "by_source": by_source,
                "sources": sources,
                "job_types": job_types,
                "categories": categories,
                "tech_stacks": tech_stacks,
                "seniority_levels": seniority_levels,
                "latest_update": latest_update,
            }
    
    async def get_latest_update_time(self) -> Optional[datetime]:
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT MAX(updated_at) FROM job_listings"
            )
            row = await cursor.fetchone()
            return datetime.fromisoformat(row[0]) if row[0] else None
    
    async def get_existing_job_ids(self, source: str) -> Set[str]:
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT job_id FROM job_listings WHERE source = ?",
                (source,)
            )
            rows = await cursor.fetchall()
            return {row[0] for row in rows}
    
    async def insert_or_update_job(self, job_data: dict) -> tuple[int, bool]:
        from src.classifier import job_classifier
        
        source = job_data.get('source', '')
        job_id = job_data.get('job_id', '')
        title = job_data.get('title', '')
        description = job_data.get('description', '')
        location = job_data.get('location', '')
        
        categories = job_data.get('categories', '')
        tech_stacks = job_data.get('tech_stacks', '')
        seniority = job_data.get('seniority', '')
        
        if not categories or not tech_stacks:
            classified = job_classifier.classify(
                title=title,
                description=description,
                location=location
            )
            if not categories:
                categories = ', '.join(classified.get('categories', []))
            if not tech_stacks:
                tech_stacks = ', '.join(classified.get('tech_stacks', []))
            if not seniority:
                seniority = ', '.join(classified.get('seniority', []))
        
        now = datetime.now().isoformat()
        
        async with self.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT id FROM job_listings WHERE source = ? AND job_id = ?",
                (source, job_id)
            )
            existing = await cursor.fetchone()
            
            if existing:
                await conn.execute('''
                    UPDATE job_listings 
                    SET title=?, company=?, company_url=?, company_logo=?,
                        description=?, location=?, job_type=?, salary=?,
                        tags=?, job_url=?, posted_at=?, updated_at=?,
                        categories=?, tech_stacks=?, seniority=?
                    WHERE source=? AND job_id=?
                ''', (
                    job_data.get('title', ''),
                    job_data.get('company', ''),
                    job_data.get('company_url', ''),
                    job_data.get('company_logo', ''),
                    job_data.get('description', ''),
                    job_data.get('location', ''),
                    job_data.get('job_type', ''),
                    job_data.get('salary', ''),
                    job_data.get('tags', ''),
                    job_data.get('job_url', ''),
                    job_data.get('posted_at'),
                    now,
                    categories,
                    tech_stacks,
                    seniority,
                    source,
                    job_id
                ))
                await conn.commit()
                return existing[0], False
            else:
                cursor = await conn.execute('''
                    INSERT INTO job_listings (
                        source, job_id, title, company, company_url, company_logo,
                        description, location, job_type, salary, tags, job_url,
                        posted_at, created_at, updated_at,
                        categories, tech_stacks, seniority
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    source, job_id,
                    job_data.get('title', ''),
                    job_data.get('company', ''),
                    job_data.get('company_url', ''),
                    job_data.get('company_logo', ''),
                    job_data.get('description', ''),
                    job_data.get('location', ''),
                    job_data.get('job_type', ''),
                    job_data.get('salary', ''),
                    job_data.get('tags', ''),
                    job_data.get('job_url', ''),
                    job_data.get('posted_at'),
                    now, now,
                    categories,
                    tech_stacks,
                    seniority,
                ))
                await conn.commit()
                return cursor.lastrowid, True
    
    async def batch_insert_jobs(self, jobs: list[dict]) -> dict:
        new_count = 0
        updated_count = 0
        job_ids = []
        
        for job_data in jobs:
            job_id, is_new = await self.insert_or_update_job(job_data)
            job_ids.append(job_id)
            if is_new:
                new_count += 1
            else:
                updated_count += 1
        
        return {
            'total': len(jobs),
            'new': new_count,
            'updated': updated_count,
            'job_ids': job_ids,
        }
    
    async def create_user(self, email: str, username: str, password_hash: str) -> dict:
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        
        async with self.get_connection() as conn:
            try:
                cursor = await conn.execute('''
                    INSERT INTO users (user_id, email, username, password_hash, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                ''', (user_id, email, username, password_hash, now))
                await conn.commit()
                return {
                    'success': True,
                    'user_id': user_id,
                    'id': cursor.lastrowid
                }
            except sqlite3.IntegrityError as e:
                if 'UNIQUE constraint failed: users.email' in str(e):
                    return {
                        'success': False,
                        'error': '邮箱已被注册'
                    }
                return {
                    'success': False,
                    'error': str(e)
                }
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        async with self.get_connection() as conn:
            cursor = await conn.execute('''
                SELECT id, user_id, email, username, password_hash, created_at, last_login, is_active
                FROM users WHERE email = ?
            ''', (email,))
            row = await cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'email': row['email'],
                    'username': row['username'],
                    'password_hash': row['password_hash'],
                    'created_at': row['created_at'],
                    'last_login': row['last_login'],
                    'is_active': row['is_active']
                }
            return None
    
    async def get_user_by_user_id(self, user_id: str) -> Optional[dict]:
        async with self.get_connection() as conn:
            cursor = await conn.execute('''
                SELECT id, user_id, email, username, password_hash, created_at, last_login, is_active
                FROM users WHERE user_id = ?
            ''', (user_id,))
            row = await cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'email': row['email'],
                    'username': row['username'],
                    'password_hash': row['password_hash'],
                    'created_at': row['created_at'],
                    'last_login': row['last_login'],
                    'is_active': row['is_active']
                }
            return None
    
    async def update_last_login(self, user_id: str) -> bool:
        now = datetime.now().isoformat()
        async with self.get_connection() as conn:
            await conn.execute('''
                UPDATE users SET last_login = ? WHERE user_id = ?
            ''', (now, user_id))
            await conn.commit()
            return True
    
    async def save_job(self, user_id: str, job_id: int) -> dict:
        now = datetime.now().isoformat()
        async with self.get_connection() as conn:
            try:
                cursor = await conn.execute('''
                    INSERT INTO saved_jobs (user_id, job_id, created_at)
                    VALUES (?, ?, ?)
                ''', (user_id, job_id, now))
                await conn.commit()
                return {
                    'success': True,
                    'saved': True,
                    'id': cursor.lastrowid
                }
            except sqlite3.IntegrityError:
                return {
                    'success': True,
                    'saved': False,
                    'message': '已经收藏过了'
                }
    
    async def unsave_job(self, user_id: str, job_id: int) -> bool:
        async with self.get_connection() as conn:
            cursor = await conn.execute('''
                DELETE FROM saved_jobs WHERE user_id = ? AND job_id = ?
            ''', (user_id, job_id))
            await conn.commit()
            return cursor.rowcount > 0
    
    async def is_job_saved(self, user_id: str, job_id: int) -> bool:
        async with self.get_connection() as conn:
            cursor = await conn.execute('''
                SELECT id FROM saved_jobs WHERE user_id = ? AND job_id = ?
            ''', (user_id, job_id))
            row = await cursor.fetchone()
            return row is not None
    
    async def get_saved_jobs(self, user_id: str) -> List[int]:
        async with self.get_connection() as conn:
            cursor = await conn.execute('''
                SELECT job_id FROM saved_jobs WHERE user_id = ? ORDER BY created_at DESC
            ''', (user_id,))
            rows = await cursor.fetchall()
            return [row['job_id'] for row in rows]


db_service = APIDatabaseService()
