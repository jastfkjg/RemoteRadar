import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.classifier import job_classifier


test_titles = [
    "Senior Technical Lead DevOps - AWS",
    "Full Stack Developer - Backend Focus",
    "Product Owner Frontend",
    "Mid Senior AI Video Artist",
    "Senior React Developer",
    "Python Backend Engineer",
    "Junior Frontend Developer",
    "Data Scientist - Machine Learning",
    "iOS Engineer - Swift",
    "Account Executive III",
    "UX Designer",
    "DevOps Engineer - Kubernetes",
    "QA Automation Engineer",
    "Security Analyst",
    "Content Writer",
    "Customer Support Specialist",
]

print("=== 测试分类器 ===\n")

for title in test_titles:
    result = job_classifier.classify(title)
    print(f"标题: {title}")
    print(f"  职位类别: {result['categories'] or '(无)'}")
    print(f"  技术栈: {result['tech_stacks'] or '(无)'}")
    print(f"  职级: {result['seniority'] or '(无)'}")
    print()
