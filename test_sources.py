#!/usr/bin/env python3
"""
测试各个远程工作网站的数据源可用性
"""

import requests
import sys
from datetime import datetime

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, application/xml, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def test_url(name, url, is_json=False, is_rss=False):
    """测试一个 URL 是否可用"""
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=30, allow_redirects=True)
        print(f"状态码: {response.status_code}")
        print(f"最终 URL: {response.url}")
        
        if response.status_code == 200:
            if is_json:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✓ 返回列表，共 {len(data)} 项")
                        if len(data) > 0:
                            print(f"  示例项: {list(data[0].keys())[:5]}")
                        return True
                    elif isinstance(data, dict):
                        print(f"✓ 返回对象，键: {list(data.keys())[:10]}")
                        # 检查是否有 jobs 字段
                        for key in ['jobs', 'results', 'data', 'items']:
                            if key in data:
                                val = data[key]
                                if isinstance(val, list):
                                    print(f"  ✓ {key}: {len(val)} 个职位")
                                    if len(val) > 0:
                                        print(f"    示例: {list(val[0].keys())[:5]}")
                        return True
                except Exception as e:
                    print(f"✗ JSON 解析失败: {e}")
                    print(f"响应预览: {response.text[:500]}")
            
            if is_rss:
                content_type = response.headers.get('content-type', '').lower()
                print(f"Content-Type: {content_type}")
                text = response.text.lower()
                if 'rss' in text or 'channel' in text or 'item' in text or '<entry>' in text:
                    print(f"✓ 看起来是 RSS/Atom 格式")
                    # 简单检查是否有职位
                    item_count = response.text.lower().count('<item>') + response.text.lower().count('<entry>')
                    if item_count > 0:
                        print(f"  约 {item_count} 个职位项")
                    return True
                else:
                    print(f"响应预览: {response.text[:300]}")
            
            # 默认检查 HTML
            text = response.text.lower()
            if 'job' in text or 'position' in text or 'vacancy' in text:
                print(f"✓ 页面包含职位相关内容")
                return True
            else:
                print(f"响应预览: {response.text[:300]}")
                
        elif response.status_code in [301, 302, 303, 307, 308]:
            print(f"重定向到: {response.headers.get('Location', 'unknown')}")
        elif response.status_code == 403:
            print(f"✗ 403 Forbidden - 可能被反爬拦截")
        elif response.status_code == 404:
            print(f"✗ 404 Not Found - 页面可能已不存在")
        elif response.status_code == 429:
            print(f"✗ 429 Too Many Requests - 请求频率限制")
            
    except requests.exceptions.Timeout:
        print(f"✗ 请求超时")
    except requests.exceptions.ConnectionError as e:
        print(f"✗ 连接错误: {e}")
    except Exception as e:
        print(f"✗ 其他错误: {type(e).__name__}: {e}")
    
    return False


def main():
    print("="*60)
    print("RemoteRadar 数据源可用性测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {}
    
    # ===== 现有爬虫测试 =====
    print("\n" + "="*60)
    print("一、现有爬虫测试")
    print("="*60)
    
    # 1. RemoteOK - API
    results['remoteok'] = test_url(
        "RemoteOK (API)",
        "https://remoteok.com/api",
        is_json=True
    )
    
    # 2. Remotive - API
    results['remotive'] = test_url(
        "Remotive (API)",
        "https://remotive.com/api/remote-jobs",
        is_json=True
    )
    
    # 3. Wework Remotely - RSS
    results['wework'] = test_url(
        "Wework Remotely (RSS)",
        "https://weworkremotely.com/remote-jobs.rss",
        is_rss=True
    )
    
    # 4. Stack Overflow Jobs - RSS
    results['stackoverflow'] = test_url(
        "Stack Overflow Jobs (RSS)",
        "https://stackoverflow.com/jobs/feed",
        is_rss=True
    )
    
    # 5. Working Nomads - RSS
    results['workingnomads'] = test_url(
        "Working Nomads (RSS)",
        "https://www.workingnomads.com/jobs/feed",
        is_rss=True
    )
    
    # 6. V2EX
    results['v2ex'] = test_url(
        "V2EX 远程工作节点",
        "https://www.v2ex.com/go/remote",
    )
    
    # ===== 潜在新数据源测试 =====
    print("\n" + "="*60)
    print("二、潜在新数据源测试")
    print("="*60)
    
    # 1. Hacker News Who is hiring? (通过 API)
    # 最新的 "Ask HN: Who is hiring?" 帖子需要查找
    
    # 2. GraphQL Jobs - API
    results['graphqljobs'] = test_url(
        "GraphQL Jobs (API)",
        "https://api.graphql.jobs/jobs",
        is_json=True
    )
    
    # 3. EU Remote Jobs - RSS
    results['euremotejobs'] = test_url(
        "EU Remote Jobs (RSS)",
        "https://euremotejobs.com/feed/",
        is_rss=True
    )
    
    # 4. Daily Remote - RSS
    results['dailyremote'] = test_url(
        "Daily Remote (RSS)",
        "https://dailyremote.com/feed",
        is_rss=True
    )
    
    # 5. Himalayas - API/RSS
    results['himalayas'] = test_url(
        "Himalayas (RSS)",
        "https://himalayas.app/jobs/rss",
        is_rss=True
    )
    
    # 6. Relocate.me - RSS
    results['relocate'] = test_url(
        "Relocate.me (RSS)",
        "https://relocate.me/feed",
        is_rss=True
    )
    
    # 7. JustRemote - RSS
    results['justremote'] = test_url(
        "JustRemote (RSS)",
        "https://justremote.co/rss",
        is_rss=True
    )
    
    # ===== 汇总 =====
    print("\n" + "="*60)
    print("三、测试结果汇总")
    print("="*60)
    
    print("\n现有爬虫:")
    for name in ['remoteok', 'remotive', 'wework', 'stackoverflow', 'workingnomads', 'v2ex']:
        status = "✓ 可用" if results.get(name) else "✗ 不可用"
        print(f"  {name}: {status}")
    
    print("\n潜在新数据源:")
    for name in ['graphqljobs', 'euremotejobs', 'dailyremote', 'himalayas', 'relocate', 'justremote']:
        if name in results:
            status = "✓ 可用" if results[name] else "✗ 不可用"
            print(f"  {name}: {status}")
    
    return results


if __name__ == "__main__":
    main()
