<div align="center">
  <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=modern%20radar%20icon%20with%20blue%20and%20green%20colors%2C%20symbolizing%20remote%20work%20job%20search%20platform%2C%20minimalist%20design&image_size=square_hd" alt="RemoteRadar Logo" width="120" height="120">
  <h1>RemoteRadar</h1>
  <p>智能远程工作职位聚合平台</p>
  
  <p>
    <img src="https://img.shields.io/github/stars/your-username/RemoteRadar?style=social" alt="GitHub Stars">
    <img src="https://img.shields.io/github/forks/your-username/RemoteRadar?style=social" alt="GitHub Forks">
    <img src="https://img.shields.io/github/last-commit/your-username/RemoteRadar" alt="Last Commit">
    <img src="https://img.shields.io/github/license/your-username/RemoteRadar" alt="License">
  </p>
  
  <p>
    <a href="#-功能特性">功能特性</a> •
    <a href="#-快速开始">快速开始</a> •
    <a href="#-安装指南">安装指南</a> •
    <a href="#-使用方法">使用方法</a> •
    <a href="#-贡献指南">贡献指南</a>
  </p>
</div>

---

## 🚀 项目简介

**RemoteRadar** 是一个功能强大的远程工作职位聚合平台，它像雷达一样扫描全球知名远程招聘平台，为你发现理想的远程工作机会。

### 🌟 核心优势

- **🔍 多源聚合**：整合 15+ 全球知名远程招聘平台
- **🤖 智能推荐**：基于内容过滤的个性化职位推荐系统
- **👤 个人中心**：技能管理、工作经验记录、职位偏好设置
- **🔐 安全认证**：JWT 认证机制，保护你的数据安全
- **📱 响应式设计**：完美适配桌面和移动设备
- **⏰ 自动更新**：GitHub Actions 定时任务，每 12 小时自动爬取数据

---

## ✨ 功能特性

### 🕷️ 智能爬虫系统

- **多平台支持**：爬取 15+ 知名远程招聘平台，包括 Himalayas、RemoteOK、WeWork Remotely 等
- **丰富数据**：抓取职位名称、公司信息、薪资范围、地点限制、时区要求等完整信息
- **智能去重**：自动识别重复职位，确保数据准确性
- **增量爬取**：遇到已存在职位自动停止，提高效率
- **稳定可靠**：优先使用官方 API，减少因网站改版导致的爬虫失效

### 🤖 个性化推荐系统

- **多维度用户画像**：
  - 技能兴趣分析（从用户行为推断权重）
  - 行业偏好识别（从收藏职位推断）
  - 地点偏好收集（从收藏职位推断）
  - 薪资范围预测（从收藏职位推断）
  - 职级智能推断（从职位标题和标签推断）

- **智能推荐算法**：
  - 内容过滤推荐（Content-based Filtering）
  - TF-IDF + 余弦相似度计算
  - 热门职位回退机制（用户行为不足时）
  - 权重优化：用户主动设置 > 用户技能/经验 > 用户行为推断

### 👤 个人中心系统

- **技能管理**：
  - 添加、编辑、删除个人专业技能
  - 支持熟练度选择（初级/中级/高级/专家）
  - 星级熟练度可视化展示

- **工作经验**：
  - 完整的工作经历记录
  - 公司名称、职位、时间范围
  - 工作描述和主要成就
  - 支持"目前在职"标记

- **职位偏好**：
  - 期望行业（多选）
  - 职位类型选择
  - 薪资范围设置
  - 工作模式偏好（全职/兼职/远程）
  - 仅远程职位选项

### 🔐 用户认证与收藏

- **JWT 认证**：安全的 Bearer Token 认证机制
- **用户注册/登录**：完整的用户身份验证系统
- **职位收藏**：收藏感兴趣的职位，随时查看
- **行为记录**：自动记录用户浏览、点击、收藏等行为，用于个性化推荐

### 🖥️ 现代化 Web 界面

- **双标签页首页**：
  - "全部职位"：浏览所有爬取的职位
  - "为我推荐"：基于用户画像的个性化推荐

- **强大筛选功能**：
  - 按来源筛选（Himalayas、RemoteOK 等）
  - 按时间筛选（今天、本周、本月）
  - 按职位类型筛选
  - 关键词搜索（职位名、公司名、描述）

