#!/usr/bin/env python3
"""
测试新爬虫是否正常工作
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.spiders.himalayas_spider import HimalayasSpider
from src.spiders.justremote_spider import JustRemoteSpider


def test_himalayas():
    print("\n" + "="*60)
    print("测试 Himalayas 爬虫")
    print("="*60)
    
    try:
        spider = HimalayasSpider(delay=1.0)
        jobs = spider.crawl(max_jobs=5)
        spider.close()
        
        print(f"爬取到 {len(jobs)} 个职位")
        for i, job in enumerate(jobs[:3]):
            print(f"\n  职位 {i+1}:")
            print(f"    标题: {job.title}")
            print(f"    公司: {job.company}")
            print(f"    地点: {job.location}")
            print(f"    链接: {job.job_url}")
        
        return True
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_justremote():
    print("\n" + "="*60)
    print("测试 JustRemote 爬虫")
    print("="*60)
    
    try:
        spider = JustRemoteSpider(delay=1.0)
        jobs = spider.crawl(max_jobs=5)
        spider.close()
        
        print(f"爬取到 {len(jobs)} 个职位")
        for i, job in enumerate(jobs[:3]):
            print(f"\n  职位 {i+1}:")
            print(f"    标题: {job.title}")
            print(f"    公司: {job.company}")
            print(f"    地点: {job.location}")
            print(f"    链接: {job.job_url}")
        
        return True
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*60)
    print("新爬虫测试")
    print("="*60)
    
    results = {}
    
    results['himalayas'] = test_himalayas()
    results['justremote'] = test_justremote()
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, success in results.items():
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {name}: {status}")


if __name__ == "__main__":
    main()
