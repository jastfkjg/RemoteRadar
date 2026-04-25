from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class JobSchema(BaseModel):
    id: Optional[int] = None
    source: str = ""
    job_id: str = ""
    title: str = ""
    company: str = ""
    company_url: str = ""
    company_logo: str = ""
    description: str = ""
    location: str = ""
    job_type: str = ""
    salary: str = ""
    tags: str = ""
    job_url: str = ""
    posted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    categories: str = ""
    tech_stacks: str = ""
    seniority: str = ""
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }


class JobCreateSchema(BaseModel):
    source: str
    job_id: str
    title: str = ""
    company: str = ""
    company_url: str = ""
    company_logo: str = ""
    description: str = ""
    location: str = ""
    job_type: str = ""
    salary: str = ""
    tags: str = ""
    job_url: str = ""
    posted_at: Optional[datetime] = None
    categories: str = ""
    tech_stacks: str = ""
    seniority: str = ""


class BatchCreateRequest(BaseModel):
    jobs: List[JobCreateSchema]


class BatchCreateResponse(BaseModel):
    total: int
    new: int
    updated: int
    job_ids: List[int]


class JobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    jobs: List[JobSchema]
    has_new: bool = False
    last_updated: Optional[datetime] = None


class StatsResponse(BaseModel):
    total_jobs: int
    by_source: dict[str, int]
    sources: List[str]
    job_types: List[str]
    categories: List[str] = []
    tech_stacks: List[str] = []
    seniority_levels: List[str] = []
    latest_update: Optional[datetime] = None


class FilterOptions(BaseModel):
    sources: List[str] = []
    job_types: List[str] = []
    locations: List[str] = []
    categories: List[str] = []
    tech_stacks: List[str] = []
    seniority_levels: List[str] = []
    date_ranges: Dict[str, str] = {
        "today": "今天",
        "week": "本周",
        "month": "本月",
        "all": "全部",
    }


class UserProfileSchema(BaseModel):
    user_id: str
    categories: List[str] = []
    tech_stacks: List[str] = []
    seniority: Optional[str] = None
    locations: List[str] = []
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None


class UserProfileUpdate(BaseModel):
    categories: Optional[List[str]] = None
    tech_stacks: Optional[List[str]] = None
    seniority: Optional[str] = None
    locations: Optional[List[str]] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None


class UserActionSchema(BaseModel):
    user_id: str
    job_id: int
    action_type: str
    duration_seconds: Optional[int] = None


class RecommendationItem(BaseModel):
    job_id: int
    job: Dict[str, Any]
    score: float
    reasons: List[str]


class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[RecommendationItem]
    is_hot: bool = False


class InferredProfileResponse(BaseModel):
    categories: List[str]
    tech_stacks: List[str]
    seniority: Optional[str]
    locations: List[str]
