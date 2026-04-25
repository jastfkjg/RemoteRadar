import re
from typing import Dict, List, Set, Optional


ROLE_KEYWORDS = {
    "frontend": {
        "name": "前端开发",
        "patterns": [
            r"\b前端开发工程师\b", r"\b前端工程师\b", r"\b前端开发\b", 
            r"\bui开发工程师\b", r"\bui工程师\b", r"\bh5开发\b",
            r"\bFrontend Developer\b", r"\bFrontend Engineer\b", 
            r"\bFront-end Developer\b", r"\bFront-end Engineer\b",
            r"\bFront End Developer\b", r"\bFront End Engineer\b",
            r"\bUI Developer\b", r"\bUI Engineer\b",
        ],
        "tech_hints": ["react", "vue", "angular", "next.js", "typescript", "javascript"],
    },
    "backend": {
        "name": "后端开发",
        "patterns": [
            r"\b后端开发工程师\b", r"\b后端工程师\b", r"\b后端开发\b",
            r"\b服务端开发\b", r"\b服务器端开发\b", r"\b接口开发\b",
            r"\bBackend Developer\b", r"\bBackend Engineer\b",
            r"\bBack-end Developer\b", r"\bBack-end Engineer\b",
            r"\bBack End Developer\b", r"\bBack End Engineer\b",
            r"\bServer Developer\b", r"\bAPI Developer\b",
        ],
        "tech_hints": ["python", "java", "golang", "rust", "php", "ruby", "node.js"],
    },
    "fullstack": {
        "name": "全栈开发",
        "patterns": [
            r"\b全栈开发工程师\b", r"\b全栈工程师\b", r"\b全栈开发\b", r"\b全栈\b",
            r"\b前后端开发\b",
            r"\bFull Stack Developer\b", r"\bFull-Stack Developer\b",
            r"\bFull Stack Engineer\b", r"\bFull-Stack Engineer\b",
            r"\bFullstack Developer\b",
        ],
        "tech_hints": [],
    },
    "mobile": {
        "name": "移动开发",
        "patterns": [
            r"\b移动端开发工程师\b", r"\b移动端工程师\b", r"\b移动开发\b", r"\b移动端\b",
            r"\bios开发工程师\b", r"\bandroid开发工程师\b",
            r"\bMobile Developer\b", r"\bMobile Engineer\b",
            r"\biOS Developer\b", r"\biOS Engineer\b",
            r"\bAndroid Developer\b", r"\bAndroid Engineer\b",
        ],
        "tech_hints": ["ios", "android", "swift", "kotlin", "flutter", "react native"],
    },
    "devops": {
        "name": "运维/DevOps",
        "patterns": [
            r"\b运维工程师\b", r"\bdevops工程师\b", r"\bsre工程师\b",
            r"\b系统运维\b", r"\b服务器运维\b", r"\b云原生\b",
            r"\bDevOps Engineer\b", r"\bSRE Engineer\b",
            r"\bSite Reliability Engineer\b", r"\bOperations Engineer\b",
            r"\bInfrastructure Engineer\b", r"\bCloud Engineer\b",
            r"\bPlatform Engineer\b",
        ],
        "tech_hints": ["docker", "kubernetes", "k8s", "aws", "gcp", "azure", "terraform"],
    },
    "design": {
        "name": "设计",
        "patterns": [
            r"\b设计师\b", r"\bui设计师\b", r"\bux设计师\b",
            r"\b产品设计师\b", r"\b交互设计师\b", r"\b视觉设计师\b",
            r"\bDesigner\b", r"\bUI Designer\b", r"\bUX Designer\b",
            r"\bProduct Designer\b", r"\bVisual Designer\b",
            r"\bInteraction Designer\b",
        ],
        "tech_hints": ["figma", "sketch", "photoshop", "adobe xd"],
    },
    "product": {
        "name": "产品",
        "patterns": [
            r"\b产品经理\b", r"\b产品策划\b", r"\b产品运营\b",
            r"\bProduct Manager\b", r"\bPM\b", r"\bProduct Owner\b",
        ],
        "tech_hints": [],
    },
    "data": {
        "name": "数据/AI",
        "patterns": [
            r"\b数据工程师\b", r"\b数据分析师\b", r"\b算法工程师\b",
            r"\bai工程师\b", r"\b机器学习工程师\b", r"\b数据科学家\b",
            r"\bData Engineer\b", r"\bData Analyst\b", r"\bData Scientist\b",
            r"\bML Engineer\b", r"\bMachine Learning Engineer\b",
            r"\bAI Engineer\b", r"\bAlgorithm Engineer\b",
        ],
        "tech_hints": ["pytorch", "tensorflow", "langchain", "llm", "gpt", "机器学习", "深度学习"],
    },
    "testing": {
        "name": "测试",
        "patterns": [
            r"\b测试工程师\b", r"\bqa工程师\b", r"\b测试开发工程师\b",
            r"\b自动化测试\b", r"\b功能测试\b", r"\b接口测试\b",
            r"\bTest Engineer\b", r"\bQA Engineer\b",
            r"\bQuality Assurance Engineer\b", r"\bSDET\b",
            r"\bSoftware Developer in Test\b", r"\bAutomation Engineer\b",
        ],
        "tech_hints": ["selenium", "appium", "pytest", "cypress"],
    },
    "security": {
        "name": "安全",
        "patterns": [
            r"\b安全工程师\b", r"\b安全研究员\b", r"\b渗透测试工程师\b",
            r"\b信息安全\b", r"\b网络安全\b",
            r"\bSecurity Engineer\b", r"\bSecurity Researcher\b",
            r"\bPenetration Tester\b", r"\bInformation Security\b",
            r"\bCyber Security\b",
        ],
        "tech_hints": [],
    },
    "marketing": {
        "name": "营销/运营",
        "patterns": [
            r"\b营销经理\b", r"\b市场经理\b", r"\b运营经理\b",
            r"\b内容运营\b", r"\b用户运营\b", r"\b活动运营\b",
            r"\b新媒体运营\b", r"\b增长\b", r"\bseo\b", r"\bsem\b",
            r"\bMarketing Manager\b", r"\bMarketing Specialist\b",
            r"\bGrowth Hacker\b", r"\bBrand Manager\b",
        ],
        "tech_hints": [],
    },
    "writing": {
        "name": "内容/写作",
        "patterns": [
            r"\b内容编辑\b", r"\b文案策划\b", r"\b技术写作\b",
            r"\bContent Writer\b", r"\bTechnical Writer\b",
            r"\bCopywriter\b", r"\bEditor\b",
        ],
        "tech_hints": [],
    },
    "support": {
        "name": "客服/支持",
        "patterns": [
            r"\b客户支持\b", r"\b技术支持\b", r"\b客服专员\b",
            r"\bCustomer Support\b", r"\bTechnical Support\b",
            r"\bSupport Engineer\b", r"\bCustomer Success\b",
        ],
        "tech_hints": [],
    },
    "sales": {
        "name": "销售",
        "patterns": [
            r"\b销售经理\b", r"\b销售代表\b", r"\b客户经理\b",
            r"\b商务拓展\b", r"\bbd\b", r"\b销售工程师\b",
            r"\bSales Manager\b", r"\bSales Representative\b",
            r"\bAccount Executive\b", r"\bBusiness Development\b",
            r"\bSales Engineer\b",
        ],
        "tech_hints": [],
    },
    "management": {
        "name": "管理",
        "patterns": [
            r"\b技术负责人\b", r"\b团队负责人\b", r"\b技术经理\b",
            r"\b工程经理\b", r"\b技术总监\b", r"\bcto\b", r"\b架构师\b",
            r"\bTech Lead\b", r"\bTeam Lead\b", r"\bEngineering Manager\b",
            r"\bTechnical Manager\b", r"\bDirector\b", r"\bVP of Engineering\b",
            r"\bCTO\b", r"\bArchitect\b",
        ],
        "tech_hints": [],
    },
}


