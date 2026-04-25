from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class JobListing:
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'job_id': self.job_id,
            'title': self.title,
            'company': self.company,
            'company_url': self.company_url,
            'company_logo': self.company_logo,
            'description': self.description,
            'location': self.location,
            'job_type': self.job_type,
            'salary': self.salary,
            'tags': self.tags,
            'job_url': self.job_url,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'categories': self.categories,
            'tech_stacks': self.tech_stacks,
            'seniority': self.seniority,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            source=data.get('source', ''),
            job_id=data.get('job_id', ''),
            title=data.get('title', ''),
            company=data.get('company', ''),
            company_url=data.get('company_url', ''),
            company_logo=data.get('company_logo', ''),
            description=data.get('description', ''),
            location=data.get('location', ''),
            job_type=data.get('job_type', ''),
            salary=data.get('salary', ''),
            tags=data.get('tags', ''),
            job_url=data.get('job_url', ''),
            posted_at=datetime.fromisoformat(data['posted_at']) if data.get('posted_at') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            categories=data.get('categories', ''),
            tech_stacks=data.get('tech_stacks', ''),
            seniority=data.get('seniority', ''),
        )
    
    def auto_classify(self):
        from src.classifier import job_classifier
        classified = job_classifier.classify(
            title=self.title,
            description=self.description,
            location=self.location
        )
        self.categories = ', '.join(classified.get('categories', []))
        self.tech_stacks = ', '.join(classified.get('tech_stacks', []))
        self.seniority = ', '.join(classified.get('seniority', []))
    
    def get_categories_list(self) -> List[str]:
        return [t.strip() for t in self.categories.split(',') if t.strip()]
    
    def get_tech_stacks_list(self) -> List[str]:
        return [t.strip() for t in self.tech_stacks.split(',') if t.strip()]
    
    def get_seniority_list(self) -> List[str]:
        return [t.strip() for t in self.seniority.split(',') if t.strip()]
