import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

from ..models.job_listing import JobListing


class HimalayasSpider:
    SOURCE = "himalayas"
    BASE_URL = "https://himalayas.app"
    API_URL = "https://himalayas.app/jobs/api"
    SEARCH_API_URL = "https://himalayas.app/jobs/api/search"
    
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://himalayas.app/",
    }
    
    CATEGORIES = [
        'engineering', 'design', 'product', 'marketing', 'sales',
        'data', 'devops', 'finance', 'operations', 'all'
    ]
    
    EMPLOYMENT_TYPES = {
        'Full Time': 'Full-time',
        'Part Time': 'Part-time',
        'Contractor': 'Contract',
        'Temporary': 'Temporary',
        'Intern': 'Internship',
        'Volunteer': 'Volunteer',
    }
    
    SENIORITY_MAP = {
        'Entry-level': 'Entry',
        'Mid-level': 'Mid',
        'Senior': 'Senior',
        'Manager': 'Manager',
        'Director': 'Director',
        'Executive': 'Executive',
    }
    
    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
    
    def fetch_api(self, offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        time.sleep(self.delay)
        
        params = {
            'offset': offset,
            'limit': limit,
        }
        
        response = self.session.get(self.API_URL, params=params, timeout=(10, 30))
        response.raise_for_status()
        return response.json()
    
    def search_api(self, query: str = None, seniority: str = None, 
                    employment_type: str = None, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        time.sleep(self.delay)
        
        params = {'limit': limit, 'page': page}
        if query:
            params['q'] = query
        if seniority:
            params['seniority'] = seniority
        if employment_type:
            params['employment_type'] = employment_type
        
        response = self.session.get(self.SEARCH_API_URL, params=params, timeout=(10, 30))
        response.raise_for_status()
        return response.json()
    
    def parse_job(self, job_data: Dict[str, Any]) -> Optional[JobListing]:
        if not job_data:
            return None
        
        try:
            guid = job_data.get('guid', '')
            if not guid:
                return None
            
            job_id = self._extract_job_id(guid)
            if not job_id:
                return None
            
            title = job_data.get('title', '')
            company = job_data.get('companyName', '')
            description = job_data.get('description', '')
            application_link = job_data.get('applicationLink', '') or guid
            
            company_logo = job_data.get('companyLogo', '')
            
            employment_type = job_data.get('employmentType', '')
            if employment_type in self.EMPLOYMENT_TYPES:
                employment_type = self.EMPLOYMENT_TYPES[employment_type]
            
            min_salary = job_data.get('minSalary')
            max_salary = job_data.get('maxSalary')
            currency = job_data.get('currency', 'USD')
            
            salary = ''
            if min_salary and max_salary:
                salary = f"${min_salary} - ${max_salary} {currency}"
            elif min_salary:
                salary = f"${min_salary}+ {currency}"
            elif max_salary:
                salary = f"Up to ${max_salary} {currency}"
            
            location_restrictions = job_data.get('locationRestrictions', [])
            location = ''
            if location_restrictions:
                location = ', '.join(location_restrictions)
            if not location:
                timezone_restrictions = job_data.get('timezoneRestrictions', [])
                if timezone_restrictions:
                    timezone_strs = [f'UTC{tz:+d}' if tz != 0 else 'UTC' for tz in timezone_restrictions]
                    location = f"Timezones: {', '.join(timezone_strs)}"
            if not location:
                location = 'Remote (Worldwide)'
            
            categories = job_data.get('categories', []) or []
            parent_categories = job_data.get('parentCategories', []) or []
            seniority = job_data.get('seniority', []) or []
            
            all_tags = []
            if categories:
                all_tags.extend(categories)
            if parent_categories:
                all_tags.extend(parent_categories)
            if seniority:
                all_tags.extend([f"{s}" for s in seniority])
            if employment_type:
                all_tags.append(employment_type)
            
            tags_str = ', '.join(all_tags) if all_tags else ''
            
            pub_date = job_data.get('pubDate')
            posted_at = None
            if pub_date:
                try:
                    if isinstance(pub_date, (int, float)):
                        posted_at = datetime.fromtimestamp(pub_date)
                    elif isinstance(pub_date, str):
                        from dateutil import parser
                        posted_at = parser.parse(pub_date, fuzzy=True)
                except Exception:
                    pass
            
            return JobListing(
                source=self.SOURCE,
                job_id=f"hml_{job_id}",
                title=title,
                company=company,
                company_logo=company_logo,
                description=self._clean_description(description),
                location=location,
                job_type=employment_type,
                salary=salary,
                tags=tags_str if tags_str else 'remote, himalayas',
                job_url=application_link,
                posted_at=posted_at,
            )
            
        except Exception as e:
            return None
    
    def _extract_job_id(self, guid: str) -> Optional[str]:
        if not guid:
            return None
        
        patterns = [
            r'/jobs/([^/\?]+)',
            r'/companies/[^/]+/jobs/([^/\?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, guid)
            if match:
                return match.group(1)
        
        import hashlib
        return hashlib.md5(guid.encode()).hexdigest()[:12]
    
    def _clean_description(self, html_text: str) -> str:
        if not html_text:
            return ""
        
        try:
            soup = BeautifulSoup(html_text, 'lxml')
            
            for br in soup.find_all('br'):
                br.replace_with('\n')
            for p in soup.find_all('p'):
                p.append('\n\n')
            for li in soup.find_all('li'):
                li.insert_before('• ')
                li.append('\n')
            
            for a in soup.find_all('a'):
                href = a.get('href', '')
                text = a.get_text(strip=True)
                if href and href.startswith('http'):
                    if text:
                        a.replace_with(f"{text} ({href})")
                    else:
                        a.replace_with(href)
            
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
    
    def crawl(self, categories: List[str] = None, max_jobs: int = 200,
              existing_ids: set = None, stop_after_duplicates: int = 10) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        offset = 0
        limit = 20
        
        print(f"  [Himalayas] 开始从 API 爬取 (总数约 100,000+)...")
        
        while len(all_jobs) < max_jobs:
            if consecutive_duplicates >= stop_after_duplicates:
                print(f"  [Himalayas] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                break
            
            try:
                data = self.fetch_api(offset=offset, limit=limit)
                jobs_list = data.get('jobs', [])
                
                if not jobs_list:
                    print(f"  [Himalayas] 没有更多职位，停止爬取")
                    break
                
                print(f"  [Himalayas] 获取到 {len(jobs_list)} 个职位 (offset={offset})")
                
                for job_data in jobs_list:
                    if len(all_jobs) >= max_jobs:
                        break
                    
                    guid = job_data.get('guid', '')
                    raw_id = self._extract_job_id(guid)
                    job_id = f"hml_{raw_id}" if raw_id else ""
                    
                    if not job_id or job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)
                    
                    if job_id in existing_ids:
                        consecutive_duplicates += 1
                        if consecutive_duplicates >= stop_after_duplicates:
                            print(f"  [Himalayas] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    job = self.parse_job(job_data)
                    if job:
                        all_jobs.append(job)
                
                offset += limit
                
            except Exception as e:
                print(f"  [Himalayas] 获取职位时出错: {e}")
                break
        
        return all_jobs
    
    def close(self):
        self.session.close()