TECH_STACK_PATTERNS = {
    "python": {
        "name": "Python",
        "patterns": [
            r"\bPython\b", r"\bDjango\b", r"\bFlask\b", r"\bFastAPI\b",
            r"\bPyramid\b", r"\bTornado\b", r"\bScrapy\b",
        ],
    },
    "javascript": {
        "name": "JavaScript",
        "patterns": [
            r"\bJavaScript\b", r"\bJS\b", r"\bTypeScript\b", r"\bTS\b",
            r"\bNode\.js\b", r"\bNodeJS\b", r"\bNode\b",
            r"\bES6\b", r"\bES5\b",
        ],
    },
    "react": {
        "name": "React",
        "patterns": [
            r"\bReact\b", r"\bReact\.js\b", r"\bReactJS\b",
            r"\bNext\.js\b", r"\bNextJS\b", r"\bGatsby\b",
            r"\bReact Native\b", r"\bRN\b",
        ],
    },
    "vue": {
        "name": "Vue",
        "patterns": [
            r"\bVue\b", r"\bVue\.js\b", r"\bVueJS\b",
            r"\bNuxt\b", r"\bNuxt\.js\b", r"\bNuxtJS\b",
        ],
    },
    "java": {
        "name": "Java",
        "patterns": [
            r"\bJava\b", r"\bSpring\b", r"\bSpring Boot\b", r"\bSpringBoot\b",
            r"\bJVM\b", r"\bKotlin\b", r"\bGrails\b",
        ],
    },
    "golang": {
        "name": "Go",
        "patterns": [
            r"\bGo\b", r"\bGolang\b", r"\bGoLang\b",
            r"\bGin\b", r"\bEcho\b", r"\bGoFrame\b",
        ],
    },
    "rust": {
        "name": "Rust",
        "patterns": [
            r"\bRust\b", r"\bRustlang\b", r"\bRustLang\b",
            r"\bActix\b", r"\bRocket\b",
        ],
    },
    "php": {
        "name": "PHP",
        "patterns": [
            r"\bPHP\b", r"\bLaravel\b", r"\bSymfony\b",
            r"\bThinkPHP\b", r"\bYii\b", r"\bCodeIgniter\b",
        ],
    },
    "ruby": {
        "name": "Ruby",
        "patterns": [
            r"\bRuby\b", r"\bRails\b", r"\bRuby on Rails\b",
            r"\bRoR\b", r"\bSinatra\b",
        ],
    },
    "csharp": {
        "name": "C#",
        "patterns": [
            r"\bC#\b", r"\b\.NET\b", r"\.NET Core\b", r"\.NET Framework\b",
            r"\bASP\.NET\b", r"\bEntity Framework\b",
        ],
    },
    "swift": {
        "name": "Swift",
        "patterns": [
            r"\bSwift\b", r"\bObjective-C\b", r"\bObjC\b",
            r"\bUIKit\b", r"\bSwiftUI\b",
        ],
    },
    "kotlin": {
        "name": "Kotlin",
        "patterns": [
            r"\bKotlin\b", r"\bAndroid SDK\b",
            r"\bJetpack Compose\b",
        ],
    },
    "flutter": {
        "name": "Flutter",
        "patterns": [
            r"\bFlutter\b", r"\bDart\b",
        ],
    },
    "devops_tools": {
        "name": "DevOps",
        "patterns": [
            r"\bDocker\b", r"\bKubernetes\b", r"\bK8s\b",
            r"\bAWS\b", r"\bGCP\b", r"\bAzure\b", r"\b阿里云\b", r"\b腾讯云\b",
            r"\bTerraform\b", r"\bAnsible\b", r"\bCI/CD\b",
            r"\bJenkins\b", r"\bGitHub Actions\b", r"\bGitLab CI\b",
            r"\bNginx\b", r"\bRedis\b", r"\bElasticsearch\b",
            r"\bKafka\b", r"\bRabbitMQ\b",
        ],
    },
    "database": {
        "name": "数据库",
        "patterns": [
            r"\bMySQL\b", r"\bPostgreSQL\b", r"\bPostgres\b",
            r"\bMongoDB\b", r"\bMongo\b", r"\bRedis\b",
            r"\bElasticsearch\b", r"\bSQL\b", r"\bNoSQL\b",
            r"\bSQLite\b", r"\bOracle\b", r"\bSQL Server\b",
            r"\bTiDB\b", r"\bPolarDB\b",
        ],
    },
    "ai_ml": {
        "name": "AI/ML",
        "patterns": [
            r"\bAI\b", r"\bML\b", r"\bMachine Learning\b", r"\bDeep Learning\b",
            r"\bNLP\b", r"\bComputer Vision\b", r"\bCV\b",
            r"\bLLM\b", r"\bGPT\b", r"\bTransformer\b",
            r"\bPyTorch\b", r"\bTensorFlow\b", r"\bKeras\b",
            r"\bLangChain\b", r"\bLangchain\b",
            r"\b人工智能\b", r"\b大模型\b", r"\b机器学习\b", r"\b深度学习\b",
            r"\b自然语言处理\b", r"\b计算机视觉\b",
        ],
    },
    "frontend_tech": {
        "name": "前端技术",
        "patterns": [
            r"\bHTML\b", r"\bCSS\b", r"\bSass\b", r"\bSCSS\b", r"\bLess\b",
            r"\bTailwind\b", r"\bTailwindCSS\b",
            r"\bWebpack\b", r"\bVite\b", r"\bRollup\b", r"\bParcel\b",
            r"\bAngular\b", r"\bEmber\b", r"\bSvelte\b",
            r"\bjQuery\b", r"\bBootstrap\b",
        ],
    },
}


