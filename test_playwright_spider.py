#!/usr/bin/env python3
"""
测试 Playwright 爬虫
测试 JustRemote 网站是否能被正确抓取
"""

import asyncio
import sys
from datetime import datetime

sys.path.insert(0, '.')


def test_import():
    """测试导入是否正常"""
    print("测试导入...")
    try:
        from src.spiders.playwright_spider import PlaywrightSpider
        from src.spiders.justremote_spider import JustRemoteSpider
        print("  ✓ PlaywrightSpider 导入成功")
        print("  ✓ JustRemoteSpider 导入成功")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False


async def test_playwright_basic():
    """测试 Playwright 基础功能"""
    print("\n测试 Playwright 基础功能...")
    try:
        from playwright.async_api import async_playwright
        
        print("  正在启动浏览器...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print("  正在访问测试页面...")
            await page.goto('https://httpbin.org/get', wait_until='networkidle')
            content = await page.content()
            
            if 'httpbin' in content:
                print("  ✓ Playwright 基础功能正常")
            else:
                print("  ✗ 页面内容异常")
            
            await browser.close()
            return True
            
    except Exception as e:
        print(f"  ✗ Playwright 测试失败: {e}")
        print("  提示: 可能需要运行 'playwright install chromium'")
        return False


async def test_justremote_spider():
    """测试 JustRemote 爬虫"""
    print("\n测试 JustRemote 爬虫...")
    try:
        from src.spiders.justremote_spider import JustRemoteSpider
        
        spider = JustRemoteSpider(delay=1.0, headless=True)
        
        print("  开始爬取（限制最多5个职位）...")
        jobs = spider.crawl(max_jobs=5, stop_after_duplicates=999)
        
        print(f"\n  爬取结果:")
        print(f"    总职位数: {len(jobs)}")
        
        if jobs:
            print(f"\n  职位详情:")
            for i, job in enumerate(jobs, 1):
                print(f"\n    {i}. {job.title}")
                print(f"       公司: {job.company or '未知'}")
                print(f"       地点: {job.location or 'Remote'}")
                print(f"       链接: {job.job_url}")
                if job.posted_at:
                    print(f"       发布时间: {job.posted_at.strftime('%Y-%m-%d %H:%M')}")
                if job.salary:
                    print(f"       薪资: {job.salary}")
                if job.tags:
                    print(f"       标签: {job.tags}")
        
        spider.close()
        return len(jobs) > 0
        
    except Exception as e:
        print(f"  ✗ JustRemote 爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("=" * 60)
    print("Playwright 爬虫测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    results['import'] = test_import()
    
    results['playwright_basic'] = await test_playwright_basic()
    
    if results['playwright_basic']:
        results['justremote'] = await test_justremote_spider()
    else:
        results['justremote'] = False
        print("\n  跳过 JustRemote 测试，因为 Playwright 基础功能失败")
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if all_passed:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print("\n✗ 部分测试失败")
        print("\n提示:")
        print("  - 如果 Playwright 基础功能失败，请运行: pip install playwright && playwright install chromium")
        print("  - 确保网络连接正常")
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
