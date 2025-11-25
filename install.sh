#!/bin/bash
# Installation script for Regional Industrial Dashboard with WeChat functionality

echo "Regional Industrial Dashboard - Installation Script"
echo "=============================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$python_version < 3.7" | bc -l) -eq 1 ]]; then
    echo "Error: Python 3.7 or higher is required. Current version: $python_version"
    exit 1
fi

echo "Python version: $python_version ✓"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Install wechatsogou separately to handle potential issues
echo "Installing wechatsogou..."
pip install wechatsogou || {
    echo "Warning: Failed to install wechatsogou. The application will still work but with mock implementation."
    echo "To enable real WeChat content fetching, install it manually with one of these options:"
    echo "  pip install wechatsogou"
    echo "  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple wechatsogou"
    echo "  pip install wechatsogou==2023.3.3"
}

# Setup directories
echo "Setting up directories..."
mkdir -p data/input
mkdir -p data/output
mkdir -p data/output/llm_reports
mkdir -p static/css
mkdir -p static/js
mkdir -p logs

# Check if config.json exists, if not create a basic one
if [ ! -f "config.json" ]; then
    echo "Creating basic config.json..."
    cat > config.json << EOF
{
    "categories": [
        "产业概述", "政策环境", "市场规模", "重点企业",
        "技术趋势", "发展机遇", "挑战风险", "未来展望"
    ],
    "ai_integration_focus": [
        "智能制造", "数据分析", "自动化流程", "预测性维护",
        "供应链优化", "客户服务", "质量控制"
    ],
    "api_keys": {
        "google_map": "",
        "baidu_map": ""
    }
}
EOF
fi

# Check if wechat_accounts_config.json exists, if not create a basic one
if [ ! -f "data/wechat_accounts_config.json" ]; then
    echo "Creating basic wechat_accounts_config.json..."
    mkdir -p data
    cat > data/wechat_accounts_config.json << EOF
[
  {
    "province": "四川省",
    "accounts": [
      "四川发布",
      "天府发布"
    ],
    "cities": [
      {
        "city": "成都市",
        "accounts": [
          "成都发布"
        ],
        "districts": [
          {
            "district": "高新区",
            "accounts": [
              "成都高新"
            ]
          }
        ]
      }
    ]
  },
  {
    "province": "北京市",
    "accounts": [
      "北京发布"
    ],
    "cities": []
  }
]
EOF
fi

# Initialize database
echo "Initializing database..."
python3 -c "
import sys
import os
sys.path.append(os.getcwd())
from app import init_db
init_db()
print('Database initialized successfully')
"

echo "=============================================="
echo "Installation completed successfully!"
echo ""
echo "To start the application, run:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "To start the Celery worker (for background tasks), run in another terminal:"
echo "  source venv/bin/activate"
echo "  celery -A src.tasks.celery_app worker --loglevel=info"
echo ""
echo "To start the Celery beat (for periodic tasks), run in another terminal:"
echo "  source venv/bin/activate"
echo "  celery -A src.tasks.celery_app beat --loglevel=info"
echo ""
echo "Note: If you didn't install wechatsogou properly, the WeChat functionality"
echo "will use mock data. To install it manually, run:"
echo "  pip install wechatsogou"
echo "=============================================="