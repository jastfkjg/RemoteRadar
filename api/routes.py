from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime

from api.schemas import JobSchema, JobListResponse, StatsResponse, FilterOptions
from api.database_service import db_service


router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs", response_model=JobListResponse)
async def get_jobs(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    source: Optional[str] = Query(None, description="筛选来源 (v2ex, wework, remoteok)"),
    job_type: Optional[str] = Query(None, description="筛选职位类型（原始）"),
    location: Optional[str] = Query(None, description="筛选工作地点"),
    days_ago: Optional[int] = Query(None, ge=1, description="筛选最近N天内的职位"),
    search: Optional[str] = Query(None, description="搜索关键词 (职位名、公司名、描述)"),
    category: Optional[str] = Query(None, description="筛选职位类别 (前端开发、后端开发、全栈开发等)"),
    tech_stack: Optional[str] = Query(None, description="筛选技术栈 (Python、JavaScript、React等)"),
    seniority: Optional[str] = Query(None, description="筛选职级 (实习、初级、中级、高级等)"),
    sort_by: str = Query("posted_at", description="排序字段 (posted_at, created_at, updated_at, title, company)"),
    sort_order: str = Query("desc", description="排序方式 (asc, desc)"),
    since_time: Optional[str] = Query(None, description="仅获取此时间之后更新的数据 (用于轮询，ISO格式)"),
):
    jobs, total, total_pages = await db_service.get_jobs(
        page=page,
        page_size=page_size,
        source=source,
        job_type=job_type,
        location=location,
        days_ago=days_ago,
        search=search,
        category=category,
        tech_stack=tech_stack,
        seniority=seniority,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    has_new = False
    latest_updated = await db_service.get_latest_update_time()
    
    if since_time:
        try:
            since_dt = datetime.fromisoformat(since_time)
            for job in jobs:
                if job.updated_at and job.updated_at > since_dt:
                    has_new = True
                    break
        except ValueError:
            pass
    
    return JobListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        jobs=jobs,
        has_new=has_new,
        last_updated=latest_updated,
    )


@router.get("/jobs/{job_id}", response_model=JobSchema)
async def get_job_detail(job_id: int):
    job = await db_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    return job


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    stats = await db_service.get_stats()
    return StatsResponse(**stats)


@router.get("/filters", response_model=FilterOptions)
async def get_filter_options():
    sources = await db_service.get_sources()
    job_types = await db_service.get_job_types()
    locations = await db_service.get_locations()
    categories = await db_service.get_categories()
    tech_stacks = await db_service.get_tech_stacks()
    seniority_levels = await db_service.get_seniority_levels()
    
    return FilterOptions(
        sources=sources,
        job_types=job_types,
        locations=locations,
        categories=categories,
        tech_stacks=tech_stacks,
        seniority_levels=seniority_levels,
        date_ranges={
            "today": "今天",
            "week": "本周",
            "month": "本月",
            "all": "全部",
        }
    )


@router.get("/health")
async def health_check():
    stats = await db_service.get_stats()
    return {
        "status": "healthy",
        "total_jobs": stats.get("total_jobs", 0),
        "timestamp": datetime.now().isoformat(),
    }
