#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║       DataForge v1.0.0 启动中...     ║"
echo "╚══════════════════════════════════════╝"

# 启动后端（数据持久保存在 dataforge.db）
echo "→ 启动后端 (http://localhost:8000)"
cd "$ROOT_DIR/backend"
source venv/bin/activate
python main.py &

# 启动前端
echo "→ 启动前端 (http://localhost:5173)"
cd "$ROOT_DIR/frontend"
npm run dev &

echo ""
echo "✅ DataForge 已启动!"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo "   数据持久保存在 backend/dataforge.db"
echo ""
echo "按 Ctrl+C 停止所有服务"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '已停止'; exit 0" SIGINT SIGTERM

wait
