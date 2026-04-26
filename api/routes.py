from fastapi import APIRouter, Query, HTTPException, Depends, status
from typing import Optional, List
from datetime import datetime

from api.schemas import (
    JobSchema, JobListResponse, StatsResponse, FilterOptions,
    BatchCreateRequest, BatchCreateResponse,
    UserProfileSchema, UserProfileUpdate, UserActionSchema,
    RecommendationResponse, InferredProfileResponse,
    AuthUser, AuthRegisterRequest, AuthLoginRequest, AuthTokenResponse,
    SaveJobRequest, SaveJobResponse, SavedJobsResponse
)
from api.database_service import db_service
from api.auth import get_api_key, get_api_key_optional, get_current_user, get_current_user_required
from api.user_auth import (
    get_password_hash, verify_password, create_access_token,
    User as AuthUserModel
)
from api.recommender import Recommender


router = APIRouter(prefix="/api", tags=["jobs"])

recommender = Recommender()


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
    current_user: Optional[dict] = Depends(get_current_user),
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
    
    if current_user:
        saved_job_ids = await db_service.get_saved_jobs(current_user['user_id'])
        saved_set = set(saved_job_ids)
        for job in jobs:
            job.is_saved = job.id in saved_set
    
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
async def get_job_detail(
    job_id: int,
    current_user: Optional[dict] = Depends(get_current_user),
):
    job = await db_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    
    if current_user:
        job.is_saved = await db_service.is_job_saved(current_user['user_id'], job_id)
    
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


@router.get("/jobs/existing-ids/{source}")
async def get_existing_job_ids(
    source: str,
    api_key: str = Depends(get_api_key)
):
    existing_ids = await db_service.get_existing_job_ids(source)
    return {
        "source": source,
        "existing_ids": list(existing_ids),
        "count": len(existing_ids)
    }


@router.post("/jobs/batch", response_model=BatchCreateResponse)
async def batch_create_jobs(
    request: BatchCreateRequest,
    api_key: str = Depends(get_api_key)
):
    jobs_data = []
    for job in request.jobs:
        job_dict = job.model_dump()
        if job_dict.get('posted_at'):
            job_dict['posted_at'] = job_dict['posted_at'].isoformat() if job_dict['posted_at'] else None
        jobs_data.append(job_dict)
    
    result = await db_service.batch_insert_jobs(jobs_data)
    return BatchCreateResponse(**result)


@router.post("/auth/register", response_model=AuthTokenResponse)
async def register(request: AuthRegisterRequest):
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码至少需要6个字符"
        )
    
    if len(request.username) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名至少需要2个字符"
        )
    
    existing = await db_service.get_user_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    password_hash = get_password_hash(request.password)
    result = await db_service.create_user(
        email=request.email,
        username=request.username,
        password_hash=password_hash
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get('error', '注册失败')
        )
    
    user = await db_service.get_user_by_user_id(result['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )
    
    access_token = create_access_token(data={"sub": user['user_id']})
    
    await db_service.update_last_login(user['user_id'])
    
    return AuthTokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=AuthUser(
            id=user['id'],
            user_id=user['user_id'],
            email=user['email'],
            username=user['username'],
            created_at=datetime.fromisoformat(user['created_at']) if user['created_at'] else None,
            last_login=datetime.fromisoformat(user['last_login']) if user['last_login'] else None,
        )
    )


@router.post("/auth/login", response_model=AuthTokenResponse)
async def login(request: AuthLoginRequest):
    user = await db_service.get_user_by_email(request.email)
    
    if not user or not verify_password(request.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user['user_id']})
    
    await db_service.update_last_login(user['user_id'])
    
    return AuthTokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=AuthUser(
            id=user['id'],
            user_id=user['user_id'],
            email=user['email'],
            username=user['username'],
            created_at=datetime.fromisoformat(user['created_at']) if user['created_at'] else None,
            last_login=datetime.fromisoformat(user['last_login']) if user['last_login'] else None,
        )
    )


@router.get("/auth/me", response_model=AuthUser)
async def get_me(current_user: dict = Depends(get_current_user_required)):
    return AuthUser(
        id=current_user['id'],
        user_id=current_user['user_id'],
        email=current_user['email'],
        username=current_user['username'],
        created_at=datetime.fromisoformat(current_user['created_at']) if current_user['created_at'] else None,
        last_login=datetime.fromisoformat(current_user['last_login']) if current_user['last_login'] else None,
    )


