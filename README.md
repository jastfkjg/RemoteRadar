<div align="center">
  <img src="./logo.svg" alt="RemoteRadar Logo" width="120" height="120">
  <h1>RemoteRadar</h1>
  <p>智能远程工作职位聚合平台</p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React">
    <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS">
  </p>
  
  <p>
    <a href="#-功能特性">功能特性</a> •
    <a href="#-快速开始">快速开始</a> •
    <a href="#-安装指南">安装指南</a> •
    <a href="#-使用方法">使用方法</a> •
    <a href="#-许可证">许可证</a>
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
- 爬取 15+ 知名远程招聘平台
- 智能去重与增量爬取
- 优先使用官方 API，稳定可靠

### 🤖 个性化推荐系统
- 多维度用户画像分析
- 内容过滤推荐算法
- 权重优化：用户主动设置 > 用户技能/经验 > 用户行为推断

### 👤 个人中心系统
- 技能管理（支持熟练度选择）
- 工作经验记录
- 职位偏好设置

### 🔐 用户认证与收藏
- JWT 认证机制
- 用户注册/登录
- 职位收藏功能
- 行为记录用于个性化推荐

### 🖥️ 现代化 Web 界面
- 双标签页首页（全部职位 / 为我推荐）
- 强大筛选功能（来源、时间、职位类型、关键词搜索）
- 职位详情页
- 响应式设计

---

## 🛠️ 技术架构

### 后端技术栈
- **FastAPI**：Web 框架
- **SQLite**：数据库
- **Pydantic**：数据验证
- **JWT**：身份认证

### 前端技术栈
- **React 18**：UI 框架
- **TypeScript**：类型安全
- **React Router**：路由管理
- **Axios**：HTTP 客户端
- **Tailwind CSS**：样式框架
- **Lucide React**：图标库
- **Vite**：构建工具

### 推荐算法
- **算法类型**：内容过滤推荐（Content-based Filtering）
- **特征提取**：TF-IDF 向量化
- **相似度计算**：余弦相似度

---

## 📊 支持的平台

主要数据源（按数据量排序）：
- **Himalayas** ⭐：100,000+ 职位，官方 JSON API
- **Arbeitnow** ⭐：~200+ 职位，官方 JSON API
- **RemoteOK** ⭐：~116 职位，官方 JSON API
- **Jobicy** ⭐：~100 职位，官方 JSON API
- **Empllo**：~100 职位，RSS Feed
- **Remotive**：~20 职位，官方 JSON API
- 以及其他 9 个远程招聘平台

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
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate  # Windows
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

访问地址：
- 前端页面：http://localhost:3001
- API 文档：http://localhost:8000/docs

#### 方式二：先爬取数据

如果数据库是空的，可以先运行爬虫：
```bash
# 爬取所有默认网站（推荐）
python main.py --spiders all

# 只爬取主要数据源
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

# 查看统计
python main.py --stats

# 列出职位
python main.py --list
```

### Web 界面功能
- **首页**：双标签页（全部职位 / 为我推荐）
- **筛选功能**：按来源、时间、职位类型筛选，关键词搜索
- **职位详情**：完整的职位信息展示
- **个人中心**：技能管理、工作经验、职位偏好
- **收藏功能**：收藏感兴趣的职位

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

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
4. **做出修改**：确保代码风格一致，测试你的修改
5. **提交更改**：
   ```bash
   git add .
   git commit -m "feat: 描述你的修改"
   ```
6. **推送到你的 Fork**：
   ```bash
   git push origin feature/your-feature-name
   ```
7. **创建 Pull Request**

### 提交信息规范
- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

---

## 📝 常见问题

**Q: 前端无法连接后端？**
A: 确保后端已启动在 8000 端口，开发模式下前端会自动代理 `/api` 请求到后端。

**Q: 数据库为空？**
A: 先运行爬虫 `python main.py --spiders all`，主要数据源是 Himalayas（10万+ 职位）。

**Q: 推荐不工作？**
A: 推荐系统需要用户行为或在个人中心设置数据（登录账号、浏览/收藏职位、设置技能/经验/倾向）。

---

## ⚠️ 注意事项

1. **爬虫使用限制**：请合理设置请求间隔，遵守各网站的 `robots.txt` 和使用条款
2. **数据准确性**：爬虫依赖网站结构，如果网站改版可能需要更新爬虫
3. **API 限流**：部分网站有 API 调用频率限制，请注意间隔

---

## 🛣️ 路线图

我们计划在未来添加以下功能：
- [ ] 协作过滤推荐算法
- [ ] 职位订阅与邮件通知
- [ ] 多语言支持
- [ ] 深色模式
- [ ] 数据分析与市场趋势
- [ ] 社区功能

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

<div align="center">
  <p>如果这个项目对你有帮助，请给我们一个 ⭐ Star！</p>
</div>
