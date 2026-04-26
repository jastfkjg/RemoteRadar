#!/usr/bin/env python3
"""
RemoteRadar - 远程工作职位爬虫
支持爬取多个远程工作招聘网站
支持两种运行模式:
  - local: 直接写入本地 SQLite (本地开发用)
  - api: 调用远程 API (GitHub Actions 生产用)
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from typing import List, Optional, Set, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from src.database import Database
from src.spiders import (
    V2EXSpider, 
    WeworkSpider, 
    RemoteOkSpider, 
    RemotiveSpider,
    StackOverflowSpider,
    EluduckSpider,
    WellfoundSpider,
    RemoteCoSpider,
    WorkingNomadsSpider,
    NoFluffJobsSpider,
    HimalayasSpider,
    JustRemoteSpider,
    ArbeitnowSpider,
    JobicySpider,
    EmplloSpider,
)
from src.models import JobListing
from src.api_client import RemoteAPIClient, job_listing_to_api_dict


class RemoteRadar:
    AVAILABLE_SPIDERS = [
        'v2ex', 'wework', 'remoteok', 'remotive', 'stackoverflow',
        'wellfound', 'remoteco', 'workingnomads', 'nofluffjobs',
        'himalayas', 'justremote', 'eleduck', 'arbeitnow', 'jobicy', 'empllo', 'all'
    ]
    
    DEFAULT_SPIDERS = [
        'himalayas', 'remoteok', 'remotive', 'arbeitnow', 'jobicy'
    ]
    
    def __init__(self, db_path: str = "jobs.db", mode: str = "local", api_url: str = None, api_key: str = None):
        self.mode = mode
        self.api_url = api_url
        self.api_key = api_key
        self.db = Database(db_path) if mode == 'local' else None
        self.api_client = RemoteAPIClient(api_url, api_key) if mode == 'api' else None
        self.stats = {
            'total_new': 0,
            'total_updated': 0,
            'sources': {},
        }
    
    async def check_api_connection(self) -> bool:
        if self.mode != 'api' or not self.api_client:
            return True
        
        try:
            health = await self.api_client.health_check()
            print(f"API 连接成功: {health.get('status')}, 总职位数: {health.get('total_jobs', 0)}")
            return True
        except Exception as e:
            print(f"API 连接失败: {e}")
            return False
    
    async def get_existing_ids(self, source: str) -> Set[str]:
        if self.mode == 'local' and self.db:
            return self.db.get_existing_job_ids(source)
        elif self.mode == 'api' and self.api_client:
            return await self.api_client.get_existing_job_ids(source)
        return set()
    
    def run_spider(self, spider_name: str, options: dict = None) -> List[JobListing]:
        options = options or {}
        jobs = []
        
        existing_ids = options.get('existing_ids', set())
        stop_after = options.get('stop_after_duplicates', 5)
        
        if spider_name == 'v2ex':
            spider = V2EXSpider(delay=options.get('delay', 1.0))
            jobs = spider.crawl(
                max_pages=options.get('max_pages', 3),
                fetch_details=options.get('fetch_details', True),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
            
        elif spider_name == 'wework':
            spider = WeworkSpider(delay=options.get('delay', 1.0))
            categories = options.get('categories')
            if categories and categories != ['all']:
                jobs = spider.crawl(
                    use_rss=options.get('use_rss', True),
                    fetch_details=options.get('fetch_details', False),
                    categories=categories,
                    existing_ids=existing_ids,
                    stop_after_duplicates=stop_after
                )
            else:
                jobs = spider.crawl(
                    use_rss=True,
                    fetch_details=options.get('fetch_details', False),
                    existing_ids=existing_ids,
                    stop_after_duplicates=stop_after
                )
            spider.close()
            
        elif spider_name == 'remoteok':
            spider = RemoteOkSpider(delay=options.get('delay', 1.0))
            tags = options.get('tags')
            jobs = spider.crawl(
                tags=tags if tags and tags != ['all'] else None,
                max_jobs=options.get('max_jobs', 100),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'remotive':
            spider = RemotiveSpider(delay=options.get('delay', 1.0))
            categories = options.get('categories')
            jobs = spider.crawl(
                categories=categories if categories and categories != ['all'] else None,
                search=options.get('search'),
                max_jobs=options.get('max_jobs', 100),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'stackoverflow':
            spider = StackOverflowSpider(delay=options.get('delay', 1.0))
            categories = options.get('categories')
            jobs = spider.crawl(
                categories=categories if categories and categories != ['all'] else None,
                search=options.get('search'),
                max_jobs=options.get('max_jobs', 100),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'wellfound':
            spider = WellfoundSpider(delay=options.get('delay', 1.5))
            categories = options.get('categories')
            jobs = spider.crawl(
                categories=categories if categories and categories != ['all'] else None,
                max_jobs=options.get('max_jobs', 100),
                fetch_details=options.get('fetch_details', False),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'remoteco':
            spider = RemoteCoSpider(delay=options.get('delay', 1.5))
            categories = options.get('categories')
            jobs = spider.crawl(
                categories=categories if categories and categories != ['all'] else None,
                max_jobs=options.get('max_jobs', 100),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'workingnomads':
            spider = WorkingNomadsSpider(delay=options.get('delay', 1.5))
            categories = options.get('categories')
            jobs = spider.crawl(
                categories=categories if categories and categories != ['all'] else None,
                max_jobs=options.get('max_jobs', 100),
                use_rss=options.get('use_rss', True),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'nofluffjobs':
            spider = NoFluffJobsSpider(delay=options.get('delay', 1.5))
            categories = options.get('categories')
            jobs = spider.crawl(
                categories=categories if categories and categories != ['all'] else None,
                max_jobs=options.get('max_jobs', 100),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'himalayas':
            spider = HimalayasSpider(delay=options.get('delay', 1.0))
            categories = options.get('categories')
            jobs = spider.crawl(
                categories=categories if categories and categories != ['all'] else None,
                max_jobs=options.get('max_jobs', 100),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'justremote':
            spider = JustRemoteSpider(delay=options.get('delay', 1.0))
            categories = options.get('categories')
            jobs = spider.crawl(
                categories=categories if categories and categories != ['all'] else None,
                max_jobs=options.get('max_jobs', 100),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'eleduck':
            spider = EluduckSpider(delay=options.get('delay', 1.0))
            jobs = spider.crawl(
                max_pages=options.get('max_pages', 3),
                use_rss=options.get('use_rss', True),
                fetch_details=options.get('fetch_details', True),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'arbeitnow':
            spider = ArbeitnowSpider(delay=options.get('delay', 0.5))
            jobs = spider.crawl(
                max_pages=options.get('max_pages', 5),
                max_jobs=options.get('max_jobs', 200),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'jobicy':
            spider = JobicySpider(delay=options.get('delay', 1.0))
            categories = options.get('categories')
            jobs = spider.crawl(
                categories=categories if categories and categories != ['all'] else None,
                max_jobs=options.get('max_jobs', 200),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        elif spider_name == 'empllo':
            spider = EmplloSpider(delay=options.get('delay', 1.0))
            jobs = spider.crawl(
                remote_only=options.get('remote_only', True),
                categories=options.get('categories'),
                max_jobs=options.get('max_jobs', 200),
                existing_ids=existing_ids,
                stop_after_duplicates=stop_after
            )
            spider.close()
        
        return jobs
    
    def save_jobs_local(self, jobs: List[JobListing], source: str) -> tuple:
        if source not in self.stats['sources']:
            self.stats['sources'][source] = {'new': 0, 'updated': 0}
        
        new_count = 0
        updated_count = 0
        
        for job in jobs:
            existing = self.db.find_by_source_and_id(job.source, job.job_id)
            job_id = self.db.insert_or_update(job)
            
            if existing:
                updated_count += 1
                self.stats['sources'][source]['updated'] += 1
                self.stats['total_updated'] += 1
            else:
                new_count += 1
                self.stats['sources'][source]['new'] += 1
                self.stats['total_new'] += 1
        
        return new_count, updated_count
    
    async def save_jobs_api(self, jobs: List[JobListing], source: str) -> tuple:
        if source not in self.stats['sources']:
            self.stats['sources'][source] = {'new': 0, 'updated': 0}
        
        if not jobs:
            return 0, 0
        
        jobs_dicts = [job_listing_to_api_dict(job) for job in jobs]
        
        result = await self.api_client.send_jobs_in_batches(jobs_dicts, batch_size=50)
        
        new_count = result.get('new', 0)
        updated_count = result.get('updated', 0)
        
        self.stats['sources'][source]['new'] += new_count
        self.stats['sources'][source]['updated'] += updated_count
        self.stats['total_new'] += new_count
        self.stats['total_updated'] += updated_count
        
        return new_count, updated_count
    
    async def save_jobs(self, jobs: List[JobListing], source: str) -> tuple:
        if self.mode == 'local':
            return self.save_jobs_local(jobs, source)
        elif self.mode == 'api':
            return await self.save_jobs_api(jobs, source)
        return 0, 0
    
    async def run_async(self, spiders: List[str], options: dict = None) -> dict:
        options = options or {}
        
        if 'all' in spiders:
            spiders = self.DEFAULT_SPIDERS
        
        for spider_name in spiders:
            if spider_name not in self.AVAILABLE_SPIDERS:
                continue
            
            existing_ids = await self.get_existing_ids(spider_name)
            print(f"\n[{spider_name}] 已存在 {len(existing_ids)} 个职位，开始增量爬取...")
            
            options['existing_ids'] = existing_ids
            
            jobs = self.run_spider(spider_name, options)
            
            if jobs:
                print(f"  发现 {len(jobs)} 个新职位，准备存储...")
                await self.save_jobs(jobs, spider_name)
            else:
                print(f"  没有发现新职位")
        
        return self.stats
    
    def run(self, spiders: List[str], options: dict = None) -> dict:
        return asyncio.run(self.run_async(spiders, options))
    
    def get_stats(self) -> dict:
        if self.mode == 'local' and self.db:
            stats = {
                'total_jobs': self.db.count_all(),
                'by_source': {},
                'latest_jobs': [],
            }
            
            for source in self.db.get_sources():
                stats['by_source'][source] = self.db.count_by_source(source)
            
            latest = self.db.find_all(limit=10)
            stats['latest_jobs'] = [job.to_dict() for job in latest]
            
            return stats
        return {'total_jobs': 0, 'by_source': {}, 'latest_jobs': []}
    
    def list_jobs(self, source: str = None, limit: int = 50) -> List[JobListing]:
        if self.mode == 'local' and self.db:
            if source and source != 'all':
                return self.db.find_by_source(source, limit=limit)
            return self.db.find_all(limit=limit)
        return []
    
    async def close(self):
        if self.api_client:
            await self.api_client.close()


def get_env_mode() -> str:
    mode = os.getenv("MODE", "local").lower()
    return mode if mode in ['local', 'api'] else 'local'


def main():
    parser = argparse.ArgumentParser(
        description='RemoteRadar - 远程工作职位爬虫',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
运行模式:
  --mode local: 直接写入本地 SQLite (默认，本地开发用)
  --mode api: 调用远程 API (GitHub Actions 生产用)
    需要配置环境变量:
      - API_URL: 后端 API 地址 (如 https://your-domain.com)
      - API_KEY: API 认证密钥

示例:
  # 本地模式，爬取所有网站
  python main.py --spiders all
  
  # API 模式，爬取并发送到远程服务器
  python main.py --spiders all --mode api --api-url https://your-domain.com --api-key your-secret-key
  
  # 使用环境变量配置 API 模式
  export MODE=api
  export API_URL=https://your-domain.com
  export API_KEY=your-secret-key
  python main.py --spiders all
  
  # 增量爬取，遇到连续5个已存在职位后自动停止
  python main.py --spiders all
  
  # 只爬取特定网站
  python main.py --spiders remotive wellfound
  
  # 查看统计信息
  python main.py --stats
  
  # 列出最新职位
  python main.py --list

支持的网站:
  himalayas     - Himalayas (免费公开API，10万+远程职位)
  remoteok      - RemoteOK
  remotive      - Remotive (公开API)
  arbeitnow     - ArbeitNow (免费公开API，聚合多源)
  jobicy        - Jobicy (免费API，含薪资信息)
  empllo        - Empllo (RSS feed，远程职位)
  v2ex          - V2EX 社区远程工作节点
  wework        - Wework Remotely
  stackoverflow - Stack Overflow Jobs (RSS)
  wellfound     - Wellfound (原 AngelList)
  remoteco      - Remote.co
  workingnomads - Working Nomads (RSS)
  nofluffjobs   - NoFluffJobs (欧洲技术岗位)
  eleduck       - 电鸭社区 (有反爬机制)
        '''
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['local', 'api'],
        default=get_env_mode(),
        help='运行模式: local (本地 SQLite), api (远程 API) (默认: local 或 环境变量 MODE)'
    )
    
    parser.add_argument(
        '--api-url',
        default=os.getenv("API_URL"),
        help='API 地址 (默认: 环境变量 API_URL)'
    )
    
    parser.add_argument(
        '--api-key',
        default=os.getenv("API_KEY"),
        help='API 认证密钥 (默认: 环境变量 API_KEY)'
    )
    
    parser.add_argument(
        '--spiders', '-s',
        nargs='+',
        default=['all'],
        choices=['v2ex', 'wework', 'remoteok', 'remotive', 'stackoverflow',
                 'wellfound', 'remoteco', 'workingnomads', 'nofluffjobs', 
                 'eleduck', 'arbeitnow', 'jobicy', 'empllo', 'all'],
        help='指定要爬取的网站 (默认: all - 除 eleduck 外)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=3,
        help='V2EX/电鸭社区 爬取的最大页数 (默认: 3)'
    )
    
    parser.add_argument(
        '--max-jobs',
        type=int,
        default=100,
        help='每个网站爬取的最大职位数 (默认: 100)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.5,
        help='请求间隔时间(秒) (默认: 1.5)'
    )
    
    parser.add_argument(
        '--no-details',
        action='store_true',
        help='不获取职位详情页面，只爬取列表页'
    )
    
    parser.add_argument(
        '--categories',
        nargs='+',
        default=None,
        help='爬取的分类'
    )
    
    parser.add_argument(
        '--tags',
        nargs='+',
        default=None,
        help='RemoteOk 爬取的标签过滤'
    )
    
    parser.add_argument(
        '--search',
        default=None,
        help='搜索关键词'
    )
    
    parser.add_argument(
        '--stop-after',
        type=int,
        default=5,
        help='遇到连续多少个已存在职位后停止爬取 (默认: 5)'
    )
    
    parser.add_argument(
        '--no-incremental',
        action='store_true',
        help='禁用增量爬取，爬取所有职位'
    )
    
    parser.add_argument(
        '--db',
        default='jobs.db',
        help='数据库文件路径 (仅 local 模式, 默认: jobs.db)'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='显示数据库统计信息 (仅 local 模式)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出最新职位 (仅 local 模式)'
    )
    
    parser.add_argument(
        '--source',
        default=None,
        choices=['v2ex', 'wework', 'remoteok', 'remotive', 'stackoverflow',
                 'wellfound', 'remoteco', 'workingnomads', 'nofluffjobs', 
                 'eleduck', 'arbeitnow', 'jobicy', 'empllo', 'all'],
        help='列表显示时过滤来源'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='列表显示的数量限制 (默认: 50)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'api' and not args.api_key:
        print("错误: API 模式需要提供 API Key")
        print("使用 --api-key 参数或设置 API_KEY 环境变量")
        sys.exit(1)
    
    if args.mode == 'api' and not args.api_url:
        print("错误: API 模式需要提供 API URL")
        print("使用 --api-url 参数或设置 API_URL 环境变量")
        sys.exit(1)
    
    radar = RemoteRadar(
        db_path=args.db,
        mode=args.mode,
        api_url=args.api_url,
        api_key=args.api_key
    )
    
    async def run_with_close():
        try:
            if args.stats:
                if args.mode != 'local':
                    print("警告: --stats 仅在 local 模式下有效")
                    return
                stats = radar.get_stats()
                print(f"\n=== RemoteRadar 统计信息 ===")
                print(f"总职位数: {stats['total_jobs']}")
                print(f"\n按来源分布:")
                for source, count in stats['by_source'].items():
                    print(f"  {source}: {count} 个职位")
                print(f"\n最新10个职位:")
                for job in stats['latest_jobs']:
                    posted = job.get('posted_at', '')
                    if posted:
                        try:
                            dt = datetime.fromisoformat(posted)
                            posted = dt.strftime('%Y-%m-%d %H:%M')
                        except Exception:
                            pass
                    print(f"  [{job['source']}] {job['title']} ({job['company']}) - {posted}")
                return
            
            if args.list:
                if args.mode != 'local':
                    print("警告: --list 仅在 local 模式下有效")
                    return
                jobs = radar.list_jobs(source=args.source, limit=args.limit)
                print(f"\n=== 最新职位 (共 {len(jobs)} 个) ===")
                for i, job in enumerate(jobs, 1):
                    posted = ""
                    if job.posted_at:
                        posted = job.posted_at.strftime('%Y-%m-%d %H:%M')
                    print(f"\n{i}. [{job.source}] {job.title}")
                    print(f"   公司: {job.company or '未知'}")
                    print(f"   地点: {job.location or '全球'}")
                    print(f"   发布时间: {posted}")
                    print(f"   链接: {job.job_url}")
                return
            
            if args.mode == 'api':
                connected = await radar.check_api_connection()
                if not connected:
                    print("错误: 无法连接到 API 服务器")
                    sys.exit(1)
            
            options = {
                'max_pages': args.max_pages,
                'max_jobs': args.max_jobs,
                'delay': args.delay,
                'fetch_details': not args.no_details,
                'categories': args.categories,
                'tags': args.tags,
                'search': args.search,
                'stop_after_duplicates': args.stop_after if not args.no_incremental else 999999,
            }
            
            if args.no_incremental:
                options['existing_ids'] = set()
            
            print(f"\n=== RemoteRadar 开始运行 ===")
            print(f"运行模式: {args.mode}")
            if args.mode == 'api':
                print(f"API 地址: {args.api_url}")
            print(f"爬取目标: {', '.join(args.spiders)}")
            if args.mode == 'local':
                print(f"数据库: {args.db}")
            print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            stats = await radar.run_async(spiders=args.spiders, options=options)
            
            print(f"\n=== 爬取完成 ===")
            print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n结果统计:")
            print(f"  新增职位: {stats['total_new']}")
            print(f"  更新职位: {stats['total_updated']}")
            print(f"\n按网站分布:")
            for source, source_stats in stats['sources'].items():
                print(f"  {source}: 新增 {source_stats['new']}, 更新 {source_stats['updated']}")
            
            if args.mode == 'local':
                db_stats = radar.get_stats()
                print(f"\n数据库总职位数: {db_stats['total_jobs']}")
                
        finally:
            await radar.close()
    
    asyncio.run(run_with_close())


if __name__ == '__main__':
    main()
