# RemoteRadar - 智能远程工作职位聚合平台

一个完整的远程工作职位抓取和展示平台，包含爬虫、RESTful API、智能推荐系统、个人中心和现代化Web界面。

## 功能特性

### 🕷️ 爬虫功能

- **多网站支持**：爬取 15+ 知名远程招聘平台
- **丰富数据**：抓取公司信息、职位名称、职位描述、发布时间、薪资范围、公司Logo、地点限制、时区限制等
- **智能去重**：支持根据来源和职位ID自动去重更新
- **增量爬取**：遇到连续已存在职位自动停止
- **GitHub Actions**：内置定时任务，每12小时自动运行一次

### 🤖 智能推荐系统

- **内容过滤推荐**：基于职位内容和用户画像进行相似度计算
- **多维度用户画像**：
  - 技能兴趣：从用户行为推断（浏览=1, 点击=2, 收藏=5, 申请=10）
  - 行业偏好：从收藏的职位推断
  - 地点偏好：从收藏的职位推断
  - 薪资范围：从收藏的职位推断
  - 职级推断：从职位标题和标签推断
- **用户显式数据**：支持用户在个人中心设置的技能、工作经验、工作倾向
- **热门推荐回退**：当用户行为不足时推荐热门职位
- **权重优化**：用户主动设置的数据 > 用户技能/经验 > 用户行为推断

### 👤 个人中心系统

- **技能管理**：
  - 添加、编辑、删除个人专业技能
  - 支持技能名称、熟练程度（初级/中级/高级/专家）、获取时间
  - 星级熟练度显示
- **工作经验**：
  - 支持录入工作经历
  - 公司名称、职位、工作时间、主要职责与成就
  - 支持"目前在职"标记
- **工作倾向设置**：
  - 期望行业（多选）
  - 职位类型
  - 薪资范围
  - 工作模式（全职/兼职/远程）
  - 仅远程职位选项

### 🔐 用户认证系统

- **JWT Bearer Token** 认证机制
- **用户注册**：用户名、邮箱、密码
- **用户登录**：邮箱/密码认证，返回 Token
- **Token 持久化**：localStorage 存储
- **API 拦截器**：自动添加认证头

### ❤️ 收藏功能

- **收藏职位**：点击收藏按钮保存感兴趣的职位
- **取消收藏**：随时取消收藏
- **收藏页面**：专门的"我的收藏"页面管理收藏
- **影响推荐**：收藏行为权重是浏览的 5 倍

### 🖥️ Web应用功能

- **双标签页首页**：
  - "全部职位"：所有爬取的职位
  - "为我推荐"：基于用户画像的个性化推荐
- **职位展示**：美观的职位卡片展示，包含完整的职位信息
- **筛选功能**：支持按来源、职位类型、发布时间筛选
- **搜索功能**：支持关键词搜索职位名、公司名、描述
- **分页浏览**：支持多页浏览职位列表
- **实时同步**：前端轮询检查新数据，有更新时自动通知
- **职位详情页**：查看完整的职位描述和公司信息
- **响应式设计**：适配桌面和移动设备

### 🏗️ 技术架构

- **后端**：FastAPI + SQLite + aiosqlite + Pydantic
- **前端**：React 18 + TypeScript + React Router + React Context + Axios + Tailwind CSS + Lucide React
- **推荐算法**：内容过滤推荐（Content-based Filtering）、TF-IDF + 余弦相似度
- **认证**：JWT (python-jose) + bcrypt
- **构建工具**：Vite

---

## 支持的网站

按数据量排序（⭐ 推荐优先使用）：

