#!/bin/bash
# Script to install wechatsogou and configure WeChat functionality

echo "=============================================="
echo "WeChat Functionality Setup"
echo "=============================================="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Error: venv directory not found. Please run the main installation script first."
    exit 1
fi

echo "Attempting to install wechatsogou..."

# Try different installation methods
pip install wechatsogou && {
    echo "✅ wechatsogou installed successfully!"
    echo "The application will now fetch real content from WeChat public accounts."
    exit 0
} || {
    echo "❌ Standard installation failed. Trying alternative methods..."
}

# Alternative installation with specific version
pip install wechatsogou==2023.3.3 && {
    echo "✅ wechatsogou installed successfully!"
    echo "The application will now fetch real content from WeChat public accounts."
    exit 0
} || {
    echo "❌ Version-specific installation failed. Trying Chinese mirror..."
}

# Alternative installation with Chinese mirror
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple wechatsogou && {
    echo "✅ wechatsogou installed successfully!"
    echo "The application will now fetch real content from WeChat public accounts."
    exit 0
} || {
    echo "❌ All installation methods failed."
    echo ""
    echo "Note: The application will continue to work with mock implementation."
    echo "To enable real WeChat functionality, please try manual installation:"
    echo ""
    echo "1. Activate your virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Try one of these commands:"
    echo "   pip install wechatsogou"
    echo "   pip install wechatsogou==2023.3.3"
    echo "   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple wechatsogou"
    echo ""
    echo "3. If pip install fails, you may need to:"
    echo "   - Update pip: pip install --upgrade pip"
    echo "   - Use proxy if in China: pip install --proxy http://<proxy>:<port> wechatsogou"
    echo "   - Install dependencies manually"
    echo ""
    echo "The system will still work with mock data. All other features are unaffected."
}

echo "=============================================="