import re
import time
from datetime import datetime
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

from ..models.job_listing import JobListing


class WeworkSpider:
    SOURCE = "weworkremotely"
    BASE_URL = "https://weworkremotely.com"
    RSS_URL = "https://weworkremotely.com/remote-jobs.rss"
    CATEGORIES = {
        "programming": "https://weworkremotely.com/categories/remote-programming-jobs",
        "design": "https://weworkremotely.com/categories/remote-design-jobs",
        "devops": "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs",
        "customer-support": "https://weworkremotely.com/categories/remote-customer-support-jobs",
        "sales": "https://weworkremotely.com/categories/remote-sales-and-marketing-jobs",
    }
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.REQUEST_HEADERS)
    
    def fetch_page(self, url: str) -> str:
        time.sleep(self.delay)
        response = self.session.get(url, timeout=(10, 30))
        response.raise_for_status()
        return response.text
    
    def fetch_rss(self) -> str:
        return self.fetch_page(self.RSS_URL)
    
    def parse_rss(self, xml_content: str) -> List[dict]:
        jobs = []
        soup = BeautifulSoup(xml_content, 'xml')
        
        items = soup.find_all('item')
        for item in items:
            try:
                title = item.find('title')
                title_text = title.get_text(strip=True) if title else ""
                
                link = item.find('link')
                job_url = link.get_text(strip=True) if link else ""
                
                guid = item.find('guid')
                job_id = ""
                if guid:
                    guid_text = guid.get_text(strip=True)
                    job_id = self._extract_job_id(guid_text)
                
                description = item.find('description')
                description_text = ""
                if description:
                    desc_html = description.get_text(strip=True)
                    description_text = self._clean_description(desc_html)
                
                pub_date = item.find('pubDate')
                posted_at = None
                if pub_date:
                    posted_at = self._parse_pub_date(pub_date.get_text(strip=True))
                
                category = item.find('category')
                category_text = category.get_text(strip=True) if category else ""
                
                job_data = {
                    'title': title_text,
                    'job_url': job_url,
                    'job_id': job_id,
                    'description': description_text,
                    'posted_at': posted_at,
                    'category': category_text,
                }
                
                title_parsed = self._parse_title(title_text)
                job_data.update(title_parsed)
                
                jobs.append(job_data)
            except Exception as e:
                continue
        
        return jobs
    
    def parse_job_page(self, url: str) -> dict:
        result = {
            'company': '',
            'company_url': '',
            'company_logo': '',
            'location': '',
            'salary': '',
            'description': '',
        }
        
        try:
            html = self.fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')
            
            company_name = soup.select_one('.company-name')
            if company_name:
                result['company'] = company_name.get_text(strip=True)
            
            company_link = soup.select_one('.company-name a')
            if company_link:
                result['company_url'] = company_link.get('href', '')
            
            company_logo = soup.select_one('.listing-logo img')
            if company_logo:
                logo_url = company_logo.get('src', '')
                if logo_url.startswith('//'):
                    logo_url = 'https:' + logo_url
                result['company_logo'] = logo_url
            
            location = soup.select_one('.location-name')
            if location:
                result['location'] = location.get_text(strip=True)
            
            job_description = soup.select_one('.listing-container .content')
            if job_description:
                for br in job_description.find_all('br'):
                    br.replace_with('\n')
                result['description'] = job_description.get_text('\n', strip=True)
            
            tags = soup.select('.listing-header .listing-tag a')
            if tags:
                result['tags'] = ', '.join([tag.get_text(strip=True) for tag in tags])
            
        except Exception as e:
            pass
        
        return result
    
    def crawl(self, use_rss: bool = True, fetch_details: bool = False, 
              categories: List[str] = None, existing_ids: set = None, 
              stop_after_duplicates: int = 5) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        if use_rss:
            try:
                xml_content = self.fetch_rss()
                job_list = self.parse_rss(xml_content)
                
                for job_data in job_list:
                    job_id = job_data.get('job_id', '')
                    if not job_id or job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)
                    
                    if job_id in existing_ids:
                        consecutive_duplicates += 1
                        if consecutive_duplicates >= stop_after_duplicates:
                            print(f"  [Wework] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    company = job_data.get('company', '')
                    description = job_data.get('description', '')
                    
                    if fetch_details and job_data.get('job_url'):
                        details = self.parse_job_page(job_data['job_url'])
                        if not company:
                            company = details.get('company', '')
                        if not description:
                            description = details.get('description', '')
                        if not job_data.get('location'):
                            job_data['location'] = details.get('location', '')
                        if not job_data.get('tags'):
                            job_data['tags'] = details.get('tags', '')
                    
                    job_listing = JobListing(
                        source=self.SOURCE,
                        job_id=job_id,
                        title=job_data.get('title', ''),
                        company=company,
                        company_url=job_data.get('company_url', ''),
                        company_logo=job_data.get('company_logo', ''),
                        description=description,
                        location=job_data.get('location', ''),
                        job_type=job_data.get('category', ''),
                        salary=job_data.get('salary', ''),
                        tags=job_data.get('tags', f'remote, {self.SOURCE}'),
                        job_url=job_data.get('job_url', ''),
                        posted_at=job_data.get('posted_at'),
                    )
                    
                    all_jobs.append(job_listing)
                    
            except Exception as e:
                pass
        
        if categories:
            for category in categories:
                if category in self.CATEGORIES:
                    try:
                        url = self.CATEGORIES[category]
                        html = self.fetch_page(url)
                        jobs_from_category = self._parse_category_page(html)
                        
                        for job_data in jobs_from_category:
                            job_id = job_data.get('job_id', '')
                            if not job_id or job_id in seen_ids:
                                continue
                            seen_ids.add(job_id)
                            
                            if job_id in existing_ids:
                                consecutive_duplicates += 1
                                if consecutive_duplicates >= stop_after_duplicates:
                                    print(f"  [Wework] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                                    return all_jobs
                                continue
                            
                            consecutive_duplicates = 0
                            job_data['category'] = category
                            
                            company = job_data.get('company', '')
                            description = job_data.get('description', '')
                            
                            if fetch_details and job_data.get('job_url'):
                                details = self.parse_job_page(job_data['job_url'])
                                if not company:
                                    company = details.get('company', '')
                                if not description:
                                    description = details.get('description', '')
                            
                            job_listing = JobListing(
                                source=self.SOURCE,
                                job_id=job_id,
                                title=job_data.get('title', ''),
                                company=company,
                                description=description,
                                location=job_data.get('location', ''),
                                job_type=category,
                                tags=f'remote, {self.SOURCE}, {category}',
                                job_url=job_data.get('job_url', ''),
                                posted_at=job_data.get('posted_at'),
                            )
                            
                            all_jobs.append(job_listing)
                            
                    except Exception as e:
                        continue
        
        return all_jobs
    
    def _parse_category_page(self, html: str) -> List[dict]:
        jobs = []
        soup = BeautifulSoup(html, 'lxml')
        
        items = soup.select('.jobs li')
        for item in items:
            try:
                link = item.select_one('a')
                if not link:
                    continue
                
                href = link.get('href', '')
                if href.startswith('/'):
                    href = self.BASE_URL + href
                elif not href.startswith('http'):
                    continue
                
                job_id = self._extract_job_id(href)
                if not job_id:
                    continue
                
                title_elem = item.select_one('.title')
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                company_elem = item.select_one('.company')
                company = company_elem.get_text(strip=True) if company_elem else ""
                
                location_elem = item.select_one('.region')
                location = location_elem.get_text(strip=True) if location_elem else ""
                
                time_elem = item.select_one('.date')
                posted_at = None
                if time_elem:
                    posted_at = self._parse_relative_time(time_elem.get_text(strip=True))
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'job_url': href,
                    'job_id': job_id,
                    'posted_at': posted_at,
                })
            except Exception as e:
                continue
        
        return jobs
    
    def _parse_title(self, title: str) -> dict:
        result = {
            'company': '',
            'title': title,
            'location': '',
        }
        
        match = re.match(r'^(.+?)\s*:\s*(.+?)\s*$', title)
        if match:
            result['company'] = match.group(1).strip()
            result['title'] = match.group(2).strip()
        
        location_match = re.search(r'\(([^)]+)\)$', title)
        if location_match:
            result['location'] = location_match.group(1).strip()
        
        return result
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        match = re.search(r'/remote-jobs/(\d+)', url)
        if match:
            return f"wwr_{match.group(1)}"
        return None
    
    def _clean_description(self, html_text: str) -> str:
        if not html_text:
            return ""
        
        soup = BeautifulSoup(html_text, 'lxml')
        for br in soup.find_all('br'):
            br.replace_with('\n')
        return soup.get_text('\n', strip=True)
    
    def _parse_pub_date(self, pub_date_str: str) -> Optional[datetime]:
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(pub_date_str)
        except Exception:
            try:
                from dateutil import parser
                return parser.parse(pub_date_str, fuzzy=True)
            except Exception:
                return None
    
    def _parse_relative_time(self, time_str: str) -> Optional[datetime]:
        from datetime import timedelta
        
        if not time_str:
            return None
        
        now = datetime.now()
        
        patterns = [
            (r'(\d+)\s*d', timedelta(days=1)),
            (r'(\d+)\s*h', timedelta(hours=1)),
            (r'(\d+)\s*m', timedelta(minutes=1)),
            (r'yesterday', timedelta(days=1)),
            (r'today', timedelta(days=0)),
        ]
        
        for pattern, delta in patterns:
            match = re.search(pattern, time_str, re.IGNORECASE)
            if match:
                if match.groups():
                    count = int(match.group(1))
                    if 'd' in pattern:
                        return now - timedelta(days=count)
                    elif 'h' in pattern:
                        return now - timedelta(hours=count)
                    elif 'm' in pattern:
                        return now - timedelta(minutes=count)
                else:
                    return now - delta
        
        return None
    
    def close(self):
        self.session.close()
