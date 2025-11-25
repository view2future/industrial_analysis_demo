#!/bin/bash
# setup.sh - Setup script for Regional Industrial Dashboard

echo "🚀 Setting up Regional Industrial Dashboard..."

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "🔧 Installing dependencies..."
pip install -r requirements.txt

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "📝 Creating config.json template..."
    cat > config.json << EOF
{
  "api_keys": {
    "kimi": "",
    "google_gemini": "",
    "google_map": "",
    "baidu_map": "",
    "baidu_ernie": ""
  },
  "categories": [
    "产业概述",
    "政策环境",
    "市场规模",
    "重点企业",
    "技术趋势",
    "发展机遇",
    "挑战风险",
    "未来展望"
  ],
  "ai_integration_focus": [
    "智能制造",
    "数据分析",
    "自动化流程",
    "预测性维护",
    "供应链优化",
    "客户服务",
    "质量控制"
  ],
  "google_maps": {
    "map_id": ""
  },
  "version": "1.1"
}
EOF
    echo "📝 Please update config.json with your API keys before running the application."
fi

echo "✅ Setup complete!"
echo "📥 To activate the virtual environment, run: source venv/bin/activate"
echo "🚀 To start the application, run: python app.py"
echo "📖 For more information, read the README.md file."