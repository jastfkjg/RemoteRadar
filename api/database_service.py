import sqlite3
import aiosqlite
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Set
from contextlib import asynccontextmanager

from api.schemas import JobSchema


class APIDatabaseService:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
    
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


db_service = APIDatabaseService()
