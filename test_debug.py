import sqlite3
import sys

sys.path.insert(0, '.')

print("=== 测试分类器导入 ===")
try:
    from src.classifier import job_classifier
    print("✓ 分类器导入成功")
    
    # 测试分类
    test_title = "高级前端开发工程师"
    test_desc = "要求熟练掌握 React, TypeScript, 有3年以上经验"
    result = job_classifier.classify(test_title, test_desc)
    print(f"\n测试标题: {test_title}")
    print(f"分类结果: {result}")
except Exception as e:
    print(f"✗ 分类器导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 数据库检查 ===")
try:
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(job_listings)")
    columns = cursor.fetchall()
    print("表结构:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 检查数据
    cursor.execute('SELECT COUNT(*) FROM job_listings')
    count = cursor.fetchone()[0]
    print(f"\n总记录数: {count}")
    
    if count > 0:
        # 检查来源
        cursor.execute('SELECT source, COUNT(*) FROM job_listings GROUP BY source')
        sources = cursor.fetchall()
        print("\n来源分布:")
        for s in sources:
            print(f"  {s[0]}: {s[1]}")
        
        # 检查分类字段
        cursor.execute('''
            SELECT id, source, title, categories, tech_stacks, seniority 
            FROM job_listings 
            LIMIT 3
        ''')
        rows = cursor.fetchall()
        print("\n样本数据:")
        for row in rows:
            print(f"  ID: {row[0]}")
            print(f"  Source: {row[1]}")
            print(f"  Title: {row[2]}")
            print(f"  Categories: '{row[3]}'")
            print(f"  Tech: '{row[4]}'")
            print(f"  Seniority: '{row[5]}'")
            print()
        
        # 检查是否有分类数据
        cursor.execute('SELECT COUNT(*) FROM job_listings WHERE categories IS NOT NULL AND categories != ""')
        cat_count = cursor.fetchone()[0]
        print(f"\n有分类标签的记录数: {cat_count}")
    
    conn.close()
except Exception as e:
    print(f"数据库检查失败: {e}")
    import traceback
    traceback.print_exc()
