from datetime import datetime
from typing import Optional, List
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
    
    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }


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
    latest_update: Optional[datetime] = None


class FilterOptions(BaseModel):
    sources: List[str] = []
    job_types: List[str] = []
    locations: List[str] = []
    date_ranges: dict[str, str] = {}