| 爬虫名称 | 数据源 | 预计数据量 | 特点 |
|---------|--------|-----------|------|
| **Himalayas** ⭐ | 官方 JSON API | **100,000+** | 免费公开API，薪资范围、职级、地点/时区限制 |
| **Arbeitnow** ⭐ | 官方 JSON API | ~200+ | 免费公开API，聚合多源ATS系统（Greenhouse、SmartRecruiters等） |
| **RemoteOK** ⭐ | 官方 JSON API | ~116 | 成熟稳定，官方API支持 |
| **Jobicy** ⭐ | 官方 JSON API | ~100 | 免费API，含详细薪资范围信息 |
| **Empllo** | RSS Feed | ~100 | 远程职位RSS feed |
| **Remotive** | 官方 JSON API | ~20 | 官方API支持，分类清晰 |
| **Wework Remotely** | RSS + HTML解析 | ~少量 | 高质量远程职位 |
| **V2EX** | HTML解析 | ~少量 | 国内活跃的远程招聘社区 |
| **Stack Overflow Jobs** | RSS Feed | - | Stack Overflow 工作板块 |
| **Wellfound** | HTML解析 | - | 原 AngelList |
| **Remote.co** | HTML解析 | - | 远程工作平台 |
| **Working Nomads** | RSS Feed | - | 远程工作聚合 |
| **NoFluffJobs** | HTML解析 | - | 欧洲技术岗位 |
| **JustRemote** | HTML解析 | - | 远程工作平台 |
| **Eleduck (电鸭)** | HTML解析 | - | 中文远程社区，有反爬机制 |

### 数据来源统计（根据最新测试）

```
数据源统计:
├── himalayas: 102,030+ 职位 (主要数据源)
├── arbeitnow: ~100 职位/页，支持分页
├── remoteok: ~116 职位
├── jobicy: ~100 职位
├── empllo: ~100 职位
└── remotive: ~20 职位
```

---

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

---

## 快速开始

### 方式一：开发模式（推荐）

需要分别启动后端和前端两个终端。

**终端1 - 启动后端：**
```bash
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**终端2 - 启动前端：**
```bash
cd frontend && npm run dev
```

然后访问：
- 前端页面：http://localhost:3001
- API文档：http://localhost:8000/docs

### 方式二：生产模式（构建前端）

先构建前端，然后通过 FastAPI 服务静态文件。

```bash
# 构建前端
cd frontend && npm run build && cd ..

# 启动后端
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

然后访问：http://localhost:8000

### 方式三：先爬取数据

如果数据库是空的，可以先运行爬虫：

```bash
# 爬取所有默认网站（推荐）
python main.py --spiders all

# 只爬取特定网站
python main.py --spiders himalayas arbeitnow

# 只爬取主要数据源（数据量最大的）
python main.py --spiders himalayas
```

---

## 使用方法

### 爬虫命令行

```bash
# 查看帮助
python main.py --help

# 爬取所有默认网站
python main.py --spiders all

# 爬取特定网站
python main.py --spiders himalayas

# 爬取多个网站
python main.py --spiders himalayas arbeitnow jobicy

# 查看统计
python main.py --stats

# 列出职位
python main.py --list
python main.py --list --source himalayas
python main.py --list --limit 100

# 增量爬取（遇到连续10个已存在职位停止）
python main.py --spiders all --stop-after 10

# 设置最大页数和职位数
python main.py --spiders all --max-pages 10 --max-jobs 500
```

### Web界面功能

#### 首页（双标签页）

**全部职位标签页**：
- 统计栏：显示总职位数和各来源分布
- 筛选面板：
  - 来源筛选：所有来源 / Himalayas / RemoteOK / Arbeitnow 等
  - 时间筛选：今天、本周、本月、全部
  - 职位类型筛选
- 搜索框：支持关键词搜索
- 职位卡片：展示公司Logo、职位名、公司名、地点、薪资、标签
- 分页：支持页码导航

**为我推荐标签页**：
- 推荐算法根据用户画像和行为推荐
- 访客模式显示登录引导
- 登录后显示个性化推荐

#### 职位详情页

- 完整的职位信息展示
- 公司信息和Logo
- 薪资范围（如果有）
- 地点/时区限制
- 访问公司网站按钮
- 查看原职位按钮
- 收藏按钮（登录后可见）
- 标签展示
- 详细描述
- 发布/更新时间

#### 个人中心

**技能管理**：
- 添加新技能
- 编辑现有技能
- 删除技能
- 熟练度选择：初级 / 中级 / 高级 / 专家
- 开始学习时间（可选）

**工作经验**：
- 添加工作经历
- 公司名称、职位
- 开始时间、结束时间
- "目前在职"选项
- 工作描述
- 主要成就

