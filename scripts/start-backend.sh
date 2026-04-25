#!/bin/bash

echo "🚀 启动 FastAPI 后端服务器..."
echo "📡 API文档: http://localhost:8000/docs"
echo ""

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
