#!/usr/bin/env python3
"""
详细调试 JustRemote 网站
查看所有链接和页面结构
"""

import asyncio
import sys

sys.path.insert(0, '.')


async def debug_detailed():
    from playwright.async_api import async_playwright
    
    print("=" * 70)
    print("详细调试 JustRemote 网站")
    print("=" * 70)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
        )
        
        page = await context.new_page()
        
        url = 'https://justremote.co/'
        print(f"\n正在访问首页: {url}")
        
        await page.goto(url, wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(3000)
        
        page_title = await page.title()
        print(f"页面标题: {page_title}")
        
        all_links = await page.evaluate('''
            () => {
                const links = [];
                const seen = new Set();
                document.querySelectorAll('a').forEach(a => {
                    if (a.href && a.href.startsWith('http') && !seen.has(a.href)) {
                        seen.add(a.href);
                        links.push({
                            href: a.href,
                            text: (a.innerText || '').trim().substring(0, 80)
                        });
                    }
                });
                return links;
            }
        ''')
        
        print(f"\n首页找到 {len(all_links)} 个链接")
        
        job_related_links = []
        for link in all_links:
            href = link['href']
            text = link['text'].lower()
            
            if ('job' in href.lower() or 'remote' in href.lower()) and \
               'new' not in href.lower() and \
               not href.endswith('/remote-jobs') and \
               not href.endswith('/remote-jobs/'):
                job_related_links.append(link)
        
        print(f"\n可能的职位链接（排除 /remote-jobs 和 new）: {len(job_related_links)} 个")
        for i, link in enumerate(job_related_links[:30], 1):
            print(f"  {i}. {link['href']}")
            if link['text']:
                print(f"     文本: {link['text'][:60]}")
        
        print(f"\n{'=' * 70}")
        print("尝试访问 /remote-development-jobs 页面")
        print("=" * 70)
        
        await page.goto('https://justremote.co/remote-development-jobs', wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(3000)
        
        page_title = await page.title()
        print(f"\n页面标题: {page_title}")
        
        dev_links = await page.evaluate('''
            () => {
                const links = [];
                const seen = new Set();
                document.querySelectorAll('a').forEach(a => {
                    if (a.href && a.href.startsWith('http') && !seen.has(a.href)) {
                        seen.add(a.href);
                        links.push({
                            href: a.href,
                            text: (a.innerText || '').trim().substring(0, 100)
                        });
                    }
                });
                return links;
            }
        ''')
        
        print(f"\n开发职位页面找到 {len(dev_links)} 个链接")
        
        actual_jobs = []
        for link in dev_links:
            href = link['href']
            text = link['text']
            
            if 'justremote.co' in href and \
               '/remote-' in href and \
               '-jobs' not in href.split('/')[-1] and \
               'new' not in href.lower() and \
               len(href.split('/')[-1]) > 10:
                actual_jobs.append(link)
        
        print(f"\n可能的具体职位链接: {len(actual_jobs)} 个")
        for i, link in enumerate(actual_jobs[:20], 1):
            print(f"  {i}. {link['href']}")
            if link['text']:
                print(f"     文本: {link['text'][:80]}")
        
        body_html = await page.content()
        body_text = await page.inner_text('body')
        
        print(f"\n{'=' * 70}")
        print("页面内容分析")
        print("=" * 70)
        print(f"HTML 长度: {len(body_html)} 字符")
        print(f"文本长度: {len(body_text)} 字符")
        
        patterns = [
            r'/remote-[^/]+-[^/]+-(?:developer|engineer|designer|manager)',
            r'/remote-[a-z-]+-\d+$',
            r'job-[a-f0-9]+',
        ]
        
        import re
        for pattern in patterns:
            matches = re.findall(pattern, body_html, re.IGNORECASE)
            if matches:
                print(f"\n模式 '{pattern}' 匹配到 {len(matches)} 个:")
                for m in list(set(matches))[:10]:
                    print(f"  - {m}")
        
        print(f"\n{'=' * 70}")
        print("尝试寻找数据 API")
        print("=" * 70)
        
        api_patterns = [
            r'https?://[^"\']+api[^"\']*',
            r'https?://[^"\']+graphql[^"\']*',
            r'window\.__NEXT_DATA__\s*=\s*({[^;]+})',
            r'__NEXT_DATA__',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, body_html, re.IGNORECASE)
            if matches:
                print(f"模式 '{pattern[:50]}...' 匹配到 {len(matches)} 个")
        
        if '__NEXT_DATA__' in body_html:
            print("\n检测到 Next.js 应用，尝试提取 __NEXT_DATA__")
            
            next_data_match = re.search(r'window\.__NEXT_DATA__\s*=\s*({[^;]+});?', body_html)
            if next_data_match:
                print(f"找到 __NEXT_DATA__ (长度: {len(next_data_match.group(1))})")
        
        await browser.close()


if __name__ == '__main__':
    asyncio.run(debug_detailed())