**工作倾向设置**：
- 期望行业（多选）：Developer / Design / Marketing / Sales / Product / Data / DevOps / Finance / Operations
- 期望薪资范围
- 工作模式：不限 / 全职 / 兼职 / 合同 / 仅远程
- 仅搜索远程职位复选框

#### 用户菜单

登录后右上角头像下拉菜单：
- **个人中心**：技能/经验/倾向管理
- **我的收藏**：查看收藏的职位
- **退出登录**：清除 Token

---

## 推荐算法

### 用户画像 UserProfile

```python
@dataclass
class UserProfile:
    skill_interests: Dict[str, float]  # 技能兴趣权重
    category_preferences: Dict[str, float]  # 类别偏好
    location_preferences: List[str]  # 地点偏好
    salary_preferences: Dict[str, float]  # 薪资偏好
    seniority: Optional[str]  # 职级 (Entry/Mid/Senior/Manager/Executive)
    
    # 新增：用户显式设置的数据
    skills: List[Dict]  # 用户在个人中心设置的技能
    experiences: List[Dict]  # 用户工作经验
    preferences: Optional[Dict]  # 用户工作倾向设置
```

### 推荐流程

```
用户行为 → 用户画像 ← 用户主动设置（个人中心）
     │              │
     └──────┬───────┘
            ▼
    ┌───────────────┐
    │  相似度计算    │
    │  (技能/类别/  │
    │   地点/薪资)  │
    └───────┬───────┘
            ▼
    ┌───────────────┐
    │  热门职位回退  │
    │  (行为不足时) │
    └───────┬───────┘
            ▼
    ┌───────────────┐
    │  推荐职位列表  │
    └───────────────┘
```

### 行为权重

| 行为类型 | 权重 | 说明 |
|---------|------|------|
| 浏览 | 1 | 查看职位列表 |
| 点击 | 2 | 查看职位详情 |
| 收藏 | 5 | 收藏职位 |
| 申请 | 10 | 申请职位（预留） |

### 显式数据权重

用户在个人中心主动设置的数据具有更高权重：

| 数据来源 | 匹配权重 | 说明 |
|---------|---------|------|
| **技能** | 初级×1.5, 中级×3, 高级×4.5, 专家×6 | 技能熟练度越高，权重越大 |
| **工作经验** | ~×2 | 职位类型关键词匹配 |
| **工作倾向 - 期望行业** | ×4 | 行业匹配权重最高 |
| **工作倾向 - 职位类型** | ×2 | 职位类型匹配 |
| **工作倾向 - 远程优先** | ×3 | 仅远程职位设置 |

---

## API 接口

### 职位相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/jobs` | 获取职位列表（支持筛选、分页、搜索） |
| GET | `/api/jobs/{id}` | 获取单个职位详情 |
| GET | `/api/stats` | 获取统计信息 |
| GET | `/api/filters` | 获取筛选选项 |
| GET | `/api/health` | 健康检查 |

### 推荐相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/recommendations` | 获取推荐职位 |
| POST | `/api/recommendations/refresh` | 刷新推荐 |
| GET | `/api/recommendations/profile` | 获取用户画像（推断） |
| POST | `/api/actions` | 记录用户行为 |

### 用户认证相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录（返回 JWT Token） |
| GET | `/api/auth/me` | 获取当前用户信息 |

### 收藏相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/jobs/save` | 收藏/取消收藏职位 |
| GET | `/api/jobs/saved` | 获取收藏的职位列表 |

### 个人中心相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/profile/me` | 获取完整个人资料（技能+经验+倾向） |

**技能管理**：
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/profile/skills` | 获取技能列表 |
| POST | `/api/profile/skills` | 添加新技能 |
| PUT | `/api/profile/skills/{id}` | 更新技能 |
| DELETE | `/api/profile/skills/{id}` | 删除技能 |

**工作经验管理**：
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/profile/experiences` | 获取工作经验列表 |
| POST | `/api/profile/experiences` | 添加工作经验 |
| PUT | `/api/profile/experiences/{id}` | 更新工作经验 |
| DELETE | `/api/profile/experiences/{id}` | 删除工作经验 |

