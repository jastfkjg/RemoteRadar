import re
import time
from datetime import datetime
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

from ..models.job_listing import JobListing


class V2EXSpider:
    SOURCE = "v2ex"
    BASE_URL = "https://www.v2ex.com"
    REMOTE_NODE_URL = "https://www.v2ex.com/go/remote"
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
        response = self.session.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    
    def parse_job_list(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, 'lxml')
        jobs = []
        
        items = soup.select('.item')
        for item in items:
            try:
                title_link = item.select_one('.item_title a')
                if not title_link:
                    continue
                
                title = title_link.get_text(strip=True)
                href = title_link.get('href', '')
                if not href.startswith('http'):
                    href = self.BASE_URL + href
                
                topic_id = self._extract_topic_id(href)
                if not topic_id:
                    continue
                
                meta = item.select_one('.small.fade')
                meta_text = meta.get_text(strip=True) if meta else ""
                posted_at = self._parse_time(meta_text)
                
                job_data = {
                    'title': title,
                    'job_url': href,
                    'topic_id': topic_id,
                    'meta_text': meta_text,
                    'posted_at': posted_at,
                }
                jobs.append(job_data)
            except Exception as e:
                continue
        
        return jobs
    
    def fetch_job_detail(self, url: str) -> Optional[dict]:
        try:
            html = self.fetch_page(url)
            soup = BeautifulSoup(html, 'lxml')
            
            content_div = soup.select_one('.topic_content')
            description = ""
            if content_div:
                for br in content_div.find_all('br'):
                    br.replace_with('\n')
                description = content_div.get_text('\n', strip=True)
            
            author_link = soup.select_one('.header a[href^="/member/"]')
            company = ""
            if author_link:
                company = author_link.get_text(strip=True)
            
            reply_count = 0
            reply_span = soup.select_one('.box .cell strong')
            if reply_span:
                try:
                    reply_count = int(reply_span.get_text(strip=True))
                except ValueError:
                    pass
            
            return {
                'description': description,
                'company': company,
                'reply_count': reply_count,
            }
        except Exception as e:
            return None
    
    def parse_title(self, title: str) -> dict:
        result = {
            'company': '',
            'title': title,
            'location': '',
            'salary': '',
        }
        
        patterns = [
            (r'(?:招聘|诚聘|招)\s*(?:.*?\s*@\s*|)([^\s\|\[\]（）]+?)\s*(?:公司|科技|网络)?[\s\|·\[\]【「]', 'company'),
            (r'([^\s\|\[\]（）]+?)\s*(?:公司|科技|网络)\s*[招@/]', 'company'),
            (r'\[(.*?)\]', 'location'),
            (r'【(.*?)】', 'location'),
            (r'「(.*?)」', 'location'),
        ]
        
        for pattern, key in patterns:
            match = re.search(pattern, title)
            if match:
                result[key] = match.group(1).strip()
        
        salary_match = re.search(r'(?:薪资|待遇|薪水|薪酬)\s*[:：]?\s*([^\s，。]+)', title)
        if salary_match:
            result['salary'] = salary_match.group(1).strip()
        
        return result
    
    def crawl(self, max_pages: int = 3, fetch_details: bool = True) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        
        for page in range(1, max_pages + 1):
            page_url = f"{self.REMOTE_NODE_URL}?p={page}"
            try:
                html = self.fetch_page(page_url)
                job_list = self.parse_job_list(html)
                
                for job_data in job_list:
                    topic_id = job_data['topic_id']
                    if topic_id in seen_ids:
                        continue
                    seen_ids.add(topic_id)
                    
                    parsed = self.parse_title(job_data['title'])
                    
                    description = ""
                    company = parsed.get('company', '')
                    
                    if fetch_details:
                        detail = self.fetch_job_detail(job_data['job_url'])
                        if detail:
                            description = detail.get('description', '')
                            if not company:
                                company = detail.get('company', '')
                    
                    job_listing = JobListing(
                        source=self.SOURCE,
                        job_id=topic_id,
                        title=parsed.get('title', job_data['title']),
                        company=company,
                        description=description,
                        location=parsed.get('location', ''),
                        job_url=job_data['job_url'],
                        posted_at=job_data.get('posted_at'),
                        tags='remote, v2ex',
                    )
                    
                    all_jobs.append(job_listing)
                
            except Exception as e:
                continue
        
        return all_jobs
    
    def _extract_topic_id(self, url: str) -> Optional[str]:
        match = re.search(r'/t/(\d+)', url)
        if match:
            return f"t_{match.group(1)}"
        return None
    
    def _parse_time(self, meta_text: str) -> Optional[datetime]:
        if not meta_text:
            return None
        
        patterns = [
            r'(\d+)\s*天前',
            r'(\d+)\s*小时前',
            r'(\d+)\s*分钟前',
            r'(\d+)\s*秒前',
            r'(\d{4})-(\d{2})-(\d{2})',
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, meta_text)
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
                elif i == 3:
                    seconds = int(match.group(1))
                    return now - timedelta(seconds=seconds)
                elif i == 4:
                    return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        
        return None
    
    def close(self):
        self.session.close()
