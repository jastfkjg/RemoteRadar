# RemoteRadar - 远程工作职位聚合平台

一个完整的远程工作职位抓取和展示平台，包含爬虫、RESTful API和现代化Web界面。

## 功能特性

### 爬虫功能
- **多网站支持**：爬取 V2EX、Wework Remotely、RemoteOk 等知名远程招聘平台
- **丰富数据**：抓取公司信息、职位名称、职位描述、发布时间、薪资范围等
- **智能去重**：支持根据来源和职位ID自动去重更新
- **GitHub Actions**：内置定时任务，每12小时自动运行一次

### Web应用功能
- **工作展示系统**：美观的职位卡片展示，包含完整的职位信息
- **筛选功能**：支持按来源、职位类型、发布时间筛选
- **搜索功能**：支持关键词搜索职位名、公司名、描述
- **分页浏览**：支持多页浏览职位列表
- **实时同步**：前端轮询检查新数据，有更新时自动通知
- **职位详情页**：查看完整的职位描述和公司信息

### 技术架构
- **后端**：FastAPI + SQLite
- **前端**：React 18 + TypeScript + Tailwind CSS
- **构建工具**：Vite

## 支持的网站

| 网站 | 数据源 | 特点 |
|------|--------|------|
| **V2EX** | HTML解析 | 国内活跃的远程招聘社区，remote节点 |
| **Wework Remotely** | RSS + HTML解析 | 高质量远程职位，支持分类筛选 |
| **RemoteOk** | API (JSON) | 官方API支持，数据结构清晰 |

## 安装

### 环境要求

- Python 3.8+
- Node.js 18+
- npm 或 yarn

### 安装步骤

1. 克隆仓库
```bash
git clone <your-repo-url>
cd RemoteRadar
```

2. 安装 Python 依赖
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
cd ..
```

## 快速开始

### 方式一：开发模式（推荐）

需要分别启动后端和前端两个终端。

**终端1 - 启动后端：**
```bash
source venv/bin/activate
./scripts/start-backend.sh
# 或
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**终端2 - 启动前端：**
```bash
./scripts/start-frontend.sh
# 或
cd frontend && npm run dev
```

然后访问：
- 前端页面：http://localhost:3000
- API文档：http://localhost:8000/docs

### 方式二：生产模式（构建前端）

先构建前端，然后通过 FastAPI 服务静态文件。

```bash
# 构建前端
./scripts/build-frontend.sh
# 或
cd frontend && npm run build

# 启动后端
./scripts/start-backend.sh
```

然后访问：http://localhost:8000

### 方式三：先爬取数据

如果数据库是空的，可以先运行爬虫：

```bash
./scripts/crawl.sh
# 或
python main.py --spiders all
```

## 使用方法

### 爬虫命令行

```bash
# 爬取所有网站
python main.py --spiders all

# 爬取特定网站
python main.py --spiders v2ex

# 查看统计
python main.py --stats

# 列出职位
python main.py --list
python main.py --list --source v2ex
```

### Web界面功能

#### 职位列表页
- **统计栏**：显示总职位数和各来源分布
- **筛选面板**：
  - 来源筛选：V2EX、Wework、RemoteOk
  - 时间筛选：今天、本周、本月、全部
  - 职位类型筛选
- **搜索框**：支持关键词搜索
- **职位卡片**：展示公司Logo、职位名、公司名、地点、薪资、标签
- **分页**：支持页码导航

#### 职位详情页
- 完整的职位信息展示
- 公司信息和Logo
- 访问公司网站按钮
- 查看原职位按钮
- 标签展示
- 详细描述
- 发布/更新时间

#### 实时同步
- 前端每30秒自动检查新数据
- 有新数据时显示通知栏
- 点击通知刷新页面

### API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/jobs` | 获取职位列表（支持筛选、分页、搜索） |
| GET | `/api/jobs/{id}` | 获取单个职位详情 |
| GET | `/api/stats` | 获取统计信息 |
| GET | `/api/filters` | 获取筛选选项 |
| GET | `/api/health` | 健康检查 |
| GET | `/docs` | Swagger API文档 |
| GET | `/redoc` | ReDoc API文档 |