SENIORITY_PATTERNS = {
    "intern": {
        "name": "实习",
        "patterns": [
            r"\bIntern\b", r"\bInternship\b", r"\bTrainee\b",
            r"\b实习\b", r"\b在校生\b", r"\b应届生\b", r"\b应届毕业生\b",
        ],
    },
    "junior": {
        "name": "初级",
        "patterns": [
            r"\bJunior\b", r"\bEntry Level\b", r"\bEntry-Level\b",
            r"\b初级\b", r"\b入门\b", r"\b刚毕业\b",
            r"\b1-3年\b", r"\b1-2年\b", r"\b1年经验\b", r"\b2年经验\b",
        ],
    },
    "mid": {
        "name": "中级",
        "patterns": [
            r"\bMid\b", r"\bMid-level\b", r"\bMid Level\b",
            r"\b中级\b", r"\b3-5年\b", r"\b3年经验\b", r"\b4年经验\b",
            r"\b5年经验\b", r"\b资深\b",
        ],
    },
    "senior": {
        "name": "高级",
        "patterns": [
            r"\bSenior\b", r"\bSr\.\b", r"\bSr\b",
            r"\b5\+ years\b", r"\b5年以上\b", r"\b5-10年\b",
            r"\b高级\b", r"\b专家\b", r"\b高级工程师\b",
        ],
    },
    "lead": {
        "name": "负责人",
        "patterns": [
            r"\bLead\b", r"\bLeader\b", r"\bPrincipal\b", r"\bStaff\b",
            r"\b负责人\b", r"\bTeam Lead\b", r"\bTech Lead\b",
            r"\b技术负责人\b", r"\b架构师\b", r"\bArchitect\b",
            r"\bManager\b", r"\b总监\b", r"\bCTO\b",
        ],
    },
}


