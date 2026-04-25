import re
from typing import Dict, List, Set


STANDARD_CATEGORIES = {
    "frontend": {
        "name": "前端开发",
        "keywords": [
            "前端", "frontend", "front-end", "前端开发", "ui开发",
            "react", "vue", "angular", "next.js", "nuxt",
            "javascript", "typescript", "js", "ts",
            "html", "css", "sass", "less", "tailwind",
            "webpack", "vite", "css", "移动端h5", "h5开发"
        ],
    },
    "backend": {
        "name": "后端开发",
        "keywords": [
            "后端", "backend", "back-end", "后端开发", "服务端", "服务器端",
            "python", "java", "go", "golang", "rust", "php", "ruby", "c#",
            "django", "flask", "fastapi", "spring", "laravel", "rails",
            "node", "nodejs", "express", "nest",
            "api开发", "接口开发", "中间件", "微服务"
        ],
    },
    "fullstack": {
        "name": "全栈开发",
        "keywords": [
            "全栈", "fullstack", "full stack", "full-stack",
            "全栈工程师", "前后端"
        ],
    },
    "mobile": {
        "name": "移动开发",
        "keywords": [
            "移动端", "移动开发", "ios", "android", "安卓", "苹果",
            "react native", "flutter", "rn", "跨端", "移动端开发",
            "swift", "kotlin", "objective-c", "xamarin", "uni-app"
        ],
    },
    "devops": {
        "name": "运维/DevOps",
        "keywords": [
            "运维", "devops", "sre", "site reliability", "运维工程师",
            "docker", "kubernetes", "k8s", "容器", "云原生",
            "aws", "gcp", "azure", "阿里云", "腾讯云", "云服务",
            "terraform", "ansible", "ci/cd", "jenkins", "github actions",
            "nginx", "监控", "部署", "服务器运维", "系统运维"
        ],
    },
    "design": {
        "name": "设计",
        "keywords": [
            "设计", "designer", "ui", "ux", "ui/ux", "视觉设计",
            "产品设计", "交互设计", "设计师", "平面设计", "figma",
            "sketch", "adobe xd", "photoshop", "ps", "ui设计"
        ],
    },
    "product": {
        "name": "产品",
        "keywords": [
            "产品经理", "product manager", "pm", "产品策划", "产品运营",
            "产品设计师", "需求分析", "产品岗"
        ],
    },
    "data": {
        "name": "数据/AI",
        "keywords": [
            "数据", "data", "数据分析", "数据工程师", "数据分析师",
            "ai", "ml", "机器学习", "machine learning", "深度学习",
            "nlp", "计算机视觉", "cv", "算法", "算法工程师",
            "pytorch", "tensorflow", "langchain", "llm", "大模型",
            "数据科学", "data science", "数据挖掘"
        ],
    },
    "testing": {
        "name": "测试",
        "keywords": [
            "测试", "qa", "quality assurance", "测试工程师", "测试开发",
            "自动化测试", "功能测试", "接口测试", "性能测试",
            "selenium", "appium", "pytest", "测试用例"
        ],
    },
    "security": {
        "name": "安全",
        "keywords": [
            "安全", "security", "信息安全", "网络安全", "渗透测试",
            "安全工程师", "安全研究员", "漏洞", "攻防", "cyber security"
        ],
    },
    "marketing": {
        "name": "营销/运营",
        "keywords": [
            "营销", "marketing", "运营", "市场", "增长", "growth",
            "品牌", "brand", "内容运营", "用户运营", "活动运营",
            "seo", "sem", "社交媒体", "social media", "新媒体"
        ],
    },
    "writing": {
        "name": "内容/写作",
        "keywords": [
            "写作", "writer", "编辑", "editor", "内容", "content",
            "文案", "文案策划", "内容创作", "技术写作", "技术文档"
        ],
    },
    "support": {
        "name": "客服/支持",
        "keywords": [
            "客服", "customer support", "客户支持", "客户成功",
            "customer success", "技术支持", "技术客服", "售后"
        ],
    },
    "sales": {
        "name": "销售",
        "keywords": [
            "销售", "sales", "客户经理", "商务", "bd", "business development",
            "销售经理", "销售代表", "渠道销售"
        ],
    },
    "management": {
        "name": "管理",
        "keywords": [
            "经理", "manager", "总监", "director", "负责人", "lead",
            "cto", "技术负责人", "团队负责人", "vp", "合伙人",
            "founder", "联合创始人"
        ],
    },
}

