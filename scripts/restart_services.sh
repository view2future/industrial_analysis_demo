#!/bin/bash
# 重新启动系统的脚本

echo "🛑 停止现有服务..."

# 停止 Celery
pkill -f "celery.*worker" 2>/dev/null
echo "  ✓ Celery 已停止"

# 等待进程完全停止
sleep 2

echo ""
echo "🚀 启动服务..."

# 确保日志目录存在
mkdir -p logs

# 启动 Celery worker
echo "  启动 Celery worker..."
cd /Users/wangyu94/regional-industrial-dashboard
python3 -m celery -A src.tasks.celery_app worker --loglevel=info --detach --logfile=logs/celery.log

sleep 3

# 检查 Celery 是否启动
if pgrep -f "celery.*worker" > /dev/null; then
    echo "  ✓ Celery worker 已启动"
else
    echo "  ✗ Celery worker 启动失败"
    exit 1
fi

echo ""
echo "✅ 所有服务已启动"
echo ""
echo "访问: http://localhost:5000"
echo "查看日志: tail -f logs/celery.log"
echo ""

# 如果Flask应用还没运行，提示启动
if ! pgrep -f "python.*app_enhanced" > /dev/null; then
    echo "💡 Flask 应用未运行，请手动启动:"
    echo "   python3 app_enhanced.py"
fi