@router.get("/profiles/me", response_model=UserProfileSchema)
async def get_my_profile(current_user: dict = Depends(get_current_user_required)):
    profile = recommender.get_user_or_create(current_user['user_id'])
    return UserProfileSchema(
        user_id=profile.user_id,
        categories=profile.categories,
        tech_stacks=profile.tech_stacks,
        seniority=profile.seniority,
        locations=profile.locations,
        min_salary=profile.min_salary,
        max_salary=profile.max_salary,
    )


@router.put("/profiles/me", response_model=UserProfileSchema)
async def update_my_profile(
    update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user_required)
):
    profile_data = {}
    if update.categories is not None:
        profile_data['categories'] = update.categories
    if update.tech_stacks is not None:
        profile_data['tech_stacks'] = update.tech_stacks
    if update.seniority is not None:
        profile_data['seniority'] = update.seniority
    if update.locations is not None:
        profile_data['locations'] = update.locations
    if update.min_salary is not None:
        profile_data['min_salary'] = update.min_salary
    if update.max_salary is not None:
        profile_data['max_salary'] = update.max_salary
    
    profile = recommender.update_user_profile(current_user['user_id'], profile_data)
    return UserProfileSchema(
        user_id=profile.user_id,
        categories=profile.categories,
        tech_stacks=profile.tech_stacks,
        seniority=profile.seniority,
        locations=profile.locations,
        min_salary=profile.min_salary,
        max_salary=profile.max_salary,
    )


@router.post("/actions")
async def record_user_action(
    action: UserActionSchema,
    current_user: dict = Depends(get_current_user_required)
):
    action_id = recommender.record_user_action(
        user_id=current_user['user_id'],
        job_id=action.job_id,
        action_type=action.action_type,
        duration_seconds=action.duration_seconds,
    )
    return {
        "status": "ok",
        "action_id": action_id,
    }


@router.get("/profiles/me/infer", response_model=InferredProfileResponse)
async def infer_my_profile(current_user: dict = Depends(get_current_user_required)):
    inferred = recommender.infer_profile_from_actions(current_user['user_id'])
    return InferredProfileResponse(**inferred)


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_my_recommendations(
    current_user: dict = Depends(get_current_user_required),
    limit: int = Query(20, ge=1, le=100, description="推荐数量"),
    days: int = Query(14, ge=1, le=60, description="考虑最近多少天的职位"),
):
    recommendations = recommender.get_recommendations(
        user_id=current_user['user_id'], 
        limit=limit, 
        days=days
    )
    
    is_hot = all(r['score'] == 0 for r in recommendations) if recommendations else False
    
    return RecommendationResponse(
        user_id=current_user['user_id'],
        recommendations=recommendations,
        is_hot=is_hot,
    )


@router.post("/saved-jobs", response_model=SaveJobResponse)
async def save_job(
    request: SaveJobRequest,
    current_user: dict = Depends(get_current_user_required)
):
    result = await db_service.save_job(current_user['user_id'], request.job_id)
    return SaveJobResponse(
        success=result['success'],
        saved=result.get('saved', False),
        message=result.get('message', ''),
    )


@router.delete("/saved-jobs/{job_id}", response_model=SaveJobResponse)
async def unsave_job(
    job_id: int,
    current_user: dict = Depends(get_current_user_required)
):
    result = await db_service.unsave_job(current_user['user_id'], job_id)
    return SaveJobResponse(
        success=True,
        saved=False,
        message="已取消收藏" if result else "职位未收藏",
    )


@router.get("/saved-jobs", response_model=SavedJobsResponse)
async def get_saved_jobs(current_user: dict = Depends(get_current_user_required)):
    job_ids = await db_service.get_saved_jobs(current_user['user_id'])
    return SavedJobsResponse(
        job_ids=job_ids,
        count=len(job_ids),
    )


@router.get("/saved-jobs/check/{job_id}")
async def check_saved_job(
    job_id: int,
    current_user: dict = Depends(get_current_user_required)
):
    is_saved = await db_service.is_job_saved(current_user['user_id'], job_id)
    return {
        "job_id": job_id,
        "is_saved": is_saved,
    }
