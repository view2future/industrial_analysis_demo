#!/usr/bin/env python3
"""
Regional Industrial Analysis Dashboard
Main application file that provides web interface for analyzing regional industrial data.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.analysis.text_processor import TextProcessor
from src.visualization.dashboard_generator import DashboardGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='../templates')
app.secret_key = 'regional_industrial_analysis_2024'
app.config['UPLOAD_FOLDER'] = 'data/input'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'md', 'json', 'doc', 'docx', 'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard page."""
    try:
        # Check if there's any processed data to display
        output_dir = Path('data/output')
        recent_files = []
        
        if output_dir.exists():
            for file in output_dir.glob('*.json'):
                recent_files.append({
                    'name': file.stem,
                    'date': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'path': str(file)
                })
        
        recent_files.sort(key=lambda x: x['date'], reverse=True)
        
        return render_template('index.html', recent_files=recent_files[:5])
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('index.html', recent_files=[])

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload and processing."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('没有选择文件')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('没有选择文件')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Ensure upload directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(file_path)
                
                # Process the file
                processor = TextProcessor()
                analysis_result = processor.analyze_file(file_path)
                
                if analysis_result:
                    # Generate dashboard data
                    dashboard_gen = DashboardGenerator()
                    dashboard_data = dashboard_gen.generate_dashboard_data(analysis_result)
                    
                    # Save processed data
                    output_path = os.path.join('data/output', f"{timestamp}_analysis.json")
                    os.makedirs('data/output', exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
                    
                    flash('文件上传并分析成功！')
                    return redirect(url_for('view_analysis', filename=f"{timestamp}_analysis.json"))
                else:
                    flash('文件处理失败，请检查文件格式')
                    
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                flash(f'处理文件时出错: {str(e)}')
        else:
            flash('不支持的文件格式。请上传 .txt, .md, .json, .docx 或 .pdf 文件')
    
    return render_template('upload.html')

@app.route('/analysis/<filename>')
def view_analysis(filename):
    """View analysis results."""
    try:
        file_path = os.path.join('data/output', filename)
        if not os.path.exists(file_path):
            flash('分析结果文件不存在')
            return redirect(url_for('index'))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        return render_template('analysis.html', data=analysis_data)
        
    except Exception as e:
        logger.error(f"Error viewing analysis: {e}")
        flash('无法加载分析结果')
        return redirect(url_for('index'))

@app.route('/api/analysis/<filename>')
def api_analysis(filename):
    """API endpoint to get analysis data as JSON."""
    try:
        file_path = os.path.join('data/output', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        return jsonify(analysis_data)
        
    except Exception as e:
        logger.error(f"Error in API analysis: {e}")
        return jsonify({'error': '读取分析数据失败'}), 500

@app.route('/settings')
def settings():
    """Configuration settings page."""
    try:
        config_path = 'config.json'
        config = {}
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        return render_template('settings.html', config=config)
        
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return render_template('settings.html', config={})

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API endpoint for configuration management."""
    config_path = 'config.json'
    
    if request.method == 'GET':
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = get_default_config()
            return jsonify(config)
        except Exception as e:
            logger.error(f"Error reading config: {e}")
            return jsonify({'error': '读取配置失败'}), 500
    
    elif request.method == 'POST':
        try:
            config = request.json
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return jsonify({'error': '保存配置失败'}), 500

def get_default_config():
    """Get default configuration."""
    return {
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
        ]
    }

def setup_directories():
    """Ensure all necessary directories exist."""
    directories = [
        'data/input',
        'data/output',
        'static/css',
        'static/js',
        'templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

if __name__ == '__main__':
    # Setup directories
    setup_directories()
    
    # Create default config if it doesn't exist
    if not os.path.exists('config.json'):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(get_default_config(), f, ensure_ascii=False, indent=2)
    
    # Get port from environment variable (for Render) or default to 8080
    port = int(os.environ.get('PORT', 8080))
    
    # Run the application
    print("🚀 启动区域产业分析小工作台...")
    print(f"📊 访问 http://localhost:{port} 查看仪表板")
    print("📁 将区域产业分析报告保存为文件并上传分析")
    
    app.run(debug=False, host='0.0.0.0', port=port)