- **职位详情页**：
  - 完整的职位信息展示
  - 公司信息和 Logo
  - 薪资范围和地点限制
  - 访问公司网站和原职位链接
  - 收藏功能（登录后）

- **响应式设计**：
  - 桌面端：完整功能展示
  - 移动端：优化的触摸体验

---

## 🛠️ 技术架构

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.100+ | Web 框架 |
| SQLite | 3.x | 数据库 |
| aiosqlite | 0.19+ | 异步数据库驱动 |
| Pydantic | 2.x | 数据验证 |
| JWT (python-jose) | 3.x | 身份认证 |
| bcrypt | 4.x | 密码加密 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2+ | UI 框架 |
| TypeScript | 5.2+ | 类型安全 |
| React Router | 6.x | 路由管理 |
| React Context | 18.x | 状态管理 |
| Axios | 1.6+ | HTTP 客户端 |
| Tailwind CSS | 3.4+ | 样式框架 |
| Lucide React | 0.303+ | 图标库 |
| Vite | 5.0+ | 构建工具 |

### 推荐算法

- **算法类型**：内容过滤推荐（Content-based Filtering）
- **特征提取**：TF-IDF 向量化
- **相似度计算**：余弦相似度
- **数据融合**：多源权重优化

---

## 📊 支持的平台

按数据量排序（⭐ 推荐优先使用）：

| 爬虫名称 | 数据源 | 预计数据量 | 特点 |
|---------|--------|-----------|------|
| **Himalayas** ⭐ | 官方 JSON API | **100,000+** | 免费公开API，薪资范围、职级、地点/时区限制 |
| **Arbeitnow** ⭐ | 官方 JSON API | ~200+ | 免费公开API，聚合多源ATS系统 |
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

---

## 🚀 快速开始

### 环境要求

- **Python**：3.8+
- **Node.js**：18+
- **npm** 或 **yarn**

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/RemoteRadar.git
   cd RemoteRadar
   ```

2. **设置 Python 虚拟环境并安装依赖**
   ```bash
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   # macOS/Linux
   source venv/bin/activate
   # Windows
   # venv\Scripts\activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

3. **安装前端依赖**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### 运行项目

#### 方式一：开发模式（推荐）

需要分别启动后端和前端两个终端。

**终端 1 - 启动后端：**
```bash
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

然后访问：
- 前端页面：http://localhost:3001
- API 文档：http://localhost:8000/docs

#### 方式二：生产模式（构建前端）

先构建前端，然后通过 FastAPI 服务静态文件。

```bash
# 构建前端
cd frontend && npm run build && cd ..

# 启动后端
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

然后访问：http://localhost:8000

#### 方式三：先爬取数据

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

## 📖 使用方法

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

### Web 界面功能

#### 首页（双标签页）

**全部职位标签页**：
- 统计栏：显示总职位数和各来源分布
- 筛选面板：
  - 来源筛选：所有来源 / Himalayas / RemoteOK / Arbeitnow 等
  - 时间筛选：今天、本周、本月、全部
  - 职位类型筛选
- 搜索框：支持关键词搜索
- 职位卡片：展示公司 Logo、职位名、公司名、地点、薪资、标签
- 分页：支持页码导航

**为我推荐标签页**：
- 推荐算法根据用户画像和行为推荐
- 访客模式显示登录引导
- 登录后显示个性化推荐

#### 职位详情页

- 完整的职位信息展示
- 公司信息和 Logo
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

## 📊 推荐算法详解

### 用户画像 (UserProfile)

```python
@dataclass
class UserProfile:
    # 从用户行为推断的画像
    skill_interests: Dict[str, float]      # 技能兴趣权重
    category_preferences: Dict[str, float] # 类别偏好
    location_preferences: List[str]         # 地点偏好
    salary_preferences: Dict[str, float]    # 薪资偏好
    seniority: Optional[str]                 # 职级
    
    # 用户主动设置的数据
    skills: List[Dict]          # 用户在个人中心设置的技能
    experiences: List[Dict]     # 用户工作经验
    preferences: Optional[Dict] # 用户工作倾向设置
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

## 🔌 API 接口

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

### API 文档

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/docs` | Swagger API 文档 |
| GET | `/redoc` | ReDoc API 文档 |
| GET | `/openapi.json` | OpenAPI 3.1 规范 |

