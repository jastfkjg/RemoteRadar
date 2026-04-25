import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests

from ..models.job_listing import JobListing


class RemoteOkSpider:
    SOURCE = "remoteok"
    BASE_URL = "https://remoteok.com"
    API_URL = "https://remoteok.com/api"
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/json, text/plain",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
    
    def fetch_api(self, endpoint: str = "", params: Dict = None) -> List[Dict[str, Any]]:
        time.sleep(self.delay)
        
        url = f"{self.API_URL}{endpoint}"
        response = self.session.get(url, params=params or {}, timeout=(10, 30))
        response.raise_for_status()
        
        data = response.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        return []
    
    def fetch_jobs(self, tag: str = None) -> List[Dict[str, Any]]:
        if tag:
            return self.fetch_api(f"/{tag}")
        return self.fetch_api()
    
    def parse_job(self, job_data: Dict[str, Any]) -> Optional[JobListing]:
        if not job_data:
            return None
        
        try:
            job_id = job_data.get('id', '')
            if not job_id:
                return None
            
            slug = job_data.get('slug', '')
            job_url = f"{self.BASE_URL}/remote-jobs/{slug}" if slug else ""
            
            company = job_data.get('company', '')
            title = job_data.get('position', '')
            description = job_data.get('description', '')
            location = job_data.get('location', '')
            
            posted_at = None
            date_str = job_data.get('date', '')
            if date_str:
                posted_at = self._parse_date(date_str)
            
            tags = job_data.get('tags', [])
            tags_str = ', '.join(tags) if tags else ''
            
            company_logo = job_data.get('logo', '')
            salary = job_data.get('salary_min', '') or job_data.get('salary', '')
            if salary and job_data.get('salary_max'):
                salary = f"{salary} - {job_data.get('salary_max')}"
            
            job_type = job_data.get('job_type', '')
            
            return JobListing(
                source=self.SOURCE,
                job_id=f"rok_{job_id}",
                title=title,
                company=company,
                company_url=job_data.get('url', ''),
                company_logo=company_logo,
                description=self._clean_description(description),
                location=location,
                job_type=job_type,
                salary=str(salary) if salary else '',
                tags=tags_str if tags_str else f'remote, {self.SOURCE}',
                job_url=job_url,
                posted_at=posted_at,
            )
            
        except Exception as e:
            return None
    
    def crawl(self, tags: List[str] = None, max_jobs: int = 100, 
              existing_ids: set = None, stop_after_duplicates: int = 5) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        if tags:
            for tag in tags:
                try:
                    jobs_data = self.fetch_jobs(tag)
                    
                    for job_data in jobs_data:
                        if len(all_jobs) >= max_jobs:
                            break
                        
                        raw_id = job_data.get('id', '')
                        job_id = f"rok_{raw_id}" if raw_id else ""
                        
                        if not job_id or job_id in seen_ids:
                            continue
                        seen_ids.add(job_id)
                        
                        if job_id in existing_ids:
                            consecutive_duplicates += 1
                            if consecutive_duplicates >= stop_after_duplicates:
                                print(f"  [RemoteOk] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                                return all_jobs
                            continue
                        
                        consecutive_duplicates = 0
                        job = self.parse_job(job_data)
                        if job:
                            all_jobs.append(job)
                            
                except Exception as e:
                    continue
        else:
            try:
                jobs_data = self.fetch_jobs()
                
                for job_data in jobs_data:
                    if len(all_jobs) >= max_jobs:
                        break
                    
                    raw_id = job_data.get('id', '')
                    job_id = f"rok_{raw_id}" if raw_id else ""
                    
                    if not job_id or job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)
                    
                    if job_id in existing_ids:
                        consecutive_duplicates += 1
                        if consecutive_duplicates >= stop_after_duplicates:
                            print(f"  [RemoteOk] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    job = self.parse_job(job_data)
                    if job:
                        all_jobs.append(job)
                        
            except Exception as e:
                pass
        
        return all_jobs
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        
        try:
            from dateutil import parser
            return parser.parse(date_str, fuzzy=True)
        except Exception:
            try:
                from datetime import timedelta
                
                patterns = [
                    (r'(\d+)\s*days?', 'days'),
                    (r'(\d+)\s*hours?', 'hours'),
                    (r'(\d+)\s*minutes?', 'minutes'),
                    (r'(\d+)\s*weeks?', 'weeks'),
                ]
                
                now = datetime.now()
                
                for pattern, unit in patterns:
                    match = re.search(pattern, date_str, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if unit == 'days':
                            return now - timedelta(days=count)
                        elif unit == 'hours':
                            return now - timedelta(hours=count)
                        elif unit == 'minutes':
                            return now - timedelta(minutes=count)
                        elif unit == 'weeks':
                            return now - timedelta(weeks=count)
            
            except Exception:
                return None
        
        return None
    
    def _clean_description(self, html_text: str) -> str:
        if not html_text:
            return ""
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_text, 'lxml')
            
            for br in soup.find_all('br'):
                br.replace_with('\n')
            for p in soup.find_all('p'):
                p.append('\n\n')
            for li in soup.find_all('li'):
                li.insert_before('• ')
                li.append('\n')
            
            text = soup.get_text()
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped:
                    cleaned_lines.append(stripped)
            
            return '\n'.join(cleaned_lines)
            
        except Exception:
            return html_text
    
    def close(self):
        self.session.close()