**工作倾向管理**：
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/profile/preferences` | 获取工作倾向设置 |
| PUT | `/api/profile/preferences` | 更新工作倾向设置 |

### 文档

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/docs` | Swagger API文档 |
| GET | `/redoc` | ReDoc API文档 |
| GET | `/openapi.json` | OpenAPI 3.1 规范 |

---

## 项目结构

```
RemoteRadar/
├── .github/
│   └── workflows/
│       └── crawl.yml              # GitHub Actions 定时任务
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 主应用
│   ├── routes.py                  # API 路由（职位/推荐/认证/收藏/个人中心）
│   ├── schemas.py                 # Pydantic 数据模型
│   ├── database_service.py        # 异步数据库服务
│   ├── auth.py                    # JWT 认证相关
│   └── recommender.py             # 推荐算法（内容过滤、用户画像）
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx         # 头部导航（含用户菜单）
│   │   │   ├── JobCard.tsx        # 职位卡片（含收藏按钮）
│   │   │   ├── Pagination.tsx     # 分页组件
│   │   │   ├── FilterPanel.tsx    # 筛选面板
│   │   │   └── common.tsx         # 通用组件（加载、空状态等）
│   │   ├── pages/
│   │   │   ├── JobsPage.tsx       # 职位列表页（双标签页：全部/推荐）
│   │   │   ├── JobDetailPage.tsx  # 职位详情页
│   │   │   ├── SavedJobsPage.tsx  # 我的收藏页面
│   │   │   ├── ProfilePage.tsx    # 个人中心页面（技能/经验/倾向）
│   │   │   ├── LoginPage.tsx      # 登录页面
│   │   │   └── RegisterPage.tsx   # 注册页面
│   │   ├── services/
│   │   │   └── api.ts             # API 服务封装
│   │   ├── context/
│   │   │   └── AuthContext.tsx    # 认证 Context
│   │   ├── types/
│   │   │   └── index.ts           # TypeScript 类型定义
│   │   ├── router.tsx             # 路由配置
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
├── scripts/
│   ├── start-backend.sh           # 启动后端
│   ├── start-frontend.sh          # 启动前端
│   ├── build-frontend.sh          # 构建前端
│   └── crawl.sh                    # 运行爬虫
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── job_listing.py         # 数据模型
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py            # SQLite 数据库操作（同步）
│   └── spiders/
│       ├── __init__.py
│       ├── himalayas_spider.py    # Himalayas 爬虫（JSON API，10万+）
│       ├── arbeitnow_spider.py    # Arbeitnow 爬虫（JSON API）
│       ├── jobicy_spider.py       # Jobicy 爬虫（JSON API）
│       ├── empllo_spider.py       # Empllo 爬虫（RSS Feed）
│       ├── remoteok_spider.py     # RemoteOK 爬虫
│       ├── remotive_spider.py     # Remotive 爬虫
│       ├── wework_spider.py       # Wework Remotely 爬虫
│       ├── v2ex_spider.py         # V2EX 爬虫
│       ├── stackoverflow_spider.py# Stack Overflow 爬虫
│       ├── wellfound_spider.py    # Wellfound 爬虫
│       ├── remoteco_spider.py     # Remote.co 爬虫
│       ├── workingnomads_spider.py# Working Nomads 爬虫
│       ├── nofluffjobs_spider.py  # NoFluffJobs 爬虫
│       ├── justremote_spider.py   # JustRemote 爬虫
│       └── eluduck_spider.py      # 电鸭社区爬虫
├── exports/                        # JSON 导出目录
│   ├── stats.json                  # 统计信息
│   └── ...                         # 各源导出数据
├── jobs.db                         # SQLite 数据库
├── main.py                         # 爬虫主程序
├── requirements.txt                # Python 依赖
├── .gitignore
└── README.md
```

---

## 数据库模型

### 核心表

| 表名 | 说明 |
|------|------|
| `jobs` | 职位列表（主表） |
| `users` | 用户表 |
| `saved_jobs` | 用户收藏关系表 |
| `user_actions` | 用户行为记录表 |
| `user_skills` | 用户技能表（个人中心） |
| `user_experiences` | 用户工作经验表（个人中心） |
| `user_preferences` | 用户工作倾向表（个人中心） |

### JobListing 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 数据库自增ID |
| source | str | 来源 |
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

### 用户相关表

