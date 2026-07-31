#!/bin/bash
# Nexus Free 一键启动脚本

set -e

echo "=========================================="
echo "  Nexus Free - 虚拟角色检索引擎"
echo "=========================================="

# 检查 .env
if [ ! -f .env ]; then
    echo "❌ 未找到 .env 文件"
    echo "   请复制 .env.example 为 .env 并填入 API Key"
    echo "   cp .env.example .env"
    exit 1
fi

# 检查 Docker
if command -v docker &> /dev/null; then
    echo "🐳 使用 Docker 启动..."
    docker compose up -d --build
    echo "✅ 已启动: http://localhost:8000"
    echo "   查看日志: docker compose logs -f"
    echo "   停止: docker compose down"
else
    echo "🐍 使用 Python 直接启动..."
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