TECH_STACKS = {
    "python": {
        "name": "Python",
        "keywords": ["python", "django", "flask", "fastapi", "pyramid", "tornado", "scrapy"],
    },
    "javascript": {
        "name": "JavaScript",
        "keywords": ["javascript", "js", "typescript", "ts", "node", "nodejs", "es6"],
    },
    "react": {
        "name": "React",
        "keywords": ["react", "reactjs", "next.js", "nextjs", "gatsby", "react native", "rn"],
    },
    "vue": {
        "name": "Vue",
        "keywords": ["vue", "vuejs", "nuxt", "nuxtjs", "vite"],
    },
    "java": {
        "name": "Java",
        "keywords": ["java", "spring", "spring boot", "springboot", "jvm", "kotlin"],
    },
    "go": {
        "name": "Go",
        "keywords": ["golang", " go ", "go语言", "gin", "echo", "goframe"],
    },
    "rust": {
        "name": "Rust",
        "keywords": ["rust", "rustlang"],
    },
    "php": {
        "name": "PHP",
        "keywords": ["php", "laravel", "symfony", "thinkphp", "yii"],
    },
    "ruby": {
        "name": "Ruby",
        "keywords": ["ruby", "rails", "ruby on rails", "ror"],
    },
    "csharp": {
        "name": "C#",
        "keywords": ["c#", ".net", "dotnet", "asp.net"],
    },
    "typescript": {
        "name": "TypeScript",
        "keywords": ["typescript", "ts"],
    },
    "swift": {
        "name": "Swift",
        "keywords": ["swift", "ios开发"],
    },
    "kotlin": {
        "name": "Kotlin",
        "keywords": ["kotlin", "android开发"],
    },
    "flutter": {
        "name": "Flutter",
        "keywords": ["flutter", "dart"],
    },
    "docker": {
        "name": "Docker",
        "keywords": ["docker", "container", "容器"],
    },
    "kubernetes": {
        "name": "Kubernetes",
        "keywords": ["kubernetes", "k8s", "k3s"],
    },
    "aws": {
        "name": "AWS",
        "keywords": ["aws", "amazon web services", "ec2", "s3"],
    },
    "database": {
        "name": "数据库",
        "keywords": ["mysql", "postgres", "postgresql", "mongodb", "mongo", "redis",
                     "elasticsearch", "sql", "nosql", "sqlite", "oracle", "sql server",
                     "tidb", "polarDB", "tdsql"],
    },
    "ai": {
        "name": "AI/ML",
        "keywords": ["ai", "artificial intelligence", "ml", "machine learning",
                     "深度学习", "deep learning", "nlp", "计算机视觉", "cv",
                     "llm", "gpt", "transformer", "pytorch", "tensorflow",
                     "langchain", "人工智能", "大模型", "算法", "机器学习"],
    },
}

SENIORITY_LEVELS = {
    "intern": {
        "name": "实习",
        "keywords": ["intern", "实习", "internship", "trainee", "在校生", "应届生"],
    },
    "junior": {
        "name": "初级",
        "keywords": ["junior", "初级", "entry level", "入门", "刚毕业", "1-3年", "1-2年"],
    },
    "mid": {
        "name": "中级",
        "keywords": ["mid", "中级", "mid-level", "3-5年", "3年", "4年", "5年", "资深"],
    },
    "senior": {
        "name": "高级",
        "keywords": ["senior", "高级", "sr.", "5+ years", "5年以上", "专家", "高级工程师"],
    },
    "lead": {
        "name": "负责人",
        "keywords": ["lead", "leader", "负责人", "team lead", "技术负责人", "架构师", "architect"],
    },
}


