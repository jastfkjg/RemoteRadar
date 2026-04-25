"""
API 客户端模块
用于爬虫调用远程 API 写入数据（替代本地 SQLite）
"""

import os
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, Set
from dotenv import load_dotenv

load_dotenv()


class RemoteAPIClient:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or os.getenv("API_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("API_KEY", "dev-api-key-12345")
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=60, connect=10)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_existing_job_ids(self, source: str) -> Set[str]:
        session = await self._get_session()
        headers = {"X-API-Key": self.api_key}
        
        async with session.get(
            f"{self.api_url}/api/jobs/existing-ids/{source}",
            headers=headers
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"获取已存在职位ID失败: {resp.status} - {text}")
            
            data = await resp.json()
            return set(data.get("existing_ids", []))
    
    async def batch_create_jobs(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not jobs:
            return {"total": 0, "new": 0, "updated": 0, "job_ids": []}
        
        session = await self._get_session()
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {"jobs": jobs}
        
        async with session.post(
            f"{self.api_url}/api/jobs/batch",
            json=payload,
            headers=headers
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"批量创建职位失败: {resp.status} - {text}")
            
            return await resp.json()
    
    async def send_jobs_in_batches(
        self, 
        jobs: List[Dict[str, Any]], 
        batch_size: int = 50
    ) -> Dict[str, Any]:
        total_new = 0
        total_updated = 0
        all_job_ids = []
        
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            print(f"  发送批次 {i//batch_size + 1}: {len(batch)} 个职位...")
            
            try:
                result = await self.batch_create_jobs(batch)
                total_new += result.get("new", 0)
                total_updated += result.get("updated", 0)
                all_job_ids.extend(result.get("job_ids", []))
            except Exception as e:
                print(f"  批次 {i//batch_size + 1} 发送失败: {e}")
                raise
        
        return {
            "total": len(jobs),
            "new": total_new,
            "updated": total_updated,
            "job_ids": all_job_ids,
        }
    
    async def health_check(self) -> Dict[str, Any]:
        session = await self._get_session()
        
        async with session.get(f"{self.api_url}/api/health") as resp:
            if resp.status != 200:
                raise Exception(f"健康检查失败: {resp.status}")
            return await resp.json()


def job_listing_to_api_dict(job) -> Dict[str, Any]:
    from src.models import JobListing
    
    if isinstance(job, JobListing):
        return {
            "source": job.source,
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "company_url": job.company_url,
            "company_logo": job.company_logo,
            "description": job.description,
            "location": job.location,
            "job_type": job.job_type,
            "salary": job.salary,
            "tags": job.tags,
            "job_url": job.job_url,
            "posted_at": job.posted_at.isoformat() if job.posted_at else None,
            "categories": job.categories,
            "tech_stacks": job.tech_stacks,
            "seniority": job.seniority,
        }
    
    return dict(job)
