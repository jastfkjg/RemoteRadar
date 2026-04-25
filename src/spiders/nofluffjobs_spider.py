import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

from ..models.job_listing import JobListing


class NoFluffJobsSpider:
    SOURCE = "nofluffjobs"
    BASE_URL = "https://nofluffjobs.com"
    JOBS_URL = "https://nofluffjobs.com/remote"
    
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://nofluffjobs.com/",
    }
    
    CATEGORIES = [
        'frontend', 'backend', 'fullstack', 'mobile', 'devops',
        'data', 'testing', 'design', 'product', 'all'
    ]
    
    def __init__(self, delay: float = 1.5):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
    
    def fetch_page(self, url: str) -> str:
        time.sleep(self.delay)
        response = self.session.get(url, allow_redirects=True)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    
    def parse_jobs_page(self, html: str) -> List[Dict[str, Any]]:
        jobs = []
        soup = BeautifulSoup(html, 'lxml')
        
        script_data = self._parse_script_data(soup)
        if script_data:
            return script_data
        
        job_selectors = [
            '[data-cy="job-offer"]',
            '.job-offer',
            '.list-item',
            '[data-testid="job-card"]',
            'a[href*="/job/"]',
            'a[href*="/pl/job/"]',
            '.nfj-list-item',
        ]
        
        seen_links = set()
        
        for selector in job_selectors:
            items = soup.select(selector)
            for item in items:
                try:
                    link = item.get('href', '')
                    if not link:
                        a_tag = item.select_one('a[href*="/job/"]')
                        link = a_tag.get('href', '') if a_tag else ''
                    
                    if link and 'nofluffjobs.com' not in link:
                        if link.startswith('/'):
                            link = self.BASE_URL + link
                    
                    if not link or link in seen_links:
                        continue
                    seen_links.add(link)
                    
                    job_id = self._extract_job_id(link)
                    if not job_id:
                        continue
                    
                    title = ""
                    title_elem = item.select_one('h3, h4, .title, [data-cy="job-title"], [class*="title"]')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    
                    if not title:
                        title = item.get_text(strip=True)[:100]
                    
                    company = ""
                    company_elem = item.select_one('.company, .employer, [data-cy="company-name"], [class*="company"]')
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                    
                    location = ""
                    location_elem = item.select_one('.location, [data-cy="location"], [class*="location"]')
                    if location_elem:
                        location = location_elem.get_text(strip=True)
                    
                    salary = ""
                    salary_elem = item.select_one('.salary, [data-cy="salary"], [class*="salary"], [class*="price"]')
                    if salary_elem:
                        salary = salary_elem.get_text(strip=True)
                    
                    tags = []
                    tag_elems = item.select('.tag, .badge, .skill, [data-cy="tag"], [class*="tag"], [class*="skill"]')
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
        
        return jobs
    
    def _parse_script_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        jobs = []
        seen_ids = set()
        
        script_selectors = [
            'script[type="application/ld+json"]',
            'script[id*="NEXT_DATA"]',
            'script[data-state]',
        ]
        
        for selector in script_selectors:
            scripts = soup.select(selector)
            for script in scripts:
                try:
                    import json
                    text = script.get_text()
                    if not text:
                        continue
                    
                    data = json.loads(text)
                    
                    if isinstance(data, dict):
                        if data.get('@type') == 'JobPosting':
                            job_url = data.get('url', '')
                            job_id = self._extract_job_id(job_url)
                            if job_id and job_id not in seen_ids:
                                seen_ids.add(job_id)
                                jobs.append({
                                    'title': data.get('title', ''),
                                    'company': data.get('hiringOrganization', {}).get('name', ''),
                                    'location': data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'Remote'),
                                    'salary': str(data.get('baseSalary', {}).get('value', '')) if data.get('baseSalary') else '',
                                    'job_url': job_url,
                                    'job_id': job_id,
                                    'tags': [],
                                })
                        
                        else:
                            def find_jobs(obj):
                                if isinstance(obj, dict):
                                    if obj.get('@type') == 'JobPosting':
                                        job_url = obj.get('url', '')
                                        job_id = self._extract_job_id(job_url)
                                        if job_id and job_id not in seen_ids:
                                            seen_ids.add(job_id)
                                            jobs.append({
                                                'title': obj.get('title', ''),
                                                'company': obj.get('hiringOrganization', {}).get('name', ''),
                                                'location': obj.get('jobLocation', {}).get('address', {}).get('addressLocality', 'Remote'),
                                                'salary': str(obj.get('baseSalary', {}).get('value', '')) if obj.get('baseSalary') else '',
                                                'job_url': job_url,
                                                'job_id': job_id,
                                                'tags': [],
                                            })
                                    for key in obj:
                                        find_jobs(obj[key])
                                elif isinstance(obj, list):
                                    for item in obj:
                                        find_jobs(item)
                            
                            find_jobs(data)
                            
                except Exception:
                    continue
        
        return jobs
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        patterns = [
            r'/job/([^/\?]+)',
            r'/pl/job/([^/\?]+)',
            r'offerCode=([^&\?]+)',
            r'id=(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f"nfj_{match.group(1)}"
        return None
    
    def crawl(self, categories: List[str] = None, max_jobs: int = 100) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        
        urls_to_try = [
            self.JOBS_URL,
            f"{self.BASE_URL}/remote/backend",
            f"{self.BASE_URL}/remote/frontend",
            f"{self.BASE_URL}/remote/fullstack",
            f"{self.BASE_URL}/remote/mobile",
            f"{self.BASE_URL}/remote/devops",
        ]
        
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
                    
                    tags = job_data.get('tags', [])
                    tags_str = ', '.join(tags) if tags else ''
                    
                    job_listing = JobListing(
                        source=self.SOURCE,
                        job_id=job_id,
                        title=job_data.get('title', ''),
                        company=job_data.get('company', ''),
                        description="",
                        location=job_data.get('location', 'Remote'),
                        salary=job_data.get('salary', ''),
                        job_url=job_data.get('job_url', ''),
                        tags=tags_str if tags_str else 'remote, nofluffjobs',
                    )
                    
                    all_jobs.append(job_listing)
                    
            except Exception as e:
                continue
        
        return all_jobs
    
    def close(self):
        self.session.close()
