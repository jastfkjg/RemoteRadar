import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

from ..models.job_listing import JobListing


class WorkingNomadsSpider:
    SOURCE = "workingnomads"
    BASE_URL = "https://www.workingnomads.com"
    JOBS_URL = "https://www.workingnomads.com/jobs"
    RSS_URL = "https://www.workingnomads.com/jobs/feed"
    
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.workingnomads.com/",
    }
    
    CATEGORIES = [
        'development', 'design', 'marketing', 'sales', 'data',
        'devops', 'product', 'management', 'all'
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
    
    def parse_rss(self, xml_content: str) -> List[Dict[str, Any]]:
        jobs = []
        soup = BeautifulSoup(xml_content, 'xml')
        
        items = soup.find_all('item')
        for item in items:
            try:
                title = item.find('title')
                title_text = title.get_text(strip=True) if title else ""
                
                link = item.find('link')
                job_url = link.get_text(strip=True) if link else ""
                
                description = item.find('description')
                description_text = ""
                if description:
                    desc_html = description.get_text(strip=True)
                    description_text = self._clean_description(desc_html)
                
                pub_date = item.find('pubDate')
                posted_at = None
                if pub_date:
                    posted_at = self._parse_date(pub_date.get_text(strip=True))
                
                category = item.find('category')
                category_text = category.get_text(strip=True) if category else ""
                
                guid = item.find('guid')
                guid_text = guid.get_text(strip=True) if guid else ""
                
                job_id = self._extract_job_id(job_url or guid_text)
                if not job_id:
                    continue
                
                company = ""
                location = ""
                salary = ""
                
                if description_text:
                    company_match = re.search(r'(?:Company|公司|At)\s*[:：\s]+([^\n\r，。,，]+)', description_text, re.IGNORECASE)
                    if company_match:
                        company = company_match.group(1).strip()
                    
                    location_match = re.search(r'(?:Location|地点|位置|Remote)\s*[:：\s]+([^\n\r，。,，]+)', description_text, re.IGNORECASE)
                    if location_match:
                        location = location_match.group(1).strip()
                    
                    salary_match = re.search(r'(?:Salary|薪资|Pay|Compensation)\s*[:：\s]+([^\n\r，。,，]+)', description_text, re.IGNORECASE)
                    if salary_match:
                        salary = salary_match.group(1).strip()
                
                tags = []
                if category_text:
                    tags.append(category_text)
                
                if title_text:
                    jobs.append({
                        'title': title_text,
                        'company': company,
                        'location': location or 'Remote',
                        'salary': salary,
                        'job_url': job_url,
                        'job_id': job_id,
                        'description': description_text,
                        'posted_at': posted_at,
                        'tags': tags,
                    })
                    
            except Exception as e:
                continue
        
        return jobs
    
    def parse_jobs_page(self, html: str) -> List[Dict[str, Any]]:
        jobs = []
        soup = BeautifulSoup(html, 'lxml')
        
        job_selectors = [
            '.job',
            '.job-listing',
            '[data-job-id]',
            'a[href*="/jobs/"]',
            'tr[class*="job"]',
            '.views-row',
        ]
        
        seen_links = set()
        
        for selector in job_selectors:
            items = soup.select(selector)
            for item in items:
                try:
                    link = item.get('href', '')
                    if not link:
                        a_tag = item.select_one('a[href*="/jobs/"]')
                        link = a_tag.get('href', '') if a_tag else ''
                    
                    if link and 'workingnomads.com' not in link:
                        if link.startswith('/'):
                            link = self.BASE_URL + link
                    
                    if not link or link in seen_links:
                        continue
                    seen_links.add(link)
                    
                    job_id = self._extract_job_id(link)
                    if not job_id:
                        continue
                    
                    title = ""
                    title_elem = item.select_one('h2, h3, h4, .title, [class*="title"]')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    
                    if not title:
                        title = item.get_text(strip=True)[:100]
                    
                    company = ""
                    company_elem = item.select_one('.company, .employer, [class*="company"]')
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                    
                    location = ""
                    location_elem = item.select_one('.location, [class*="location"]')
                    if location_elem:
                        location = location_elem.get_text(strip=True)
                    
                    if title:
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': location or 'Remote',
                            'salary': '',
                            'job_url': link,
                            'job_id': job_id,
                            'tags': [],
                        })
                        
                except Exception as e:
                    continue
            
            if len(jobs) >= 50:
                break
        
        return jobs
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        patterns = [
            r'/jobs/(\d+)',
            r'/jobs/([^/\?]+)',
            r'id=(\d+)',
            r'/job/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f"wn_{match.group(1)}"
        return None
    
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
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            try:
                from dateutil import parser
                return parser.parse(date_str, fuzzy=True)
            except Exception:
                return None
    
    def crawl(self, categories: List[str] = None, max_jobs: int = 100, use_rss: bool = True,
              existing_ids: set = None, stop_after_duplicates: int = 5) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        if use_rss:
            try:
                xml_content = self.fetch_page(self.RSS_URL)
                jobs = self.parse_rss(xml_content)
                
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
                            print(f"  [WorkingNomads] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    tags = job_data.get('tags', [])
                    tags_str = ', '.join(tags) if tags else ''
                    
                    job_listing = JobListing(
                        source=self.SOURCE,
                        job_id=job_id,
                        title=job_data.get('title', ''),
                        company=job_data.get('company', ''),
                        description=job_data.get('description', ''),
                        location=job_data.get('location', 'Remote'),
                        salary=job_data.get('salary', ''),
                        job_url=job_data.get('job_url', ''),
                        posted_at=job_data.get('posted_at'),
                        tags=tags_str if tags_str else 'remote, workingnomads',
                    )
                    
                    all_jobs.append(job_listing)
                    
            except Exception as e:
                pass
        
        if len(all_jobs) < max_jobs:
            try:
                html = self.fetch_page(self.JOBS_URL)
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
                            print(f"  [WorkingNomads] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    tags = job_data.get('tags', [])
                    tags_str = ', '.join(tags) if tags else ''
                    
                    job_listing = JobListing(
                        source=self.SOURCE,
                        job_id=job_id,
                        title=job_data.get('title', ''),
                        company=job_data.get('company', ''),
                        description=job_data.get('description', ''),
                        location=job_data.get('location', 'Remote'),
                        salary=job_data.get('salary', ''),
                        job_url=job_data.get('job_url', ''),
                        tags=tags_str if tags_str else 'remote, workingnomads',
                    )
                    
                    all_jobs.append(job_listing)
                    
            except Exception as e:
                pass
        
        return all_jobs
    
    def close(self):
        self.session.close()
