import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.classifier import job_classifier
from datetime import datetime


def migrate_database():
    db_path = "jobs.db"
    
    print("=== 数据库迁移 ===")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 添加新字段（如果不存在）
    cursor.execute("PRAGMA table_info(job_listings)")
    columns = [row[1] for row in cursor.fetchall()]
    
    migrations = [
        ('categories', 'TEXT'),
        ('tech_stacks', 'TEXT'),
        ('seniority', 'TEXT'),
    ]
    
    for column, column_type in migrations:
        if column not in columns:
            try:
                cursor.execute(f'ALTER TABLE job_listings ADD COLUMN {column} {column_type}')
                print(f"✓ 添加列: {column}")
            except Exception as e:
                print(f"✗ 添加列失败 {column}: {e}")
        else:
            print(f"✓ 列已存在: {column}")
    
    conn.commit()
    
    # 2. 获取所有记录并重新分类
    cursor.execute('SELECT id, title, description, location FROM job_listings')
    rows = cursor.fetchall()
    
    print(f"\n总记录数: {len(rows)}")
    
    count = 0
    for row in rows:
        job_id, title, description, location = row
        
        classified = job_classifier.classify(
            title=title or "",
            description=description or "",
            location=location or ""
        )
        
        categories = ', '.join(classified.get('categories', []))
        tech_stacks = ', '.join(classified.get('tech_stacks', []))
        seniority = ', '.join(classified.get('seniority', []))
        
        cursor.execute('''
            UPDATE job_listings 
            SET categories=?, tech_stacks=?, seniority=?, updated_at=?
            WHERE id=?
        ''', (
            categories,
            tech_stacks,
            seniority,
            datetime.now().isoformat(),
            job_id
        ))
        
        count += 1
        if count % 20 == 0:
            print(f"  已处理 {count}/{len(rows)} 条记录")
    
    conn.commit()
    
    # 3. 验证结果
    print("\n=== 验证结果 ===")
    
    cursor.execute('SELECT COUNT(*) FROM job_listings WHERE categories IS NOT NULL AND categories != ""')
    cat_count = cursor.fetchone()[0]
    print(f"有分类的记录数: {cat_count}")
    
    cursor.execute('''
        SELECT id, title, categories, tech_stacks, seniority 
        FROM job_listings 
        LIMIT 10
    ''')
    samples = cursor.fetchall()
    print("\n样本数据:")
    for sample in samples:
        print(f"\n  ID: {sample[0]}")
        print(f"  Title: {sample[1][:60] if sample[1] else ''}...")
        print(f"  Categories: '{sample[2]}'")
        print(f"  Tech Stacks: '{sample[3]}'")
        print(f"  Seniority: '{sample[4]}'")
    
    # 4. 检查来源数据
    print("\n=== 来源分布 ===")
    cursor.execute('SELECT source, COUNT(*) FROM job_listings GROUP BY source')
    sources = cursor.fetchall()
    for s in sources:
        print(f"  {s[0]}: {s[1]}")
    
    # 5. 检查职位类别分布
    print("\n=== 职位类别分布 ===")
    cursor.execute('SELECT categories FROM job_listings WHERE categories IS NOT NULL AND categories != ""')
    all_categories = cursor.fetchall()
    category_counts = {}
    for row in all_categories:
        if row[0]:
            for cat in row[0].split(', '):
                if cat:
                    category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, cnt in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt}")
    
    conn.close()
    print(f"\n✓ 迁移完成！共处理 {count} 条记录")


if __name__ == "__main__":
    migrate_database()
