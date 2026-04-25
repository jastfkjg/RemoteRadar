import re
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager

from ..models.job_listing import JobListing


class PlaywrightSpider:
    SOURCE = "playwright"
    BASE_URL = ""
    
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    def __init__(self, delay: float = 2.0, headless: bool = True):
        self.delay = delay
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
    
    @asynccontextmanager
    async def browser_context(self):
        from playwright.async_api import async_playwright
        
        playwright = None
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                ]
            )
            
            self.context = await self.browser.new_context(
                user_agent=self.REQUEST_HEADERS['User-Agent'],
                viewport={'width': 1920, 'height': 1080},
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
            )
            
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en']
                });
            """)
            
            self.page = await self.context.new_page()
            
            yield self.page
            
        finally:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if playwright:
                await playwright.stop()
    
    async def navigate_and_wait(self, url: str, wait_selector: str = None, timeout: int = 30000):
        if not self.page:
            raise RuntimeError("Page not initialized. Use browser_context() context manager.")
        
        await self.page.goto(url, wait_until='networkidle', timeout=timeout)
        
        if wait_selector:
            try:
                await self.page.wait_for_selector(wait_selector, timeout=timeout)
            except Exception as e:
                pass
        
        await self.page.wait_for_timeout(self.delay * 1000)
    
    async def scroll_to_bottom(self, scroll_pause: float = 1.0, max_scrolls: int = 10):
        if not self.page:
            return
        
        previous_height = 0
        for i in range(max_scrolls):
            current_height = await self.page.evaluate('document.body.scrollHeight')
            
            if current_height == previous_height:
                break
            
            previous_height = current_height
            
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await self.page.wait_for_timeout(scroll_pause * 1000)
    
    async def get_page_html(self) -> str:
        if not self.page:
            return ""
        return await self.page.content()
    
    async def get_page_text(self, selector: str = None) -> str:
        if not self.page:
            return ""
        
        if selector:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    return await element.inner_text()
            except Exception:
                pass
            return ""
        
        return await self.page.inner_text()
    
    async def extract_links(self, selector: str = "a") -> List[Dict[str, str]]:
        if not self.page:
            return []
        
        links = await self.page.evaluate(f'''
            () => {{
                const elements = document.querySelectorAll("{selector}");
                const results = [];
                elements.forEach(el => {{
                    if (el.href && el.href.startsWith('http')) {{
                        results.push({{
                            href: el.href,
                            text: el.innerText?.trim() || ''
                        }});
                    }}
                }});
                return results;
            }}
        ''')
        
        return links
    
    def _clean_description(self, html_text: str) -> str:
        if not html_text:
            return ""
        
        html_text = html_text.strip()
        if len(html_text) < 10:
            return html_text
        
        if '<' not in html_text and '>' not in html_text:
            return html_text
        
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
                try:
                    from datetime import timedelta
                    
                    patterns = [
                        (r'(\d+)\s*days?', 'days'),
                        (r'(\d+)\s*hours?', 'hours'),
                        (r'(\d+)\s*minutes?', 'minutes'),
                        (r'(\d+)\s*weeks?', 'weeks'),
                        (r'(\d+)\s*months?', 'days', 30),
                    ]
                    
                    now = datetime.now()
                    
                    for pattern in patterns:
                        if len(pattern) == 3:
                            p, unit, multiplier = pattern
                        else:
                            p, unit = pattern
                            multiplier = 1
                        
                        match = re.search(p, date_str, re.IGNORECASE)
                        if match:
                            count = int(match.group(1)) * multiplier
                            if unit == 'days':
                                return now - timedelta(days=count)
                            elif unit == 'hours':
                                return now - timedelta(hours=count)
                            elif unit == 'minutes':
                                return now - timedelta(minutes=count)
                            elif unit == 'weeks':
                                return now - timedelta(weeks=count)
                    
                except Exception:
                    return None
        
        return None
    
    async def crawl(self, **kwargs) -> List[JobListing]:
        raise NotImplementedError("Subclasses must implement crawl() method")
    
    def close(self):
        pass
