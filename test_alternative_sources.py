#!/usr/bin/env python3
"""
测试其他 JustRemote URL 或寻找替代数据源
"""

import requests

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, text/xml, application/xml, text/html, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

urls_to_test = [
    ("JustRemote RSS", "https://justremote.co/rss"),
    ("JustRemote Feed", "https://justremote.co/feed"),
    ("JustRemote Jobs RSS", "https://justremote.co/jobs/rss"),
    ("JustRemote Remote Jobs Feed", "https://justremote.co/remote-jobs/feed"),
    ("JustRemote API", "https://justremote.co/api/jobs"),
    ("FlexJobs RSS", "https://www.flexjobs.com/rss/jobs"),
    ("FlexJobs Feed", "https://www.flexjobs.com/feed"),
    ("We Work Remotely RSS", "https://weworkremotely.com/remote-jobs.rss"),
    ("Remote.co Jobs", "https://remote.co/remote-jobs/"),
]


def test_url(name, url):
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=30, allow_redirects=True)
        print(f"状态码: {response.status_code}")
        print(f"最终 URL: {response.url}")
        print(f"Content-Type: {response.headers.get('content-type', '')}")
        
        content_type = response.headers.get('content-type', '').lower()
        text = response.text[:1500]
        
        is_rss = 'xml' in content_type or '<rss' in text or '<feed' in text or '<item' in text
        is_html = 'html' in content_type or '<!DOCTYPE' in text or '<html' in text
        
        if is_rss:
            print("✓ 看起来是 RSS/Atom 格式")
            print(f"\n内容预览:\n{text[:1000]}")
            return True
        elif is_html:
            print("✗ 看起来是 HTML 页面")
            return False
        else:
            print(f"内容预览:\n{text[:500]}")
            return None
            
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        return False


def main():
    print("="*60)
    print("测试各种远程工作网站的数据源")
    print("="*60)
    
    results = {}
    
    for name, url in urls_to_test:
        results[name] = test_url(name, url)
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, success in results.items():
        if success is True:
            print(f"  ✓ {name}: RSS 可用")
        elif success is False:
            print(f"  ✗ {name}: 不是 RSS")
        else:
            print(f"  ? {name}: 不确定")


if __name__ == "__main__":
    main()
