#!/bin/bash

# 区域产业分析小工作台 - 一键启动脚本
# Regional Industrial Analysis Dashboard - Startup Script

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Print banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════╗
║   区域产业分析小工作台 - Regional Industrial Dashboard  ║
║   Powered by AI                                   ║
╚═══════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Check Python
print_info "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    print_error "未找到Python3，请先安装Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "Python版本: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "虚拟环境不存在，正在创建..."
    python3 -m venv venv
    print_success "虚拟环境创建完成"
fi

# Activate virtual environment
print_info "激活虚拟环境..."
source venv/bin/activate
print_success "虚拟环境已激活"

# Suppress pkg_resources deprecation warning
export PYTHONWARNINGS="ignore::UserWarning"

# Install dependencies
print_info "检查并安装依赖..."
PYTHONWARNINGS="ignore::UserWarning" pip install -q --upgrade pip
PYTHONWARNINGS="ignore::UserWarning" pip install -q -r requirements.txt
print_success "依赖安装完成"

# Check Redis
print_info "检查Redis服务..."
if ! command -v redis-cli &> /dev/null; then
    print_warning "未找到Redis，正在尝试安装..."
    if command -v brew &> /dev/null; then
        brew install redis
        print_success "Redis安装完成"
    else
        print_error "请手动安装Redis: https://redis.io/download"
        print_info "macOS: brew install redis"
        print_info "Ubuntu: sudo apt-get install redis-server"
        exit 1
    fi
fi

# Start Redis if not running
if ! redis-cli ping &> /dev/null; then
    print_info "启动Redis服务..."
    if command -v brew &> /dev/null; then
        brew services start redis
    else
        redis-server --daemonize yes
    fi
    sleep 2
fi

if redis-cli ping &> /dev/null; then
    print_success "Redis服务运行正常"
else
    print_error "Redis服务启动失败"
    exit 1
fi

# Create necessary directories
print_info "创建必要的目录..."
mkdir -p data/input data/output data/output/llm_reports
print_success "目录创建完成"

# Create log directory
mkdir -p logs

# Function to cleanup on exit
cleanup() {
    print_info "\n正在关闭服务..."
    
    # Kill all background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    # Stop Redis if we started it
    # brew services stop redis 2>/dev/null || true
    
    print_success "服务已关闭"
    exit 0
}

# Trap cleanup on script exit
trap cleanup EXIT INT TERM

# Start Celery Worker in background
print_info "启动Celery后台任务处理器..."
export PYTHONPATH="$SCRIPT_DIR/..:$PYTHONPATH"
PYTHONWARNINGS="ignore::UserWarning" venv/bin/celery -A src.tasks.celery_app worker --loglevel=info > logs/celery.log 2>&1 &
CELERY_PID=$!
sleep 3

if ps -p $CELERY_PID > /dev/null; then
    print_success "Celery Worker已启动 (PID: $CELERY_PID)"
else
    print_error "Celery Worker启动失败，请查看logs/celery.log"
    exit 1
fi

# Start Flask Application
print_info "启动Flask应用..."
echo ""
print_success "=========================================="
print_success "🚀 系统启动成功！"
print_success "=========================================="
echo ""
print_info "访问地址: ${GREEN}http://localhost:5000${NC}"
print_info "默认账号: ${YELLOW}admin${NC}"
print_info "默认密码: ${YELLOW}admin${NC}"
echo ""
print_warning "按 Ctrl+C 停止系统"
echo ""

# Start Flask (this will block)
PYTHONWARNINGS="ignore::UserWarning" venv/bin/python3 app.py

# Note: cleanup function will be called on exit
