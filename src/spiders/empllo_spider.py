import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

from ..models.job_listing import JobListing


class EmplloSpider:
    SOURCE = "empllo"
    BASE_URL = "https://empllo.com"
    RSS_URL = "https://empllo.com/feeds/jobs.rss"
    REMOTE_RSS_URL = "https://empllo.com/feeds/jobs.rss?remote=true"
    
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, text/xml, application/xml, text/html, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
    
    def fetch_rss(self, remote_only: bool = True) -> str:
        time.sleep(self.delay)
        url = self.REMOTE_RSS_URL if remote_only else self.RSS_URL
        response = self.session.get(url, timeout=(10, 30))
        response.raise_for_status()
        return response.text
    
    def parse_rss(self, xml_content: str) -> List[Dict[str, Any]]:
        jobs = []
        
        try:
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
                posted_at = self._parse_pub_date(pub_date.get_text(strip=True))
            
            categories = []
            category_elems = item.find_all('category')
            for cat in category_elems:
                cat_text = cat.get_text(strip=True)
                if cat_text:
                    categories.append(cat_text)
            
            company = ""
            location = ""
            salary = ""
            job_type = ""
            
            parsed_title = self._parse_title(title_text)
            if parsed_title.get('company'):
                company = parsed_title['company']
            if parsed_title.get('location'):
                location = parsed_title['location']
            
            if description_text:
                if not location:
                    location = self._extract_location(description_text)
                if not salary:
                    salary = self._extract_salary(description_text)
            
            job_id = self._extract_job_id(guid_text or job_url)
            if not job_id:
                return None
            
            tags_str = ', '.join(categories) if categories else ''
            
            return {
                'title': title_text,
                'company': company,
                'location': location or 'Remote',
                'job_type': job_type,
                'salary': salary,
                'job_url': job_url,
                'job_id': job_id,
                'description': description_text,
                'posted_at': posted_at,
                'tags': tags_str,
                'categories': categories,
            }
            
        except Exception as e:
            return None
    
    def _parse_title(self, title: str) -> Dict[str, Any]:
        result = {
            'company': '',
            'title': title,
            'location': '',
        }
        
        patterns = [
            r'^(.+?)\s+at\s+(.+?)(?:\s*\(([^)]+)\))?$',
            r'^(.+?)\s*:\s*(.+?)(?:\s*\(([^)]+)\))?$',
            r'^(.+?)\s+-\s+(.+?)(?:\s*\(([^)]+)\))?$',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, title)
            if match:
                result['title'] = match.group(1).strip()
                result['company'] = match.group(2).strip()
                if len(match.groups()) > 2 and match.group(3):
                    result['location'] = match.group(3).strip()
                break
        
        if not result['location']:
            location_match = re.search(r'\(([^)]+)\)$', title)
            if location_match:
                result['location'] = location_match.group(1).strip()
        
        return result
    
    def _extract_location(self, description: str) -> str:
        if not description:
            return ""
        
        patterns = [
            r'(?:Location|Place|Country|Region)\s*:\s*([^\n\r]+)',
            r'(?:Remote|Location)\s+in\s+([^\n\r,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                loc = match.group(1).strip()
                if loc:
                    return loc
        
        return ""
    
    def _extract_salary(self, description: str) -> str:
        if not description:
            return ""
        
        patterns = [
            r'(?:Salary|Pay|Compensation)\s*:\s*([^\n\r]+)',
            r'\$(\d+(?:,\d+)?(?:\.\d+)?)\s*[–\-–~]\s*\$(\d+(?:,\d+)?(?:\.\d+)?)',
            r'(\d+(?:,\d+)?)\s*[–\-–~]\s*(\d+(?:,\d+)?)\s*(?:USD|EUR|GBP|K)?\s*/\s*(?:year|yr|month|mo|hour|hr)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:
                    return match.group(1).strip()
                elif len(match.groups()) == 2:
                    return f"${match.group(1)} - ${match.group(2)}"
        
        return ""
    
    def _extract_job_id(self, url_or_guid: str) -> Optional[str]:
        if not url_or_guid:
            return None
        
        patterns = [
            r'/job/([^/\?]+)',
            r'/jobs/([^/\?]+)',
            r'id=([^&\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_guid)
            if match:
                return f"ell_{match.group(1)}"
        
        import hashlib
        return f"ell_{hashlib.md5(url_or_guid.encode()).hexdigest()[:12]}"
    
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
    
    def _parse_pub_date(self, pub_date_str: str) -> Optional[datetime]:
        if not pub_date_str:
            return None
        
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(pub_date_str)
        except Exception:
            try:
                from dateutil import parser
                return parser.parse(pub_date_str, fuzzy=True)
            except Exception:
                return None
    
    def crawl(self, remote_only: bool = True, categories: List[str] = None,
              max_jobs: int = 200, existing_ids: set = None,
              stop_after_duplicates: int = 10) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        print(f"  [Empllo] 开始从 RSS 爬取 {'远程职位' if remote_only else '所有职位'}...")
        
        try:
            xml_content = self.fetch_rss(remote_only=remote_only)
            job_list = self.parse_rss(xml_content)
            
            print(f"  [Empllo] RSS 返回 {len(job_list)} 个职位")
            
            for job_data in job_list:
                if len(all_jobs) >= max_jobs:
                    break
                
                job_id = job_data.get('job_id', '')
                if not job_id or job_id in seen_ids:
                    continue
                seen_ids.add(job_id)
                
                if job_id in existing_ids:
                    consecutive_duplicates += 1
                    if consecutive_duplicates >= stop_after_duplicates:
                        print(f"  [Empllo] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                        return all_jobs
                    continue
                
                consecutive_duplicates = 0
                
                tags = job_data.get('tags', '')
                categories_list = job_data.get('categories', [])
                if not tags and categories_list:
                    tags = ', '.join(categories_list)
                
                job_listing = JobListing(
                    source=self.SOURCE,
                    job_id=job_id,
                    title=job_data.get('title', ''),
                    company=job_data.get('company', ''),
                    description=job_data.get('description', ''),
                    location=job_data.get('location', 'Remote'),
                    job_type=job_data.get('job_type', ''),
                    salary=job_data.get('salary', ''),
                    tags=tags if tags else f'remote, {self.SOURCE}',
                    job_url=job_data.get('job_url', ''),
                    posted_at=job_data.get('posted_at'),
                )
                
                all_jobs.append(job_listing)
                
        except Exception as e:
            print(f"  [Empllo] 爬取出错: {e}")
        
        return all_jobs
    
    def close(self):
        self.session.close()
