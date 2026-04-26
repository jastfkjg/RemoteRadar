import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests

from ..models.job_listing import JobListing


class JobicySpider:
    SOURCE = "jobicy"
    BASE_URL = "https://jobicy.com"
    API_URL = "https://jobicy.com/api/v2/remote-jobs"
    
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://jobicy.com/",
    }
    
    CATEGORIES = [
        'developer', 'devops', 'design', 'marketing', 'sales',
        'product', 'data', 'finance', 'legal', 'writing', 'all'
    ]
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
    
    def fetch_api(self, category: str = None, count: int = 50) -> Dict[str, Any]:
        time.sleep(self.delay)
        
        params = {
            'count': count,
        }
        if category and category != 'all':
            params['industry'] = category
        
        response = self.session.get(self.API_URL, params=params, timeout=(10, 30))
        response.raise_for_status()
        return response.json()
    
    def parse_job(self, job_data: Dict[str, Any]) -> Optional[JobListing]:
        if not job_data:
            return None
        
        try:
            job_id = job_data.get('id', '') or job_data.get('slug', '')
            if not job_id:
                return None
            
            title = job_data.get('jobTitle', '') or job_data.get('title', '')
            company = job_data.get('companyName', '') or job_data.get('company', '')
            description = job_data.get('jobDescription', '') or job_data.get('description', '')
            
            location = job_data.get('jobGeo', '') or ''
            if not location:
                regions = job_data.get('region', []) or []
                if regions:
                    location = ', '.join(regions)
            
            job_url = job_data.get('url', '') or job_data.get('jobLink', '')
            if not job_url and job_id:
                job_url = f"{self.BASE_URL}/job/{job_id}"
            
            salary_min = job_data.get('annualSalaryMin', '')
            salary_max = job_data.get('annualSalaryMax', '')
            salary_currency = job_data.get('salaryCurrency', 'USD')
            
            salary = ''
            if salary_min and salary_max:
                salary = f"${salary_min}K - ${salary_max}K {salary_currency}"
            elif salary_min:
                salary = f"${salary_min}K+ {salary_currency}"
            elif salary_max:
                salary = f"Up to ${salary_max}K {salary_currency}"
            
            tags = []
            job_industry = job_data.get('jobIndustry', []) or []
            if job_industry:
                if isinstance(job_industry, list):
                    tags.extend(job_industry)
                else:
                    tags.append(str(job_industry))
            
            job_type = job_data.get('jobType', '') or ''
            if job_type:
                tags.append(job_type)
            
            tags_str = ', '.join(tags) if tags else ''
            
            posted_at = None
            pub_date = job_data.get('pubDate', '') or ''
            if pub_date:
                try:
                    from dateutil import parser
                    posted_at = parser.parse(pub_date, fuzzy=True)
                except Exception:
                    try:
                        from datetime import timedelta
                        
                        patterns = [
                            (r'(\d+)\s*hours?', 'hours'),
                            (r'(\d+)\s*days?', 'days'),
                            (r'(\d+)\s*weeks?', 'weeks'),
                        ]
                        
                        now = datetime.now()
                        
                        for pattern, unit in patterns:
                            match = re.search(pattern, pub_date, re.IGNORECASE)
                            if match:
                                count = int(match.group(1))
                                if unit == 'hours':
                                    posted_at = now - timedelta(hours=count)
                                elif unit == 'days':
                                    posted_at = now - timedelta(days=count)
                                elif unit == 'weeks':
                                    posted_at = now - timedelta(weeks=count)
                                break
                    except Exception:
                        pass
            
            company_logo = job_data.get('companyLogo', '') or ''
            company_url = job_data.get('companyUrl', '') or ''
            
            return JobListing(
                source=self.SOURCE,
                job_id=f"jcy_{job_id}",
                title=title,
                company=company,
                company_url=company_url,
                company_logo=company_logo,
                description=self._clean_description(description),
                location=location if location else 'Remote',
                job_type=job_type,
                salary=salary,
                tags=tags_str if tags_str else 'remote, jobicy',
                job_url=job_url,
                posted_at=posted_at,
            )
            
        except Exception as e:
            return None
    
    def crawl(self, categories: List[str] = None, max_jobs: int = 200,
              existing_ids: set = None, stop_after_duplicates: int = 10) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        target_categories = categories if categories and categories != ['all'] else ['all']
        
        for category in target_categories:
            if len(all_jobs) >= max_jobs:
                break
            
            if consecutive_duplicates >= stop_after_duplicates:
                break
            
            try:
                jobs_to_fetch = min(100, max_jobs - len(all_jobs))
                print(f"  [Jobicy] Fetching {jobs_to_fetch} jobs from category: {category}")
                
                data = self.fetch_api(
                    category=category if category != 'all' else None,
                    count=jobs_to_fetch
                )
                
                jobs_list = data.get('jobs', [])
                if not jobs_list:
                    print(f"  [Jobicy] No jobs in category: {category}")
                    continue
                
                for job_data in jobs_list:
                    if len(all_jobs) >= max_jobs:
                        break
                    
                    raw_id = str(job_data.get('id', '')) or job_data.get('slug', '')
                    job_id = f"jcy_{raw_id}" if raw_id else ""
                    
                    if not job_id or job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)
                    
                    if job_id in existing_ids:
                        consecutive_duplicates += 1
                        if consecutive_duplicates >= stop_after_duplicates:
                            print(f"  [Jobicy] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    job = self.parse_job(job_data)
                    if job:
                        all_jobs.append(job)
                        
            except Exception as e:
                print(f"  [Jobicy] Error fetching category {category}: {e}")
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