**user_skills (技能管理)**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| user_id | int | 用户ID |
| skill_name | str | 技能名称 |
| proficiency | str | 熟练程度 (beginner/intermediate/advanced/expert) |
| acquired_date | date | 开始学习日期 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

**user_experiences (工作经验)**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| user_id | int | 用户ID |
| company | str | 公司名称 |
| position | str | 职位 |
| start_date | date | 开始时间 |
| end_date | date | 结束时间 |
| current | bool | 是否在职 |
| description | text | 工作描述 |
| achievements | text | 主要成就 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

**user_preferences (工作倾向)**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| user_id | int | 用户ID |
| preferred_industries | str | 期望行业 (逗号分隔) |
| preferred_job_types | str | 期望职位类型 |
| preferred_locations | str | 期望地点 (逗号分隔) |
| min_salary | int | 最低薪资 |
| max_salary | int | 最高薪资 |
| work_mode | str | 工作模式 |
| remote_only | bool | 仅远程职位 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

---

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

---

## 开发指南

### 添加新的爬虫源

1. 在 `src/spiders/` 目录下创建新的 Spider 类（参考现有爬虫）
2. 在 `src/spiders/__init__.py` 中导出
3. 在 `main.py` 中：
   - 添加导入
   - 添加到 `AVAILABLE_SPIDERS` 列表
   - 添加到 `DEFAULT_SPIDERS` 列表（如果是主要数据源）
   - 在 `run_spider` 方法中添加处理逻辑
   - 更新命令行选项的 `choices`
   - 更新帮助文档

### 自定义前端样式

项目使用 Tailwind CSS 4，配置文件在 `frontend/tailwind.config.js`。

### API 扩展

在 `api/routes.py` 中添加新的端点，在 `api/schemas.py` 中定义数据模型。

### 推荐算法扩展

在 `api/recommender.py` 中：
- `UserProfile`：用户画像数据类
- `get_user_or_create()`：获取或创建用户画像
- `calculate_similarity()`：计算用户画像和职位的相似度
- `get_recommendations()`：生成推荐列表
- `record_user_action()`：记录用户行为

---

## 常见问题

### Q: 前端无法连接后端？
A: 确保后端已启动在 8000 端口，前端 vite.config.ts 已配置代理。开发模式下前端会自动代理 `/api` 请求到后端。

### Q: 数据库为空？
A: 先运行爬虫 `python main.py --spiders all` 或等待 GitHub Actions 定时任务执行。主要数据源是 Himalayas（10万+ 职位）。

### Q: 推荐不工作？
A: 推荐系统需要用户行为或用户在个人中心设置数据：
1. 登录账号
2. 浏览/收藏一些职位（行为推断）
3. 或在"个人中心"设置技能、工作经验、工作倾向（显式数据）

### Q: 如何修改轮询间隔？
A: 在 `frontend/src/pages/JobsPage.tsx` 中修改 `POLL_INTERVAL` 常量（毫秒）。

### Q: 如何添加新的筛选条件？
A: 修改以下位置：
1. `api/routes.py` - 添加新的查询参数
2. `api/database_service.py` - 添加数据库筛选逻辑
3. `frontend/src/components/FilterPanel.tsx` - 添加 UI 组件
4. `frontend/src/pages/JobsPage.tsx` - 处理新参数

### Q: 爬虫被限制？
A: 确保设置合理的请求间隔（`--delay` 参数），遵守各网站的 robots.txt 和使用条款。主要数据源（Himalayas、Arbeitnow 等）使用官方 API，不会被限制。

---

## 注意事项

1. **爬虫使用限制**：请合理设置请求间隔，遵守各网站的 robots.txt 和使用条款
2. **数据准确性**：爬虫依赖网站结构，如果网站改版可能需要更新爬虫。优先使用官方 API 的源更稳定。
3. **CORS 配置**：后端已配置 CORS 白名单，如需添加新域名请修改 `api/main.py`
4. **API 限流**：部分网站（如 Jobicy）有 API 调用频率限制，请注意间隔
5. **推荐数据**：推荐效果取决于用户行为数据量，数据越多推荐越准确。用户在个人中心主动设置的数据具有更高权重。

---

## 许可证

MIT License
