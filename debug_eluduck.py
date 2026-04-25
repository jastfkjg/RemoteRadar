#!/usr/bin/env python3
"""
测试电鸭社区 RSS 和网站结构
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def test_rss():
    print("=" * 60)
    print("测试电鸭社区 RSS")
    print("=" * 60)
    
    urls = [
        "https://eleduck.com/feed/rss",
        "https://eleduck.com/feed",
        "https://eleduck.com/categories/3.rss",
    ]
    
    for url in urls:
        try:
            print(f"\n尝试: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            print(f"状态码: {response.status_code}")
            print(f"内容类型: {response.headers.get('Content-Type', '')}")
            
            if response.status_code == 200:
                print(f"内容预览:\n{response.text[:1000]}")
        except Exception as e:
            print(f"错误: {e}")


def test_pages():
    print("\n" + "=" * 60)
    print("测试电鸭社区页面结构")
    print("=" * 60)
    
    urls = [
        "https://eleduck.com",
        "https://eleduck.com/categories/3",
        "https://eleduck.com/categories/3?page=1",
    ]
    
    for url in urls:
        try:
            print(f"\n尝试: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                
                items = soup.select('.topic-list-item, .topic, [data-topic-id], .post-item, .topic-list')
                print(f"找到的主题元素: {len(items)}")
                
                if items:
                    for i, item in enumerate(items[:3]):
                        print(f"\n  元素 {i+1}:")
                        print(f"    class: {item.get('class', [])}")
                        print(f"    内容: {item.get_text()[:200]}")
                
                links = soup.select('a[href*="/t/"], a[href*="/posts/"], a[href*="/topics/"]')
                print(f"找到的主题链接: {len(links)}")
                
                if links:
                    for i, link in enumerate(links[:5]):
                        print(f"\n  链接 {i+1}:")
                        print(f"    文本: {link.get_text()[:100]}")
                        print(f"    href: {link.get('href', '')}")
                
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_rss()
    test_pages()
