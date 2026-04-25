#!/bin/bash

echo "🕷️ 运行爬虫抓取职位数据..."
echo ""

python main.py --spiders all --delay 1.5

echo ""
echo "✅ 爬取完成！"
echo ""
echo "📊 查看统计:"
echo "   python main.py --stats"
