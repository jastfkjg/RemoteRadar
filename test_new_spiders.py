#!/usr/bin/env python3
"""
测试新的爬虫模块
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_remotive():
    print("=" * 60)
    print("测试 Remotive API")
    print("=" * 60)
    
    try:
        from src.spiders.remotive_spider import RemotiveSpider
        
        spider = RemotiveSpider(delay=1.0)
        jobs = spider.crawl(max_jobs=10)
        
        print(f"获取到 {len(jobs)} 个职位")
        for i, job in enumerate(jobs[:5], 1):
            print(f"\n{i}. {job.title}")
            print(f"   公司: {job.company}")
            print(f"   地点: {job.location or '全球'}")
            print(f"   来源: {job.source}")
            print(f"   链接: {job.job_url}")
        
        spider.close()
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_eluduck():
    print("\n" + "=" * 60)
    print("测试 电鸭社区 (Eluduck)")
    print("=" * 60)
    
    try:
        from src.spiders.eluduck_spider import EluduckSpider
        
        spider = EluduckSpider(delay=1.0)
        jobs = spider.crawl(max_pages=1, use_rss=True, fetch_details=False)
        
        print(f"获取到 {len(jobs)} 个职位")
        for i, job in enumerate(jobs[:5], 1):
            print(f"\n{i}. {job.title}")
            print(f"   公司: {job.company or '未知'}")
            print(f"   来源: {job.source}")
            print(f"   链接: {job.job_url}")
        
        spider.close()
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 60)
    print("测试新爬虫模块")
    print("=" * 60)
    
    results = {}
    
    results['remotive'] = test_remotive()
    results['eluduck'] = test_eluduck()
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    
    for name, success in results.items():
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {name}: {status}")


if __name__ == "__main__":
    main()
