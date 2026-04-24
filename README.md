# RemoteRadar - 远程工作职位爬虫

一个自动爬取远程工作招聘信息的Python程序，支持多个常用远程招聘网站，数据自动存储到SQLite数据库，并支持GitHub Actions定时运行。

## 功能特性

- **多网站支持**：爬取 V2EX、Wework Remotely、RemoteOk 等知名远程招聘平台
- **丰富数据**：抓取公司信息、职位名称、职位描述、发布时间、薪资范围等
- **智能去重**：支持根据来源和职位ID自动去重更新
- **命令行界面**：完整的CLI，支持多种运行模式
- **GitHub Actions**：内置定时任务，每12小时自动运行一次
- **数据持久化**：SQLite数据库 + JSON导出，方便数据消费

## 支持的网站

| 网站 | 数据源 | 特点 |
|------|--------|------|
| **V2EX** | HTML解析 | 国内活跃的远程招聘社区，remote节点 |
| **Wework Remotely** | RSS + HTML解析 | 高质量远程职位，支持分类筛选 |
| **RemoteOk** | API (JSON) | 官方API支持，数据结构清晰 |

## 安装

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. 克隆仓库
```bash
git clone <your-repo-url>
cd RemoteRadar
```

2. 创建虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

#### 爬取所有网站
```bash
python main.py --spiders all
```

#### 爬取特定网站
```bash
# 只爬取 V2EX
python main.py --spiders v2ex

# 爬取多个网站
python main.py --spiders v2ex wework
```

#### 查看统计信息
```bash
python main.py --stats
```

输出示例：
```
=== RemoteRadar 统计信息 ===
总职位数: 156

按来源分布:
  v2ex: 45 个职位
  wework: 68 个职位
  remoteok: 43 个职位

最新10个职位:
  [v2ex] Senior Python Developer (ABC Tech) - 2024-01-15 10:30
  [wework] Frontend Engineer (Remote) - 2024-01-15 09:00
  ...
```

#### 列出最新职位
```bash
# 列出所有来源最新50个职位
python main.py --list

# 只列出 V2EX 的职位
python main.py --list --source v2ex

# 列出100个职位
python main.py --list --limit 100
```

### 高级用法

#### V2EX 高级选项
```bash
# 爬取5页（默认3页）
python main.py --spiders v2ex --max-pages 5

# 不获取详情页，只爬取列表（更快）
python main.py --spiders v2ex --no-details
```

#### Wework Remotely 高级选项
```bash
# 只爬取编程类职位
python main.py --spiders wework --categories programming

# 爬取多个分类
python main.py --spiders wework --categories programming design devops
```

#### RemoteOk 高级选项
```bash
# 最多爬取200个职位（默认100）
python main.py --spiders remoteok --max-jobs 200

# 按标签过滤
python main.py --spiders remoteok --tags python javascript
```

#### 其他选项
```bash
# 指定数据库路径
python main.py --spiders all --db /path/to/my.db

# 设置请求间隔为2秒（默认1秒，避免被封）
python main.py --spiders all --delay 2.0
```

## 项目结构

```
RemoteRadar/
├── .github/
│   └── workflows/
│       └── crawl.yml          # GitHub Actions 定时任务
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── job_listing.py     # 数据模型定义
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py        # SQLite 数据库操作
│   └── spiders/
│       ├── __init__.py
│       ├── v2ex_spider.py     # V2EX 爬虫
│       ├── wework_spider.py   # Wework Remotely 爬虫
│       └── remoteok_spider.py # RemoteOk 爬虫
├── exports/                    # JSON 导出目录 (自动创建)
├── jobs.db                     # SQLite 数据库 (自动创建)
├── main.py                     # 主程序入口
├── requirements.txt            # Python 依赖
├── .gitignore                  # Git 忽略配置
└── README.md                   # 本文档
```

## 数据模型

### JobListing 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 数据库自增ID |
| source | str | 来源 (v2ex/wework/remoteok) |
| job_id | str | 职位唯一标识 |
| title | str | 职位名称 |
| company | str | 公司名称 |
| company_url | str | 公司网站 |
| company_logo | str | 公司Logo URL |
| description | str | 职位描述 |
| location | str | 工作地点 |
| job_type | str | 职位类型/分类 |
| salary | str | 薪资范围 |
| tags | str | 标签 (逗号分隔) |
| job_url | str | 职位详情URL |
| posted_at | datetime | 发布时间 |
| created_at | datetime | 记录创建时间 |
| updated_at | datetime | 记录更新时间 |

## GitHub Actions 配置

项目已配置好自动定时爬取任务，每12小时运行一次。

### 工作流说明

1. **定时触发**：`cron: '0 */12 * * *'` - 每天 00:00 和 12:00 UTC 时间运行
2. **手动触发**：可在 GitHub Actions 页面手动运行，支持选择爬取目标
3. **数据持久化**：每次运行后自动提交 `jobs.db` 和 `exports/` 目录到仓库

### 导出的数据文件

每次运行后会生成以下 JSON 文件：

| 文件 | 说明 |
|------|------|
| `exports/stats.json` | 统计信息（总数量、按来源分布） |
| `exports/latest_jobs.json` | 最新1000个职位详情 |
| `exports/v2ex_jobs.json` | V2EX 来源的职位 |
| `exports/wework_jobs.json` | Wework Remotely 来源的职位 |
| `exports/remoteok_jobs.json` | RemoteOk 来源的职位 |

### 启用 GitHub Actions

1. 将代码推送到 GitHub 仓库
2. 进入仓库 → Settings → Actions → General
3. 确保 "Read and write permissions" 已启用（用于提交数据）
4. （可选）首次运行可以手动触发：Actions → RemoteRadar - 定时爬取 → Run workflow

## 常见问题

### Q: 爬取速度如何调整？
A: 使用 `--delay` 参数调整请求间隔，单位为秒。建议设置 1-2 秒避免被网站限制。

### Q: 数据库可以迁移吗？
A: SQLite 是文件数据库，直接复制 `jobs.db` 文件即可迁移。也可以使用导出的 JSON 文件。

### Q: 如何添加新的爬虫源？
A: 在 `src/spiders/` 目录下创建新的 Spider 类，参考现有爬虫实现，然后在 `src/spiders/__init__.py` 和 `main.py` 中注册。

### Q: 数据会重复吗？
A: 不会。每个职位使用 `(source, job_id)` 作为唯一标识，插入时会自动检测：
- 新职位：直接插入
- 已存在：更新字段并更新 `updated_at` 时间

## 注意事项

1. **使用限制**：请合理设置请求间隔，遵守各网站的 robots.txt 和使用条款
2. **数据准确性**：爬虫依赖网站结构，如果网站改版可能需要更新爬虫
3. **网络环境**：部分网站可能需要代理才能访问，如需代理可在爬虫中添加代理配置

## 扩展建议

- 添加更多爬虫源（如 Stack Overflow Jobs, AngelList 等）
- 添加数据分析和可视化功能
- 添加邮件/消息通知（新职位提醒）
- 部署到云服务器获得更高频率的更新
- 添加 Web 界面展示职位

## 许可证

MIT License