class JobClassifier:
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        self.role_patterns: Dict[str, List[re.Pattern]] = {}
        for key, data in ROLE_KEYWORDS.items():
            self.role_patterns[key] = [
                re.compile(p, re.IGNORECASE) for p in data['patterns']
            ]
        
        self.tech_patterns: Dict[str, List[re.Pattern]] = {}
        for key, data in TECH_STACK_PATTERNS.items():
            self.tech_patterns[key] = [
                re.compile(p, re.IGNORECASE) for p in data['patterns']
            ]
        
        self.seniority_patterns: Dict[str, List[re.Pattern]] = {}
        for key, data in SENIORITY_PATTERNS.items():
            self.seniority_patterns[key] = [
                re.compile(p, re.IGNORECASE) for p in data['patterns']
            ]
    
    def classify(self, title: str, description: str = "", location: str = "") -> Dict[str, List[str]]:
        title_lower = title.lower() if title else ""
        title_text = title or ""
        
        combined_text = f"{title} {description}"
        
        categories: Set[str] = set()
        for key, patterns in self.role_patterns.items():
            for pattern in patterns:
                if pattern.search(title_text):
                    categories.add(ROLE_KEYWORDS[key]['name'])
                    break
        
        if not categories:
            categories = self._infer_role_from_tech(title_text, combined_text)
        
        tech_stacks: Set[str] = set()
        for key, patterns in self.tech_patterns.items():
            for pattern in patterns:
                if pattern.search(combined_text):
                    tech_stacks.add(TECH_STACK_PATTERNS[key]['name'])
                    break
        
        seniority: Set[str] = set()
        for key, patterns in self.seniority_patterns.items():
            for pattern in patterns:
                if pattern.search(title_text):
                    seniority.add(SENIORITY_PATTERNS[key]['name'])
                    break
        
        if not categories and not tech_stacks:
            categories = self._infer_from_generic_terms(title_lower)
        
        return {
            "categories": sorted(list(categories)),
            "tech_stacks": sorted(list(tech_stacks)),
            "seniority": sorted(list(seniority)),
        }
    
    def _infer_role_from_tech(self, title: str, combined: str) -> Set[str]:
        categories: Set[str] = set()
        
        combined_lower = combined.lower()
        title_lower = title.lower()
        
        frontend_patterns = [
            r'\breact\b', r'\bvue\b', r'\bangular\b', r'\bnext\.js\b', r'\bnuxt\b', r'\bsvelte\b',
            r'\bfrontend\b', r'\bui developer\b', r'\bh5\b', r'移动端h5'
        ]
        for pattern in frontend_patterns:
            if re.search(pattern, title_lower) or re.search(pattern, combined_lower):
                categories.add(ROLE_KEYWORDS['frontend']['name'])
                break
        
        backend_patterns = [
            r'\bpython\b', r'\bjava\b', r'\bgolang\b', r'\brust\b', r'\bphp\b', r'\bruby\b',
            r'\bc#\b', r'\.net\b',
            r'\bbackend\b', r'\bserver developer\b', r'\bapi developer\b',
            r'\bdjango\b', r'\bspring\b', r'\bflask\b', r'\bfastapi\b', r'\blaravel\b', r'\brails\b',
            r'\bgo\b',
        ]
        for pattern in backend_patterns:
            if re.search(pattern, title_lower) or re.search(pattern, combined_lower):
                categories.add(ROLE_KEYWORDS['backend']['name'])
                break
        
        mobile_patterns = [
            r'\bios\b', r'\bandroid\b', r'\bswift\b', r'\bkotlin\b', r'\bflutter\b',
            r'\breact native\b', r'\bmobile developer\b'
        ]
        for pattern in mobile_patterns:
            if re.search(pattern, title_lower) or re.search(pattern, combined_lower):
                categories.add(ROLE_KEYWORDS['mobile']['name'])
                break
        
        devops_patterns = [
            r'\bdevops\b', r'\bsre\b', r'\bkubernetes\b', r'\bk8s\b', r'\bdocker\b',
            r'\bterraform\b', r'\baws\b', r'\bgcp\b', r'\bazure\b', r'云原生'
        ]
        for pattern in devops_patterns:
            if re.search(pattern, title_lower) or re.search(pattern, combined_lower):
                categories.add(ROLE_KEYWORDS['devops']['name'])
                break
        
        data_patterns = [
            r'\bdata scientist\b', r'\bdata engineer\b', r'\bdata analyst\b',
            r'机器学习', r'深度学习',
            r'\bai\b', r'\bml\b', r'\bnlp\b',
            r'\bpytorch\b', r'\btensorflow\b', r'\blangchain\b', r'\bllm\b',
            r'算法工程师', r'数据工程师', r'数据分析师', r'\bcv\b',
        ]
        for pattern in data_patterns:
            if re.search(pattern, title_lower) or re.search(pattern, combined_lower):
                categories.add(ROLE_KEYWORDS['data']['name'])
                break
        
        return categories
    
    def _infer_from_generic_terms(self, title_lower: str) -> Set[str]:
        categories: Set[str] = set()
        
        generic_terms = {
            'developer': ROLE_KEYWORDS['backend']['name'],
            'engineer': ROLE_KEYWORDS['backend']['name'],
            '工程师': ROLE_KEYWORDS['backend']['name'],
            '开发工程师': ROLE_KEYWORDS['backend']['name'],
            'software engineer': ROLE_KEYWORDS['backend']['name'],
            'software developer': ROLE_KEYWORDS['backend']['name'],
        }
        
        for term, category in generic_terms.items():
            if term in title_lower:
                categories.add(category)
                break
        
        return categories
    
    def get_all_categories(self) -> Dict[str, str]:
        return {k: v['name'] for k, v in ROLE_KEYWORDS.items()}
    
    def get_all_tech_stacks(self) -> Dict[str, str]:
        return {k: v['name'] for k, v in TECH_STACK_PATTERNS.items()}
    
    def get_all_seniority(self) -> Dict[str, str]:
        return {k: v['name'] for k, v in SENIORITY_PATTERNS.items()}


job_classifier = JobClassifier()
