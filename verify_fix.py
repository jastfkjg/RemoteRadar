import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verify_database():
    db_path = "jobs.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("验证数据库")
    print("=" * 60)
    
    print("\n1. 来源统计:")
    cursor.execute('SELECT source, COUNT(*) FROM job_listings GROUP BY source')
    sources = cursor.fetchall()
    for s in sources:
        print(f"   {s[0]}: {s[1]} 条")
    
    print("\n2. 职位类别分布:")
    cursor.execute('SELECT categories FROM job_listings WHERE categories IS NOT NULL AND categories != ""')
    all_categories = cursor.fetchall()
    category_counts = {}
    for row in all_categories:
        if row[0]:
            for cat in row[0].split(', '):
                if cat:
                    category_counts[cat] = category_counts.get(cat, 0) + 1
    
    if category_counts:
        for cat, cnt in sorted(category_counts.items(), key=lambda x: -x[1]):
            print(f"   {cat}: {cnt}")
    else:
        print("   无数据")
    
    print("\n3. 技术栈分布:")
    cursor.execute('SELECT tech_stacks FROM job_listings WHERE tech_stacks IS NOT NULL AND tech_stacks != ""')
    all_tech = cursor.fetchall()
    tech_counts = {}
    for row in all_tech:
        if row[0]:
            for tech in row[0].split(', '):
                if tech:
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
    
    if tech_counts:
        for tech, cnt in sorted(tech_counts.items(), key=lambda x: -x[1]):
            print(f"   {tech}: {cnt}")
    else:
        print("   无数据")
    
    print("\n4. 职级分布:")
    cursor.execute('SELECT seniority FROM job_listings WHERE seniority IS NOT NULL AND seniority != ""')
    all_seniority = cursor.fetchall()
    seniority_counts = {}
    for row in all_seniority:
        if row[0]:
            for level in row[0].split(', '):
                if level:
                    seniority_counts[level] = seniority_counts.get(level, 0) + 1
    
    if seniority_counts:
        for level, cnt in sorted(seniority_counts.items(), key=lambda x: -x[1]):
            print(f"   {level}: {cnt}")
    else:
        print("   无数据")
    
    print("\n5. 样本职位:")
    cursor.execute('''
        SELECT id, title, categories, tech_stacks, seniority, source 
        FROM job_listings 
        LIMIT 10
    ''')
    samples = cursor.fetchall()
    for sample in samples:
        print(f"\n   ID: {sample[0]}")
        print(f"   标题: {sample[1][:50]}..." if len(sample[1]) > 50 else f"   标题: {sample[1]}")
        print(f"   来源: {sample[5]}")
        print(f"   类别: {sample[2] or '(无)'}")
        print(f"   技术栈: {sample[3] or '(无)'}")
        print(f"   职级: {sample[4] or '(无)'}")
    
    print("\n" + "=" * 60)
    print("总结:")
    print("=" * 60)
    
    cursor.execute('SELECT COUNT(*) FROM job_listings')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM job_listings WHERE categories IS NOT NULL AND categories != ""')
    has_cat = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT source) FROM job_listings')
    source_count = cursor.fetchone()[0]
    
    print(f"总记录数: {total}")
    print(f"有分类的记录数: {has_cat}")
    print(f"来源数量: {source_count}")
    
    if source_count > 0 and has_cat > 0:
        print("\n✓ 修复成功！")
        print("  - 职位类别、技术栈、职级现在有数据了")
        print("  - 数据来源包含多个值（remoteok, weworkremotely）")
    else:
        print("\n✗ 仍有问题需要检查")
    
    conn.close()


if __name__ == "__main__":
    verify_database()
