#!/usr/bin/env python3
"""
调试 JustRemote 网站结构
使用 Playwright 查看页面实际内容
"""

import asyncio
import sys

sys.path.insert(0, '.')


async def debug_page_structure():
    from playwright.async_api import async_playwright
    
    print("=" * 60)
    print("调试 JustRemote 网站结构")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
        )
        
        page = await context.new_page()
        
        url = 'https://justremote.co/remote-jobs'
        print(f"\n正在访问: {url}")
        
        await page.goto(url, wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(3000)
        
        print("\n等待页面加载完成...")
        await page.wait_for_timeout(2000)
        
        current_url = page.url
        print(f"\n当前 URL: {current_url}")
        
        page_title = await page.title()
        print(f"页面标题: {page_title}")
        
        all_links = await page.evaluate('''
            () => {
                const links = [];
                document.querySelectorAll('a').forEach(a => {
                    if (a.href && a.href.startsWith('http')) {
                        links.push({
                            href: a.href,
                            text: a.innerText?.trim()?.substring(0, 100) || ''
                        });
                    }
                });
                return links;
            }
        ''')
        
        print(f"\n找到 {len(all_links)} 个链接")
        
        job_links = [link for link in all_links if '/remote-jobs/' in link['href']]
        print(f"\n包含 '/remote-jobs/' 的链接: {len(job_links)} 个")
        
        for i, link in enumerate(job_links[:20], 1):
            print(f"  {i}. {link['href']}")
            if link['text']:
                print(f"     文本: {link['text'][:80]}")
        
        page_html = await page.content()
        print(f"\n页面 HTML 长度: {len(page_html)} 字符")
        
        if 'job' in page_html.lower():
            print("页面包含 'job' 关键词")
        else:
            print("页面不包含 'job' 关键词")
        
        selectors_to_try = [
            'a[href*="/remote-jobs/"]',
            '[class*="job"] a',
            '[class*="card"] a',
            '[class*="listing"] a',
            'main a',
            'article a',
            '[data-testid*="job"] a',
        ]
        
        print("\n测试各种选择器:")
        for selector in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                print(f"  {selector}: {len(elements)} 个元素")
                
                if elements and len(elements) > 0:
                    for i, el in enumerate(elements[:3]):
                        href = await el.get_attribute('href')
                        text = await el.inner_text()
                        if href:
                            print(f"    - href: {href[:100]}")
                        if text and text.strip():
                            print(f"      text: {text.strip()[:80]}")
            except Exception as e:
                print(f"  {selector}: 错误 - {e}")
        
        print("\n滚动页面加载更多内容...")
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(2000)
        
        job_links_after_scroll = await page.evaluate('''
            () => {
                const links = [];
                const seen = new Set();
                document.querySelectorAll('a[href*="/remote-jobs/"]').forEach(a => {
                    if (a.href && !seen.has(a.href)) {
                        seen.add(a.href);
                        links.push({
                            href: a.href,
                            text: a.innerText?.trim()?.substring(0, 100) || ''
                        });
                    }
                });
                return links;
            }
        ''')
        
        print(f"滚动后包含 '/remote-jobs/' 的链接: {len(job_links_after_scroll)} 个")
        
        body_text = await page.inner_text('body')
        print(f"\n页面文本中 'job' 出现次数: {body_text.lower().count('job')}")
        print(f"页面文本中 'remote' 出现次数: {body_text.lower().count('remote')}")
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(debug_page_structure())
