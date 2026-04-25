import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests

from ..models.job_listing import JobListing


class StackOverflowSpider:
    SOURCE = "stackoverflow"
    BASE_URL = "https://stackoverflow.com"
    RSS_URL = "https://stackoverflow.com/jobs/feed"
    
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, text/xml, application/xml, text/plain",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    CATEGORIES = [
        'c', 'java', 'javascript', 'python', 'c++', 'php', 'android',
        'jquery', 'html', 'css', 'ios', 'mysql', 'sql', 'asp.net',
        'ruby-on-rails', 'objective-c', 'c#', '.net', 'angularjs',
        'node.js', 'json', 'ajax', 'django', 'ruby', 'reactjs',
        'swift', 'go', 'scala', 'kotlin', 'rust', 'typescript',
        'machine-learning', 'data-science', 'devops', 'docker',
        'kubernetes', 'amazon-web-services', 'azure', 'google-cloud'
    ]
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
    
    def fetch_rss(self, category: str = None, search: str = None) -> str:
        time.sleep(self.delay)
        
        params = {}
        if category and category != 'all':
            params['tl'] = category
        if search:
            params['q'] = search
        
        response = self.session.get(self.RSS_URL, params=params, timeout=(10, 30))
        response.raise_for_status()
        return response.text
    
    def parse_rss(self, xml_content: str) -> List[JobListing]:
        jobs = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(xml_content, 'xml')
            
            items = soup.find_all('item')
            for item in items:
                try:
                    job = self._parse_item(item)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    continue
        except Exception as e:
            pass
        
        return jobs
    
    def _parse_item(self, item) -> Optional[JobListing]:
        try:
            from bs4 import BeautifulSoup
            
            title = item.find('title')
            title_text = title.get_text(strip=True) if title else ""
            
            link = item.find('link')
            job_url = link.get_text(strip=True) if link else ""
            
            guid = item.find('guid')
            guid_text = guid.get_text(strip=True) if guid else job_url
            
            description = item.find('description')
            description_text = ""
            if description:
                desc_html = description.get_text(strip=True)
                description_text = self._clean_description(desc_html)
            
            pub_date = item.find('pubDate')
            posted_at = None
            if pub_date:
                posted_at = self._parse_date(pub_date.get_text(strip=True))
            
            category_elements = item.find_all('category')
            categories = [cat.get_text(strip=True) for cat in category_elements]
            tags_str = ', '.join(categories) if categories else ''
            
            company = ""
            location = ""
            salary = ""
            
            if title_text:
                company_match = re.search(r'at\s+([^,\n]+?)(?:,|\n|$)', title_text, re.IGNORECASE)
                if company_match:
                    company = company_match.group(1).strip()
            
            if description_text:
                location_match = re.search(r'(?:location|地点|远程|位置)[:：\s]+([^\n，。,，]+)', description_text, re.IGNORECASE)
                if location_match:
                    location = location_match.group(1).strip()
                
                salary_match = re.search(r'(?:salary|薪资|待遇|薪水)[:：\s]+([^\n，。,，]+)', description_text, re.IGNORECASE)
                if salary_match:
                    salary = salary_match.group(1).strip()
            
            job_id = self._extract_job_id(job_url or guid_text)
            if not job_id:
                return None
            
            return JobListing(
                source=self.SOURCE,
                job_id=job_id,
                title=title_text,
                company=company,
                description=description_text,
                location=location,
                salary=salary,
                job_url=job_url,
                posted_at=posted_at,
                tags=tags_str if tags_str else 'remote, stackoverflow',
            )
            
        except Exception as e:
            return None
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        match = re.search(r'/jobs/(\d+)', url)
        if match:
            return f"so_{match.group(1)}"
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
    
    def crawl(self, categories: List[str] = None, search: str = None, max_jobs: int = 100,
              existing_ids: set = None, stop_after_duplicates: int = 5) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        target_categories = categories if categories and categories != ['all'] else ['all']
        
        for category in target_categories:
            if len(all_jobs) >= max_jobs:
                break
            
            try:
                xml_content = self.fetch_rss(
                    category=category if category != 'all' else None,
                    search=search
                )
                
                jobs = self.parse_rss(xml_content)
                
                for job in jobs:
                    if len(all_jobs) >= max_jobs:
                        break
                    
                    if job.job_id in seen_ids:
                        continue
                    seen_ids.add(job.job_id)
                    
                    if job.job_id in existing_ids:
                        consecutive_duplicates += 1
                        if consecutive_duplicates >= stop_after_duplicates:
                            print(f"  [StackOverflow] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    all_jobs.append(job)
                    
            except Exception as e:
                continue
        
        return all_jobs
    
    def close(self):
        self.session.close()
