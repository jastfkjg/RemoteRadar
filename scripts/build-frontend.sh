#!/bin/bash

echo "🔧 构建 React 前端..."

cd frontend && npm run build

echo ""
echo "✅ 构建完成！输出目录: frontend/dist"
echo ""
echo "📦 可以通过 FastAPI 服务访问构建后的前端:"
echo "   http://localhost:8000"