class JobClassifier:
    def __init__(self):
        self._category_patterns: Dict[str, re.Pattern] = {}
        self._tech_patterns: Dict[str, re.Pattern] = {}
        self._seniority_patterns: Dict[str, re.Pattern] = {}
        
        for key, data in STANDARD_CATEGORIES.items():
            pattern = '|'.join([re.escape(k) for k in data['keywords']])
            self._category_patterns[key] = re.compile(pattern, re.IGNORECASE)
        
        for key, data in TECH_STACKS.items():
            pattern = '|'.join([re.escape(k) for k in data['keywords']])
            self._tech_patterns[key] = re.compile(pattern, re.IGNORECASE)
        
        for key, data in SENIORITY_LEVELS.items():
            pattern = '|'.join([re.escape(k) for k in data['keywords']])
            self._seniority_patterns[key] = re.compile(pattern, re.IGNORECASE)
    
    def classify(self, title: str, description: str = "", location: str = "") -> Dict[str, List[str]]:
        combined_text = f"{title} {description} {location}".lower()
        
        categories: Set[str] = set()
        for key, pattern in self._category_patterns.items():
            if pattern.search(combined_text):
                categories.add(key)
        
        if not categories:
            inferred = self._infer_category_from_title(title)
            categories.update(inferred)
        
        tech_stacks: Set[str] = set()
        for key, pattern in self._tech_patterns.items():
            if pattern.search(combined_text):
                tech_stacks.add(key)
        
        if not tech_stacks:
            inferred_tech = self._infer_tech_from_title(title)
            tech_stacks.update(inferred_tech)
        
        seniority: Set[str] = set()
        for key, pattern in self._seniority_patterns.items():
            if pattern.search(combined_text):
                seniority.add(key)
        
        return {
            "categories": [STANDARD_CATEGORIES[k]["name"] for k in categories if k in STANDARD_CATEGORIES],
            "tech_stacks": [TECH_STACKS[k]["name"] for k in tech_stacks if k in TECH_STACKS],
            "seniority": [SENIORITY_LEVELS[k]["name"] for k in seniority if k in SENIORITY_LEVELS],
        }
    
    def _infer_category_from_title(self, title: str) -> Set[str]:
        inferred: Set[str] = set()
        title_lower = title.lower()
        
        if "前端" in title_lower or "front" in title_lower or "ui" in title_lower or "h5" in title_lower:
            inferred.add("frontend")
        
        if "后端" in title_lower or "back" in title_lower or "服务端" in title_lower or "server" in title_lower:
            inferred.add("backend")
        
        if "全栈" in title_lower or "full stack" in title_lower or "fullstack" in title_lower:
            inferred.add("fullstack")
        
        if "移动端" in title_lower or "移动开发" in title_lower or "ios" in title_lower or "android" in title_lower:
            inferred.add("mobile")
        
        if "运维" in title_lower or "devops" in title_lower or "sre" in title_lower:
            inferred.add("devops")
        
        if "设计" in title_lower or "designer" in title_lower or "ui" in title_lower or "ux" in title_lower:
            inferred.add("design")
        
        if "产品经理" in title_lower or "pm" in title_lower or "产品策划" in title_lower:
            inferred.add("product")
        
        if "数据" in title_lower or "算法" in title_lower or "ai" in title_lower or "ml" in title_lower:
            inferred.add("data")
        
        if "测试" in title_lower or "qa" in title_lower:
            inferred.add("testing")
        
        if "安全" in title_lower or "security" in title_lower:
            inferred.add("security")
        
        if "运营" in title_lower or "营销" in title_lower or "市场" in title_lower:
            inferred.add("marketing")
        
        if "经理" in title_lower or "总监" in title_lower or "负责人" in title_lower or "lead" in title_lower:
            inferred.add("management")
        
        return inferred
    
    def _infer_tech_from_title(self, title: str) -> Set[str]:
        inferred: Set[str] = set()
        title_lower = title.lower()
        
        if "python" in title_lower:
            inferred.add("python")
        
        if "java" in title_lower:
            inferred.add("java")
        
        if "golang" in title_lower or " go " in title_lower:
            inferred.add("go")
        
        if "rust" in title_lower:
            inferred.add("rust")
        
        if "php" in title_lower:
            inferred.add("php")
        
        if "react" in title_lower:
            inferred.add("react")
        
        if "vue" in title_lower:
            inferred.add("vue")
        
        if "javascript" in title_lower or "js" in title_lower or "typescript" in title_lower or "ts" in title_lower:
            inferred.add("javascript")
        
        if "flutter" in title_lower:
            inferred.add("flutter")
        
        if "ios" in title_lower:
            inferred.add("swift")
        
        if "android" in title_lower:
            inferred.add("kotlin")
        
        if "运维" in title_lower or "devops" in title_lower:
            inferred.add("docker")
            inferred.add("kubernetes")
        
        if "数据" in title_lower or "算法" in title_lower or "ai" in title_lower or "ml" in title_lower:
            inferred.add("ai")
            inferred.add("python")
        
        if "数据库" in title_lower or "dba" in title_lower:
            inferred.add("database")
        
        return inferred
    
    def get_all_categories(self) -> Dict[str, str]:
        return {k: v["name"] for k, v in STANDARD_CATEGORIES.items()}
    
    def get_all_tech_stacks(self) -> Dict[str, str]:
        return {k: v["name"] for k, v in TECH_STACKS.items()}
    
    def get_all_seniority(self) -> Dict[str, str]:
        return {k: v["name"] for k, v in SENIORITY_LEVELS.items()}


job_classifier = JobClassifier()
