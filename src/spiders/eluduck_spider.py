import re
import time
from datetime import datetime
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

from ..models.job_listing import JobListing


class EluduckSpider:
    SOURCE = "eleduck"
    BASE_URL = "https://eleduck.com"
    RSS_URL = "https://eleduck.com/feed/rss"
    POSTS_URL = "https://eleduck.com/categories/3"
    
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
        response.encoding = 'utf-8'
        return response.text
    
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
                
                guid = item.find('guid')
                guid_text = guid.get_text(strip=True) if guid else ""
                post_id = self._extract_post_id(job_url or guid_text)
                
                job_data = {
                    'title': title_text,
                    'job_url': job_url,
                    'job_id': post_id,
                    'description': description_text,
                    'posted_at': posted_at,
                    'category': category_text,
                }
                
                parsed = self._parse_title(title_text)
                job_data.update(parsed)
                
                jobs.append(job_data)
            except Exception as e:
                continue
        
        return jobs
    
    def parse_posts_page(self, html: str) -> List[dict]:
        jobs = []
        soup = BeautifulSoup(html, 'lxml')
        
        items = soup.select('.topic-list-item, .topic, .post-item, [data-topic-id]')
        
        for item in items:
            try:
                title_link = item.select_one('a[href*="/posts/"], a[href*="/topics/"], .title a')
                if not title_link:
                    continue
                
                title = title_link.get_text(strip=True)
                href = title_link.get('href', '')
                if not href.startswith('http'):
                    href = self.BASE_URL + href
                
                post_id = self._extract_post_id(href)
                if not post_id:
                    continue
                
                meta = item.select_one('.meta, .post-meta, .small, .fade')
                meta_text = meta.get_text(strip=True) if meta else ""
                posted_at = self._parse_time(meta_text)
                
                job_data = {
                    'title': title,
                    'job_url': href,
                    'job_id': post_id,
                    'posted_at': posted_at,
                }
                
                parsed = self._parse_title(title)
                job_data.update(parsed)
                
                jobs.append(job_data)
            except Exception as e:
                continue
        
        return jobs
    
    def fetch_post_detail(self, url: str) -> Optional[dict]:
        try:
            html = self.fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')
            
            content_selectors = [
                '.post-content', '.topic-content', '.cooked', 
                '[data-post-id] .contents', '.post-body',
                '.content', '.raw', '#post-body'
            ]
            
            description = ""
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    for br in content_div.find_all('br'):
                        br.replace_with('\n')
                    description = content_div.get_text('\n', strip=True)
                    if description and len(description) > 50:
                        break
            
            company_selectors = [
                '.post-meta a[href*="/u/"], .topic-meta a[href*="/u/"]',
                '.username', '.creator a', '[data-user-card]',
                '.author a', '.poster a'
            ]
            
            company = ""
            for selector in company_selectors:
                author_link = soup.select_one(selector)
                if author_link:
                    company = author_link.get_text(strip=True)
                    if company and len(company) > 1:
                        break
            
            salary_match = re.search(r'(?:薪资|待遇|薪水|薪酬|salary|pay|budget)[\s:：]*([^\s，。,，\n]+)', description or '')
            salary = ""
            if salary_match:
                salary = salary_match.group(1).strip()
            
            return {
                'description': description,
                'company': company,
                'salary': salary,
            }
        except Exception as e:
            return None
    
    def _parse_title(self, title: str) -> dict:
        result = {
            'company': '',
            'title': title,
            'location': '',
            'salary': '',
        }
        
        patterns = [
            (r'(?:招聘|诚聘|招)[\s:：]*([^\s\|\[\]（）【「「]+?)(?:公司|科技|网络|技术|咨询)?[\s\|·\[\]【「「「]', 'company'),
            (r'([^\s\|\[\]（）]+?)(?:公司|科技|网络|技术|咨询)[\s@/]', 'company'),
            (r'([^\s]+)\s*(?:公司|科技)招聘', 'company'),
            (r'\[(.*?)\]', 'location'),
            (r'【(.*?)】', 'location'),
            (r'「(.*?)」', 'location'),
        ]
        
        for pattern, key in patterns:
            match = re.search(pattern, title)
            if match:
                result[key] = match.group(1).strip()
        
        salary_match = re.search(r'(?:薪资|待遇|薪水|薪酬)[\s:：]*([^\s，。,，]+)', title)
        if salary_match:
            result['salary'] = salary_match.group(1).strip()
        
        return result
    
    def _extract_post_id(self, url: str) -> Optional[str]:
        patterns = [
            r'/posts/(\d+)',
            r'/topics/(\d+)',
            r'/t/(\d+)',
            r'post-(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f"el_{match.group(1)}"
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
    
    def _parse_time(self, text: str) -> Optional[datetime]:
        if not text:
            return None
        
        patterns = [
            r'(\d+)\s*天前',
            r'(\d+)\s*小时前',
            r'(\d+)\s*分钟前',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{4})/(\d{2})/(\d{2})',
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text)
            if match:
                from datetime import timedelta
                now = datetime.now()
                
                if i == 0:
                    days = int(match.group(1))
                    return now - timedelta(days=days)
                elif i == 1:
                    hours = int(match.group(1))
                    return now - timedelta(hours=hours)
                elif i == 2:
                    minutes = int(match.group(1))
                    return now - timedelta(minutes=minutes)
                elif i >= 3:
                    try:
                        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                    except ValueError:
                        pass
        
        return None
    
    def crawl(self, max_pages: int = 3, use_rss: bool = True, fetch_details: bool = True,
              existing_ids: set = None, stop_after_duplicates: int = 5) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        if use_rss:
            try:
                xml_content = self.fetch_page(self.RSS_URL)
                job_list = self.parse_rss(xml_content)
                
                for job_data in job_list:
                    job_id = job_data.get('job_id', '')
                    if not job_id or job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)
                    
                    if job_id in existing_ids:
                        consecutive_duplicates += 1
                        if consecutive_duplicates >= stop_after_duplicates:
                            print(f"  [电鸭社区] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                            return all_jobs
                        continue
                    
                    consecutive_duplicates = 0
                    description = job_data.get('description', '')
                    company = job_data.get('company', '')
                    salary = job_data.get('salary', '')
                    
                    if fetch_details and job_data.get('job_url'):
                        detail = self.fetch_post_detail(job_data['job_url'])
                        if detail:
                            if detail.get('description'):
                                description = detail['description']
                            if not company and detail.get('company'):
                                company = detail['company']
                            if not salary and detail.get('salary'):
                                salary = detail['salary']
                    
                    job_listing = JobListing(
                        source=self.SOURCE,
                        job_id=job_id,
                        title=job_data.get('title', ''),
                        company=company,
                        description=description,
                        location=job_data.get('location', ''),
                        salary=salary,
                        job_url=job_data.get('job_url', ''),
                        posted_at=job_data.get('posted_at'),
                        tags=f'remote, eleduck, {job_data.get("category", "")}' if job_data.get('category') else 'remote, eleduck',
                    )
                    
                    all_jobs.append(job_listing)
                    
            except Exception as e:
                pass
        
        if len(all_jobs) < 10:
            for page in range(1, max_pages + 1):
                try:
                    page_url = f"{self.POSTS_URL}?page={page}"
                    html = self.fetch_page(page_url)
                    job_list = self.parse_posts_page(html)
                    
                    for job_data in job_list:
                        job_id = job_data.get('job_id', '')
                        if not job_id or job_id in seen_ids:
                            continue
                        seen_ids.add(job_id)
                        
                        if job_id in existing_ids:
                            consecutive_duplicates += 1
                            if consecutive_duplicates >= stop_after_duplicates:
                                print(f"  [电鸭社区] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                                return all_jobs
                            continue
                        
                        consecutive_duplicates = 0
                        description = ""
                        company = job_data.get('company', '')
                        salary = job_data.get('salary', '')
                        
                        if fetch_details and job_data.get('job_url'):
                            detail = self.fetch_post_detail(job_data['job_url'])
                            if detail:
                                description = detail.get('description', '')
                                if not company and detail.get('company'):
                                    company = detail['company']
                                if not salary and detail.get('salary'):
                                    salary = detail['salary']
                        
                        job_listing = JobListing(
                            source=self.SOURCE,
                            job_id=job_id,
                            title=job_data.get('title', ''),
                            company=company,
                            description=description,
                            location=job_data.get('location', ''),
                            salary=salary,
                            job_url=job_data.get('job_url', ''),
                            posted_at=job_data.get('posted_at'),
                            tags='remote, eleduck',
                        )
                        
                        all_jobs.append(job_listing)
                        
                except Exception as e:
                    continue
        
        return all_jobs
    
    def close(self):
        self.session.close()
