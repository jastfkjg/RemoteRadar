#!/usr/bin/env python3
"""
调试 JustRemote 爬虫
"""

import requests
from bs4 import BeautifulSoup

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, text/xml, application/xml, text/html, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://justremote.co/",
}

RSS_URL = "https://justremote.co/rss"


def main():
    print("="*60)
    print("调试 JustRemote RSS")
    print("="*60)
    
    try:
        response = requests.get(RSS_URL, headers=REQUEST_HEADERS, timeout=30, allow_redirects=True)
        print(f"状态码: {response.status_code}")
        print(f"最终 URL: {response.url}")
        print(f"Content-Type: {response.headers.get('content-type', '')}")
        
        print(f"\n响应内容预览 (前 2000 字符):")
        print(response.text[:2000])
        
        print(f"\n\n解析 XML...")
        soup = BeautifulSoup(response.text, 'xml')
        
        entries = soup.find_all('entry')
        items = soup.find_all('item')
        print(f"找到 {len(entries)} 个 entry, {len(items)} 个 item")
        
        if entries:
            print("\n第一个 entry 预览:")
            print(entries[0].prettify()[:1000])
        
        if items:
            print("\n第一个 item 预览:")
            print(items[0].prettify()[:1000])
        
    except Exception as e:
        import traceback
        print(f"错误: {type(e).__name__}: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
