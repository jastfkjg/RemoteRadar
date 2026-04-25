import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

from ..models.job_listing import JobListing


class JustRemoteSpider:
    SOURCE = "justremote"
    BASE_URL = "https://justremote.co"
    RSS_URL = "https://justremote.co/rss"
    
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, text/xml, application/xml, text/html, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://justremote.co/",
    }
    
    CATEGORIES = [
        'development', 'design', 'product', 'marketing', 'sales',
        'data', 'devops', 'finance', 'content', 'operations', 'all'
    ]
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
    
    def fetch_rss(self, url: str = None) -> str:
        time.sleep(self.delay)
        target_url = url or self.RSS_URL
        response = self.session.get(target_url, allow_redirects=True, timeout=(10, 30))
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    
    def parse_rss(self, xml_content: str) -> List[Dict[str, Any]]:
        jobs = []
        
        try:
            soup = BeautifulSoup(xml_content, 'xml')
            
            entries = soup.find_all('entry')
            items = soup.find_all('item')
            
            all_items = entries if entries else items
            
            for item in all_items:
                try:
                    job = self._parse_item(item)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    continue
        except Exception as e:
            pass
        
        return jobs
    
    def _parse_item(self, item) -> Optional[Dict[str, Any]]:
        try:
            title = item.find('title')
            title_text = title.get_text(strip=True) if title else ""
            
            link = item.find('link')
            job_url = ""
            if link:
                if link.get('href'):
                    job_url = link.get('href')
                elif link.get_text(strip=True):
                    job_url = link.get_text(strip=True)
            
            id_elem = item.find('id') or item.find('guid')
            id_text = id_elem.get_text(strip=True) if id_elem else job_url
            
            description = item.find('description') or item.find('summary') or item.find('content')
            description_text = ""
            if description:
                desc_html = description.get_text(strip=True)
                description_text = self._clean_description(desc_html)
            
            pub_date = item.find('pubDate') or item.find('published') or item.find('updated')
            posted_at = None
            if pub_date:
                posted_at = self._parse_date(pub_date.get_text(strip=True))
            
            categories = []
            category_elems = item.find_all('category')
            for cat in category_elems:
                cat_text = cat.get_text(strip=True)
                if cat_text:
                    categories.append(cat_text)
            
            company = ""
            location = ""
            salary = ""
            
            if title_text:
                company_match = re.search(r'(?:at|@|with)\s+([^,\n|]+?)(?:,|\n|\||$)', title_text, re.IGNORECASE)
                if company_match:
                    company = company_match.group(1).strip()
            
            if description_text:
                location_match = re.search(r'(?:Location|地点|位置|Remote)\s*[:：\s]+([^\n\r，。,，]+)', description_text, re.IGNORECASE)
                if location_match:
                    location = location_match.group(1).strip()
                
                salary_match = re.search(r'(?:Salary|薪资|Pay|Compensation)\s*[:：\s]+([^\n\r，。,，]+)', description_text, re.IGNORECASE)
                if salary_match:
                    salary = salary_match.group(1).strip()
            
            job_id = self._extract_job_id(job_url or id_text)
            if not job_id:
                return None
            
            tags_str = ', '.join(categories) if categories else ''
            
            return {
                'title': title_text,
                'company': company,
                'location': location or 'Remote',
                'salary': salary,
                'job_url': job_url,
                'job_id': job_id,
                'description': description_text,
                'posted_at': posted_at,
                'tags': tags_str,
            }
            
        except Exception as e:
            return None
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        if not url:
            return None
        
        patterns = [
            r'/remote-jobs/([^/\?]+)',
            r'/job/([^/\?]+)',
            r'/jobs/([^/\?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f"jrm_{match.group(1)}"
        
        if url:
            import hashlib
            return f"jrm_{hashlib.md5(url.encode()).hexdigest()[:12]}"
        
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
    
    def crawl(self, categories: List[str] = None, max_jobs: int = 100,
              existing_ids: set = None, stop_after_duplicates: int = 5) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        urls_to_try = [
            self.RSS_URL,
        ]
        
        if categories and categories != ['all']:
            for cat in categories:
                urls_to_try.append(f"{self.BASE_URL}/remote-jobs/{cat}/rss")
        
        for url in urls_to_try:
            if len(all_jobs) >= max_jobs:
                break
            
            try:
                xml_content = self.fetch_rss(url)
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
                            print(f"  [JustRemote] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    tags = job_data.get('tags', '')
                    
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
                        tags=tags if tags else 'remote, justremote',
                    )
                    
                    all_jobs.append(job_listing)
                    
            except Exception as e:
                continue
        
        return all_jobs
    
    def close(self):
        self.session.close()
