import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

from ..models.job_listing import JobListing


class WellfoundSpider:
    SOURCE = "wellfound"
    BASE_URL = "https://wellfound.com"
    API_URL = "https://wellfound.com/startups_jobs"
    JOBS_URL = "https://wellfound.com/roles/remote"
    
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://wellfound.com/",
    }
    
    CATEGORIES = [
        'software-engineering', 'data-science', 'design', 'product',
        'marketing', 'sales', 'finance', 'operations', 'all'
    ]
    
    def __init__(self, delay: float = 1.5):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
    
    def fetch_page(self, url: str) -> str:
        time.sleep(self.delay)
        response = self.session.get(url, allow_redirects=True, timeout=(10, 30))
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    
    def parse_jobs_page(self, html: str) -> List[Dict[str, Any]]:
        jobs = []
        soup = BeautifulSoup(html, 'lxml')
        
        job_selectors = [
            '[data-test="job-card"]',
            '.job-card',
            '.styled__JobCardWrapper',
            '.styles__JobCard',
            'a[href*="/jobs/"]',
            '[data-job-id]',
            '.flex.flex-col',
        ]
        
        seen_links = set()
        
        for selector in job_selectors:
            items = soup.select(selector)
            for item in items:
                try:
                    link = item.get('href', '')
                    if not link:
                        a_tag = item.select_one('a[href*="/jobs/"], a[href*="/role/"]')
                        link = a_tag.get('href', '') if a_tag else ''
                    
                    if link and 'wellfound.com' not in link:
                        link = self.BASE_URL + link
                    
                    if not link or link in seen_links:
                        continue
                    seen_links.add(link)
                    
                    job_id = self._extract_job_id(link)
                    if not job_id:
                        continue
                    
                    title = ""
                    title_elem = item.select_one('h3, h4, .text-lg, .font-semibold, [data-test="job-title"]')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    
                    if not title:
                        title = item.get_text(strip=True)[:100]
                    
                    company = ""
                    company_elem = item.select_one('.text-sm, [data-test="company-name"], .font-medium, a[href*="/companies/"]')
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                    
                    location = ""
                    location_elem = item.select_one('.text-gray-500, .location, [data-test="location"]')
                    if location_elem:
                        location = location_elem.get_text(strip=True)
                    
                    salary = ""
                    salary_elem = item.select_one('.text-green-600, .salary, [data-test="salary"]')
                    if salary_elem:
                        salary = salary_elem.get_text(strip=True)
                    
                    tags = []
                    tag_elems = item.select('.tag, .badge, [data-test="tag"], .px-2.py-1')
                    for tag in tag_elems:
                        tag_text = tag.get_text(strip=True)
                        if tag_text and len(tag_text) < 30:
                            tags.append(tag_text)
                    
                    if title:
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': location or 'Remote',
                            'salary': salary,
                            'job_url': link,
                            'job_id': job_id,
                            'tags': tags,
                        })
                        
                except Exception as e:
                    continue
            
            if len(jobs) >= 50:
                break
        
        script_selector = soup.select('script[type="application/ld+json"]')
        for script in script_selector:
            try:
                import json
                data = json.loads(script.get_text())
                if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                    job_url = data.get('url', '')
                    job_id = self._extract_job_id(job_url)
                    if job_id and job_id not in seen_links:
                        jobs.append({
                            'title': data.get('title', ''),
                            'company': data.get('hiringOrganization', {}).get('name', ''),
                            'location': data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'Remote'),
                            'salary': str(data.get('baseSalary', {}).get('value', '')) if data.get('baseSalary') else '',
                            'job_url': job_url,
                            'job_id': job_id,
                            'tags': [],
                        })
            except Exception:
                continue
        
        return jobs
    
    def parse_job_detail(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            html = self.fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')
            
            description = ""
            desc_selectors = [
                '[data-test="job-description"]',
                '.job-description',
                '.description',
                '#job-description',
                '.styles__Description',
                'article',
                'main',
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    for br in desc_elem.find_all('br'):
                        br.replace_with('\n')
                    description = desc_elem.get_text('\n', strip=True)
                    if description and len(description) > 100:
                        break
            
            script_selector = soup.select_one('script[type="application/ld+json"]')
            if script_selector:
                try:
                    import json
                    data = json.loads(script_selector.get_text())
                    if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                        if not description:
                            description = data.get('description', '')
                except Exception:
                    pass
            
            return {
                'description': description,
            }
            
        except Exception as e:
            return None
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        patterns = [
            r'/jobs/(\d+)',
            r'/roles/([^/]+)',
            r'/role/([^/]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f"wf_{match.group(1)}"
        return None
    
    def crawl(self, categories: List[str] = None, max_jobs: int = 100, fetch_details: bool = False,
              existing_ids: set = None, stop_after_duplicates: int = 5) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        urls_to_try = [
            self.JOBS_URL,
            f"{self.BASE_URL}/jobs",
            f"{self.BASE_URL}/remote-jobs",
            f"{self.BASE_URL}/roles/software-engineer",
            f"{self.BASE_URL}/roles/data-scientist",
            f"{self.BASE_URL}/roles/product-manager",
        ]
        
        if categories and categories != ['all']:
            for cat in categories:
                urls_to_try.append(f"{self.BASE_URL}/roles/{cat}")
        
        for url in urls_to_try:
            if len(all_jobs) >= max_jobs:
                break
            
            try:
                html = self.fetch_page(url)
                jobs = self.parse_jobs_page(html)
                
                for job_data in jobs:
                    if len(all_jobs) >= max_jobs:
                        break
                    
                    job_id = job_data.get('job_id', '')
                    if not job_id or job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)
                    
                    if job_id in existing_ids:
                        consecutive_duplicates += 1
                        if consecutive_duplicates >= stop_after_duplicates:
                            print(f"  [Wellfound] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    description = ""
                    if fetch_details and job_data.get('job_url'):
                        detail = self.parse_job_detail(job_data['job_url'])
                        if detail:
                            description = detail.get('description', '')
                    
                    tags = job_data.get('tags', [])
                    tags_str = ', '.join(tags) if tags else ''
                    
                    job_listing = JobListing(
                        source=self.SOURCE,
                        job_id=job_id,
                        title=job_data.get('title', ''),
                        company=job_data.get('company', ''),
                        description=description,
                        location=job_data.get('location', 'Remote'),
                        salary=job_data.get('salary', ''),
                        job_url=job_data.get('job_url', ''),
                        tags=tags_str if tags_str else 'remote, wellfound',
                    )
                    
                    all_jobs.append(job_listing)
                    
            except Exception as e:
                continue
        
        return all_jobs
    
    def close(self):
        self.session.close()