---

## 📁 项目结构

```
RemoteRadar/
├── .github/
│   └── workflows/
│       └── crawl.yml              # GitHub Actions 定时任务
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 主应用
│   ├── routes.py                  # API 路由
│   ├── schemas.py                 # Pydantic 数据模型
│   ├── database_service.py        # 异步数据库服务
│   ├── auth.py                    # JWT 认证相关
│   └── recommender.py             # 推荐算法
├── frontend/
│   ├── public/
│   │   └── favicon.svg            # 网站图标
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx         # 头部导航
│   │   │   ├── JobCard.tsx        # 职位卡片
│   │   │   ├── Pagination.tsx     # 分页组件
│   │   │   ├── FilterPanel.tsx    # 筛选面板
│   │   │   └── common.tsx         # 通用组件
│   │   ├── pages/
│   │   │   ├── JobsPage.tsx       # 职位列表页
│   │   │   ├── JobDetailPage.tsx  # 职位详情页
│   │   │   ├── SavedJobsPage.tsx  # 我的收藏
│   │   │   ├── ProfilePage.tsx    # 个人中心
│   │   │   ├── LoginPage.tsx      # 登录页
│   │   │   └── RegisterPage.tsx   # 注册页
│   │   ├── services/
│   │   │   └── api.ts             # API 服务封装
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx    # 认证 Context
│   │   ├── types/
│   │   │   └── index.ts           # TypeScript 类型
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
│   └── crawl.sh                   # 运行爬虫
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── job_listing.py         # 数据模型
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py            # SQLite 数据库操作
│   └── spiders/
│       ├── __init__.py
│       ├── himalayas_spider.py    # Himalayas 爬虫
│       ├── arbeitnow_spider.py    # Arbeitnow 爬虫
│       ├── jobicy_spider.py       # Jobicy 爬虫
│       ├── remoteok_spider.py     # RemoteOK 爬虫
│       ├── remotive_spider.py     # Remotive 爬虫
│       ├── v2ex_spider.py         # V2EX 爬虫
│       ├── wework_spider.py       # Wework Remotely 爬虫
│       └── ...                    # 其他爬虫
├── exports/                        # JSON 导出目录
├── jobs.db                         # SQLite 数据库
├── main.py                         # 爬虫主程序
├── requirements.txt                # Python 依赖
├── .gitignore
└── README.md
```

---

## 🗄️ 数据库模型

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
| id | int | 数据库自增 ID |
| source | str | 来源 |
| job_id | str | 职位唯一标识 |
| title | str | 职位名称 |
| company | str | 公司名称 |
| company_url | str | 公司网站 |
| company_logo | str | 公司 Logo URL |
| description | str | 职位描述 |
| location | str | 工作地点 |
| job_type | str | 职位类型/分类 |
| salary | str | 薪资范围 |
| tags | str | 标签（逗号分隔） |
| job_url | str | 职位详情 URL |
| posted_at | datetime | 发布时间 |
| created_at | datetime | 记录创建时间 |
| updated_at | datetime | 记录更新时间 |

---

## ⏰ GitHub Actions 配置

项目已配置好自动定时爬取任务，每 12 小时运行一次。

### 工作流说明

1. **定时触发**：`cron: '0 */12 * * *'` - 每天 00:00 和 12:00 UTC 时间运行
2. **手动触发**：可在 GitHub Actions 页面手动运行，支持选择爬取目标
3. **数据持久化**：每次运行后自动提交数据到仓库

### 启用步骤

1. 将代码推送到 GitHub 仓库
2. 进入仓库 → Settings → Actions → General
3. 确保 "Read and write permissions" 已启用（用于提交数据）
4. 首次运行可以手动触发：Actions → RemoteRadar - 定时爬取 → Run workflow

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论你是想修复 bug、添加新功能、改进文档，还是提出建议，都非常感谢你的参与。

### 如何贡献

1. **Fork 仓库**：点击页面右上角的 Fork 按钮
2. **克隆你的 Fork**：
   ```bash
   git clone https://github.com/your-username/RemoteRadar.git
   cd RemoteRadar
   ```
