#!/bin/bash
# run.sh - Run script for Regional Industrial Dashboard

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Run the application
echo "🚀 Starting Regional Industrial Dashboard..."
python app.py