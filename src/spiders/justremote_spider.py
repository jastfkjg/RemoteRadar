import asyncio
import re
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any, Set

from .playwright_spider import PlaywrightSpider
from ..models.job_listing import JobListing


class JustRemoteSpider(PlaywrightSpider):
    SOURCE = "justremote"
    BASE_URL = "https://justremote.co"
    
    CATEGORIES = [
        'developer', 'design', 'marketing', 'sales',
        'data', 'devops', 'finance', 'content', 'operations', 'all'
    ]
    
    CATEGORY_URLS = {
        'developer': '/remote-developer-jobs',
        'design': '/remote-design-jobs',
        'marketing': '/remote-marketing-jobs',
        'sales': '/remote-sales-jobs',
        'data': '/remote-data-science-jobs',
        'devops': '/remote-devops-sysadmin-jobs',
        'finance': '/remote-finance-jobs',
        'content': '/remote-editing-jobs',
        'operations': '/remote-project-manager-jobs',
        'all': '/',
    }
    
    def __init__(self, delay: float = 2.0, headless: bool = True):
        super().__init__(delay=delay, headless=headless)
    
    async def _crawl_async(self, categories: List[str] = None, max_jobs: int = 100,
                           existing_ids: set = None, stop_after_duplicates: int = 5) -> List[JobListing]:
        all_jobs = []
        seen_ids = set()
        existing_ids = existing_ids or set()
        consecutive_duplicates = 0
        
        urls_to_try = []
        
        if categories and categories != ['all']:
            for cat in categories:
                if cat in self.CATEGORY_URLS:
                    urls_to_try.append(f"{self.BASE_URL}{self.CATEGORY_URLS[cat]}")
        else:
            urls_to_try.append(f"{self.BASE_URL}/")
        
        async with self.browser_context():
            for url in urls_to_try:
                if len(all_jobs) >= max_jobs:
                    break
                
                try:
                    print(f"  [JustRemote] 正在访问: {url}")
                    await self.navigate_and_wait(url, wait_selector='a[href*="/remote-"]', timeout=30000)
                    
                    await self.scroll_to_bottom(scroll_pause=1.0, max_scrolls=3)
                    
                    job_links = await self._extract_job_links()
                    
                    print(f"  [JustRemote] 发现 {len(job_links)} 个职位链接")
                    
                    for job_link in job_links:
                        if len(all_jobs) >= max_jobs:
                            break
                        
                        job_href = job_link.get('href', '')
                        job_text = job_link.get('text', '')
                        
                        job_id = self._extract_job_id(job_href)
                        if not job_id:
                            continue
                        
                        if job_id in seen_ids:
                            continue
                        seen_ids.add(job_id)
                        
                        if job_id in existing_ids:
                            consecutive_duplicates += 1
                            if consecutive_duplicates >= stop_after_duplicates:
                                print(f"  [JustRemote] 遇到连续 {consecutive_duplicates} 个已存在职位，停止爬取")
                                return all_jobs
                            continue
                        
                        consecutive_duplicates = 0
                        
                        job_data = await self._fetch_job_detail(job_href, job_text)
                        if job_data:
                            job_data['job_id'] = job_id
                            job_listing = self._create_job_listing(job_data)
                            if job_listing:
                                all_jobs.append(job_listing)
                                print(f"    ✓ {job_listing.title} at {job_listing.company}")
                    
                except Exception as e:
                    print(f"  [JustRemote] 爬取出错: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        return all_jobs
    
    async def _extract_job_links(self) -> List[Dict[str, str]]:
        if not self.page:
            return []
        
        try:
            links = await self.page.evaluate('''
                () => {
                    const results = [];
                    const seen = new Set();
                    
                    const categoryPattern = /\\/remote-(developer|design|marketing|sales|data-science|devops-sysadmin|finance|editing|project-manager|manager-exec|customer-service|hr|recruiter|seo|social-media|writing)-jobs\\//;
                    
                    document.querySelectorAll('a').forEach(a => {
                        const href = a.href;
                        if (!href || !href.startsWith('http')) return;
                        if (seen.has(href)) return;
                        
                        if (href.includes('justremote.co') && 
                            categoryPattern.test(href) &&
                            !href.includes('/new') &&
                            !href.includes('?') &&
                            !href.includes('#')) {
                            
                            const segments = href.split('/');
                            const lastSegment = segments[segments.length - 1];
                            
                            if (lastSegment && lastSegment.length > 10) {
                                seen.add(href);
                                results.push({
                                    href: href,
                                    text: a.innerText?.trim() || ''
                                });
                            }
                        }
                    });
                    
                    return results;
                }
            ''')
            
            return links
        except Exception as e:
            print(f"  [JustRemote] 提取链接出错: {e}")
            return []
    
    async def _fetch_job_detail(self, url: str, default_text: str = '') -> Optional[Dict[str, Any]]:
        if not self.page:
            return None
        
        try:
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            await self.page.wait_for_timeout(self.delay * 500)
            
            page_text = await self.page.inner_text('body')
            
            job_data = {
                'job_url': url,
                'title': '',
                'company': '',
                'location': '',
                'salary': '',
                'description': '',
                'posted_at': None,
                'tags': '',
            }
            
            title_selectors = [
                'h1',
                '[class*="title"]',
                '[class*="job-title"]',
                '[class*="position"]',
            ]
            
            for selector in title_selectors:
                try:
                    title_elem = await self.page.query_selector(selector)
                    if title_elem:
                        title_text = await title_elem.inner_text()
                        if title_text and len(title_text) > 2:
                            job_data['title'] = title_text.strip()
                            break
                except Exception:
                    continue
            
            if not job_data['title'] and default_text:
                lines = default_text.split('\n')
                if len(lines) >= 2:
                    job_data['company'] = lines[0].strip()
                    job_data['title'] = lines[1].strip()
                elif lines:
                    job_data['title'] = lines[0].strip()
            
            company_selectors = [
                '[class*="company"] a',
                '[class*="company"]',
                '[class*="employer"]',
                'span[class*="name"]',
            ]
            
            for selector in company_selectors:
                try:
                    company_elem = await self.page.query_selector(selector)
                    if company_elem:
                        company_text = await company_elem.inner_text()
                        if company_text and len(company_text) > 1 and len(company_text) < 100:
                            job_data['company'] = company_text.strip()
                            break
                except Exception:
                    continue
            
            if not job_data['company'] and default_text:
                lines = default_text.split('\n')
                if lines:
                    job_data['company'] = lines[0].strip()
            
            if not job_data['company']:
                company_match = re.search(r'(?:at|@|with|by)\s+([A-Z][^\n\r,|]+?)(?:,|\n|\||$| at | @ )', page_text, re.IGNORECASE)
                if company_match:
                    job_data['company'] = company_match.group(1).strip()
            
            location_patterns = [
                r'(?:Location|地点|位置)\s*[:：\s]+([^\n\r，。,，\d]+?)(?:\n|\r|,|$)',
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    if location and len(location) < 100 and 'job' not in location.lower():
                        job_data['location'] = location
                        break
            
            if not job_data['location']:
                keywords = ['Anywhere', 'Worldwide', 'Global']
                for keyword in keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', page_text, re.IGNORECASE):
                        job_data['location'] = keyword
                        break
            
            if not job_data['location']:
                job_data['location'] = 'Remote'
            
            salary_patterns = [
                r'(?:Salary|薪资|Pay|Compensation|Rate)\s*[:：\s]+\$?([\d,\s\-\+Kk$€£]+?)(?:\n|\r|,|$)',
                r'\$([\d,\s\-\+Kk]+)\s*(?:per|/)\s*(?:year|month|hour)',
            ]
            
            for pattern in salary_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    job_data['salary'] = match.group(1).strip()
                    break
            
            description_selectors = [
                '[class*="description"]',
                '[class*="job-description"]',
                '[class*="content"]',
                'main',
            ]
            
            for selector in description_selectors:
                try:
                    desc_elem = await self.page.query_selector(selector)
                    if desc_elem:
                        desc_html = await desc_elem.inner_html()
                        job_data['description'] = self._clean_description(desc_html)
                        if len(job_data['description']) > 50:
                            break
                except Exception:
                    continue
            
            if not job_data['description']:
                job_data['description'] = self._clean_description(page_text)
            
            tags = []
            tag_keywords = ['JavaScript', 'Python', 'React', 'Vue', 'Angular', 'Node', 'TypeScript',
                           'Java', 'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Flutter',
                           'AWS', 'GCP', 'Azure', 'DevOps', 'Docker', 'Kubernetes',
                           'Remote', 'Full-time', 'Part-time', 'Contract', 'Senior', 'Junior', 'Mid']
            
            for keyword in tag_keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', page_text, re.IGNORECASE):
                    tags.append(keyword)
            
            if tags:
                job_data['tags'] = ', '.join(tags)
            
            date_patterns = [
                r'(\d+)\s*(days?|hours?|weeks?|months?)\s+ago',
                r'Posted\s+(\d+)\s*(days?|hours?|weeks?|months?)',
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    count = int(match.group(1))
                    unit = match.group(2).lower()
                    job_data['posted_at'] = self._parse_date(f"{count} {unit} ago")
                    break
            
            return job_data
            
        except Exception as e:
            print(f"  [JustRemote] 获取职位详情出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        if not url:
            return None
        
        patterns = [
            r'/remote-[^/]+-jobs/([^/\?\#]+)',
            r'/job/([^/\?\#]+)',
            r'/jobs/([^/\?\#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                slug = match.group(1)
                if slug and len(slug) > 3 and '?' not in slug and '#' not in slug:
                    return f"jrm_{hashlib.md5(slug.encode()).hexdigest()[:12]}"
        
        if url:
            return f"jrm_{hashlib.md5(url.encode()).hexdigest()[:12]}"
        
        return None
    
    def _create_job_listing(self, job_data: Dict[str, Any]) -> Optional[JobListing]:
        if not job_data:
            return None
        
        try:
            title = job_data.get('title', '')
            if not title:
                return None
            
            company = job_data.get('company', '')
            if not company:
                name_match = re.search(r'([A-Z][a-zA-Z0-9\s\-&]+?)(?:\s+(?:is|at|for|hiring|looking|seeking))', title, re.IGNORECASE)
                if name_match:
                    company = name_match.group(1).strip()
            
            tags = job_data.get('tags', '')
            if not tags:
                tags = 'remote, justremote'
            
            return JobListing(
                source=self.SOURCE,
                job_id=job_data.get('job_id', ''),
                title=title,
                company=company,
                description=job_data.get('description', ''),
                location=job_data.get('location', 'Remote'),
                salary=job_data.get('salary', ''),
                job_url=job_data.get('job_url', ''),
                posted_at=job_data.get('posted_at'),
                tags=tags,
            )
        except Exception as e:
            return None
    
    def crawl(self, categories: List[str] = None, max_jobs: int = 100,
              existing_ids: set = None, stop_after_duplicates: int = 5) -> List[JobListing]:
        try:
            try:
                loop = asyncio.get_running_loop()
                import nest_asyncio
                nest_asyncio.apply()
            except RuntimeError:
                pass
            
            return asyncio.run(self._crawl_async(
                categories=categories,
                max_jobs=max_jobs,
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after_duplicates
            ))
        except Exception as e:
            print(f"  [JustRemote] Playwright 爬虫出错: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def close(self):
        pass
