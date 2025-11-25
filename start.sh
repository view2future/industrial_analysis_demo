#!/bin/bash

# Start script for Regional Industrial Dashboard
# This script sets up and starts the Flask application

echo "🚀 Starting Regional Industrial Dashboard..."

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed, if not install them
if [ ! -f "venv/installed" ]; then
    echo "📦 Installing dependencies (this may take a few minutes)..."
    pip install -r requirements.txt > /dev/null 2>&1
    touch venv/installed
    echo "✅ Dependencies installed!"
else
    echo "✅ Virtual environment ready!"
fi

# Start the Flask application
echo "🏃 Starting the application..."
echo "🌐 Open your browser and go to http://localhost:5000"
python app.py

echo "👋 Application stopped."