3. **创建分支**：
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **做出修改**：
   - 确保代码风格一致
   - 添加必要的注释
   - 测试你的修改
5. **提交更改**：
   ```bash
   git add .
   git commit -m "feat: 描述你的修改"
   ```
6. **推送到你的 Fork**：
   ```bash
   git push origin feature/your-feature-name
   ```
7. **创建 Pull Request**：
   - 前往原仓库
   - 点击 "Pull requests" 标签
   - 点击 "New pull request" 按钮
   - 选择你的分支和修改
   - 填写 PR 描述，详细说明你的修改

### 贡献规范

- **代码风格**：遵循现有代码风格
- **提交信息**：使用语义化提交信息
  - `feat:` 新功能
  - `fix:` 修复 bug
  - `docs:` 文档更新
  - `refactor:` 代码重构
  - `test:` 测试相关
  - `chore:` 构建/工具相关

### 开发指南

#### 添加新的爬虫源

1. 在 `src/spiders/` 目录下创建新的 Spider 类（参考现有爬虫）
2. 在 `src/spiders/__init__.py` 中导出
3. 在 `main.py` 中：
   - 添加导入
   - 添加到 `AVAILABLE_SPIDERS` 列表
   - 添加到 `DEFAULT_SPIDERS` 列表（如果是主要数据源）
   - 在 `run_spider` 方法中添加处理逻辑
   - 更新命令行选项的 `choices`
   - 更新帮助文档

#### 自定义前端样式

项目使用 Tailwind CSS 3，配置文件在 `frontend/tailwind.config.js`。

#### API 扩展

在 `api/routes.py` 中添加新的端点，在 `api/schemas.py` 中定义数据模型。

#### 推荐算法扩展

在 `api/recommender.py` 中：
- `UserProfile`：用户画像数据类
- `get_user_or_create()`：获取或创建用户画像
- `calculate_similarity()`：计算用户画像和职位的相似度
- `get_recommendations()`：生成推荐列表
- `record_user_action()`：记录用户行为

---

## 📝 常见问题

### Q: 前端无法连接后端？
A: 确保后端已启动在 8000 端口，前端 `vite.config.ts` 已配置代理。开发模式下前端会自动代理 `/api` 请求到后端。

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
A: 确保设置合理的请求间隔（`--delay` 参数），遵守各网站的 `robots.txt` 和使用条款。主要数据源（Himalayas、Arbeitnow 等）使用官方 API，不会被限制。

---

## ⚠️ 注意事项

1. **爬虫使用限制**：请合理设置请求间隔，遵守各网站的 `robots.txt` 和使用条款
2. **数据准确性**：爬虫依赖网站结构，如果网站改版可能需要更新爬虫。优先使用官方 API 的源更稳定。
3. **CORS 配置**：后端已配置 CORS 白名单，如需添加新域名请修改 `api/main.py`
4. **API 限流**：部分网站（如 Jobicy）有 API 调用频率限制，请注意间隔
5. **推荐数据**：推荐效果取决于用户行为数据量，数据越多推荐越准确。用户在个人中心主动设置的数据具有更高权重。

---

## 🛣️ 路线图

我们计划在未来添加以下功能：

- [ ] **协作过滤推荐**：基于用户相似度的推荐算法
- [ ] **职位订阅**：按条件订阅新职位，邮件通知
- [ ] **多语言支持**：国际化支持
- [ ] **深色模式**：界面主题切换
- [ ] **移动端 App**：React Native 移动端应用
- [ ] **数据分析**：职位市场趋势分析
- [ ] **社区功能**：用户交流、经验分享

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- 感谢所有提供免费 API 的远程招聘平台
- 感谢开源社区提供的优秀工具和库
- 感谢所有为这个项目做出贡献的人

---

<div align="center">
  <p>如果这个项目对你有帮助，请给我们一个 ⭐ Star！</p>
  <p>
    <a href="https://github.com/your-username/RemoteRadar/stargazers">查看星标</a> •
    <a href="https://github.com/your-username/RemoteRadar/issues">报告问题</a> •
    <a href="https://github.com/your-username/RemoteRadar/discussions">讨论交流</a>
  </p>
</div>