#### `/api/jobs` 查询参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码，默认1 |
| `page_size` | int | 每页数量，默认20，最大100 |
| `source` | string | 筛选来源 (v2ex, wework, remoteok) |
| `job_type` | string | 筛选职位类型 |
| `days_ago` | int | 筛选最近N天内的职位 |
| `search` | string | 搜索关键词 |
| `sort_by` | string | 排序字段 (posted_at, created_at, updated_at, title, company) |
| `sort_order` | string | 排序方式 (asc, desc) |

## 项目结构

```
RemoteRadar/
├── .github/
│   └── workflows/
│       └── crawl.yml              # GitHub Actions 定时任务
├── api/
│   ├── __init__.py
│   ├── main.py                     # FastAPI 主应用
│   ├── routes.py                   # API 路由
│   ├── schemas.py                  # Pydantic 数据模型
│   └── database_service.py         # 异步数据库服务
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx          # 头部导航
│   │   │   ├── JobCard.tsx         # 职位卡片
│   │   │   ├── Pagination.tsx      # 分页组件
│   │   │   ├── FilterPanel.tsx     # 筛选面板
│   │   │   └── common.tsx          # 通用组件（加载、空状态等）
│   │   ├── pages/
│   │   │   ├── JobsPage.tsx        # 职位列表页
│   │   │   └── JobDetailPage.tsx   # 职位详情页
│   │   ├── services/
│   │   │   └── api.ts              # API 服务封装
│   │   ├── types/
│   │   │   └── index.ts            # TypeScript 类型定义
│   │   ├── router.tsx              # 路由配置
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
├── scripts/
│   ├── start-backend.sh            # 启动后端
│   ├── start-frontend.sh           # 启动前端
│   ├── build-frontend.sh           # 构建前端
│   └── crawl.sh                    # 运行爬虫
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── job_listing.py          # 数据模型
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py             # SQLite 数据库操作（同步）
│   └── spiders/
│       ├── __init__.py
│       ├── v2ex_spider.py          # V2EX 爬虫
│       ├── wework_spider.py        # Wework Remotely 爬虫
│       └── remoteok_spider.py      # RemoteOk 爬虫
├── exports/                        # JSON 导出目录
├── jobs.db                         # SQLite 数据库
├── main.py                         # 爬虫主程序
├── requirements.txt                # Python 依赖
├── .gitignore
└── README.md
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

### 启用步骤

1. 将代码推送到 GitHub 仓库
2. 进入仓库 → Settings → Actions → General
3. 确保 "Read and write permissions" 已启用（用于提交数据）
4. 首次运行可以手动触发：Actions → RemoteRadar - 定时爬取 → Run workflow

## 开发指南

### 添加新的爬虫源

1. 在 `src/spiders/` 目录下创建新的 Spider 类（参考现有爬虫）
2. 在 `src/spiders/__init__.py` 中导出
3. 在 `main.py` 中注册到可用爬虫列表

### 自定义前端样式

项目使用 Tailwind CSS 4，配置文件在 `frontend/tailwind.config.js`。

### API 扩展

在 `api/routes.py` 中添加新的端点，在 `api/schemas.py` 中定义数据模型。

## 常见问题

### Q: 前端无法连接后端？
A: 确保后端已启动在 8000 端口，前端 vite.config.ts 已配置代理。开发模式下前端会自动代理 `/api` 请求到后端。

### Q: 数据库为空？
A: 先运行爬虫 `python main.py --spiders all` 或等待 GitHub Actions 定时任务执行。

### Q: 如何修改轮询间隔？
A: 在 `frontend/src/pages/JobsPage.tsx` 中修改 `POLL_INTERVAL` 常量（毫秒）。

### Q: 如何添加新的筛选条件？
A: 修改以下位置：
1. `api/routes.py` - 添加新的查询参数
2. `api/database_service.py` - 添加数据库筛选逻辑
3. `frontend/src/components/FilterPanel.tsx` - 添加 UI 组件
4. `frontend/src/pages/JobsPage.tsx` - 处理新参数

## 注意事项

1. **爬虫使用限制**：请合理设置请求间隔，遵守各网站的 robots.txt 和使用条款
2. **数据准确性**：爬虫依赖网站结构，如果网站改版可能需要更新爬虫
3. **CORS 配置**：后端已配置 CORS 白名单，如需添加新域名请修改 `api/main.py`

## 许可证

MIT License
