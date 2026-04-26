import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests

from ..models.job_listing import JobListing


class ArbeitnowSpider:
    SOURCE = "arbeitnow"
    BASE_URL = "https://www.arbeitnow.com"
    API_URL = "https://www.arbeitnow.com/api/job-board-api"
    
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.arbeitnow.com/",
    }
    
    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
    
    def fetch_api(self, page: int = 1, remote_only: bool = True) -> Dict[str, Any]:
        time.sleep(self.delay)
        
        params = {
            'page': page,
        }
        if remote_only:
            params['remote'] = 'true'
        
        response = self.session.get(self.API_URL, params=params, timeout=(10, 30))
        response.raise_for_status()
        return response.json()
    
    def parse_job(self, job_data: Dict[str, Any]) -> Optional[JobListing]:
        if not job_data:
            return None
        
        try:
            job_id = job_data.get('slug', '') or str(job_data.get('id', ''))
            if not job_id:
                return None
            
            title = job_data.get('title', '')
            company = job_data.get('company_name', '')
            description = job_data.get('description', '')
            location = job_data.get('location', '')
            job_url = job_data.get('url', '') or f"{self.BASE_URL}/jobs/{job_id}"
            
            salary = job_data.get('salary', '') or ''
            
            tags = job_data.get('tags', []) or []
            job_types = job_data.get('job_types', []) or []
            
            all_tags = tags + job_types
            tags_str = ', '.join(all_tags) if all_tags else ''
            
            posted_at = None
            created_at = job_data.get('created_at')
            if created_at:
                if isinstance(created_at, int):
                    try:
                        posted_at = datetime.fromtimestamp(created_at)
                    except Exception:
                        pass
                elif isinstance(created_at, str):
                    try:
                        from dateutil import parser
                        posted_at = parser.parse(created_at, fuzzy=True)
                    except Exception:
                        pass
            
            is_remote = job_data.get('remote', False)
            if is_remote and 'Remote' not in location and location:
                location = f"Remote ({location})"
            elif is_remote and not location:
                location = "Remote"
            
            company_logo = job_data.get('logo', '') or ''
            
            job_type = ''
            if job_types:
                job_type = ', '.join(job_types)
            
            return JobListing(
                source=self.SOURCE,
                job_id=f"atn_{job_id}",
                title=title,
                company=company,
                company_logo=company_logo,
                description=self._clean_description(description),
                location=location if location else 'Remote',
                job_type=job_type,
                salary=str(salary) if salary else '',
                tags=tags_str if tags_str else 'remote, arbeitnow',
                job_url=job_url,
                posted_at=posted_at,
            )
            
        except Exception as e:
            return None
    
    def crawl(self, max_pages: int = 5, max_jobs: int = 200,
              existing_ids: set = None, stop_after_duplicates: int = 10) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        for page in range(1, max_pages + 1):
            if len(all_jobs) >= max_jobs:
                break
            
            if consecutive_duplicates >= stop_after_duplicates:
                print(f"  [Arbeitnow] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                break
            
            try:
                print(f"  [Arbeitnow] Fetching page {page}...")
                data = self.fetch_api(page=page, remote_only=True)
                
                jobs_list = data.get('data', [])
                if not jobs_list:
                    print(f"  [Arbeitnow] No jobs on page {page}, stopping")
                    break
                
                for job_data in jobs_list:
                    if len(all_jobs) >= max_jobs:
                        break
                    
                    raw_id = job_data.get('slug', '') or str(job_data.get('id', ''))
                    job_id = f"atn_{raw_id}" if raw_id else ""
                    
                    if not job_id or job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)
                    
                    if job_id in existing_ids:
                        consecutive_duplicates += 1
                        if consecutive_duplicates >= stop_after_duplicates:
                            print(f"  [Arbeitnow] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    job = self.parse_job(job_data)
                    if job:
                        all_jobs.append(job)
                        
            except Exception as e:
                print(f"  [Arbeitnow] Error on page {page}: {e}")
                continue
        
        return all_jobs
    
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
            
            for script in soup.find_all('script'):
                script.decompose()
            for style in soup.find_all('style'):
                style.decompose()
            
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
