# 🚀 区域产业分析小工作台 / Regional Industrial Dashboard

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个专为区域产业分析设计的智能化仪表板工具，将 AI 分析结果转化为直观的可视化报告。

An intelligent dashboard tool designed for regional industrial analysis that transforms AI analysis results into intuitive visual reports.

## 🎯 项目简介 / Project Overview

本项目旨在解决区域产业分析中信息获取成本高、理解难度大的痛点。通过智能文本处理和可视化技术，将复杂的产业分析报告转化为易读易懂的仪表板，助力产业研究、投资决策和政策制定。

This project aims to solve the pain points of high information acquisition costs and difficulty in understanding in regional industrial analysis. Through intelligent text processing and visualization technology, it transforms complex industrial analysis reports into easy-to-read dashboards to assist industrial research, investment decisions, and policy making.

### 核心功能 / Core Features

- 📊 **智能文本分析**: 自动分类和提取产业分析内容 / **Smart Text Analysis**: Automatic classification and extraction of industrial analysis content
- 🤖 **AI应用机会识别**: 分析文档中的AI技术应用潜力 / **AI Application Opportunity Identification**: Analyze AI technology application potential in documents
- 📈 **可视化仪表板**: 多种图表展示分析结果 / **Visualization Dashboard**: Multiple charts to display analysis results
- ⚙️ **可配置分析**: 支持自定义分析类别和AI应用场景 / **Configurable Analysis**: Support custom analysis categories and AI application scenarios
- 🌐 **Web界面**: 友好的用户界面，支持拖拽上传 / **Web Interface**: User-friendly interface with drag-and-drop upload
- 🗺️ **地图可视化**: 基于Google Maps的POI可视化 / **Map Visualization**: POI visualization based on Google Maps
- 📋 **多格式导出**: 支持PDF、Word、Excel格式报告导出 / **Multi-format Export**: Support PDF, Word, Excel report export
- 📱 **微信公众号集成**: 从指定的微信公众号抓取政策内容并集成到智能检索中 / **WeChat Public Account Integration**: Fetch policy content from specified WeChat accounts and integrate into smart search

## 🏗️ 系统架构 / System Architecture

```
regional-industrial-dashboard/
├── app.py                      # 主应用程序 / Main application
├── requirements.txt            # Python依赖 / Python dependencies
├── config.json                # 配置文件 / Configuration file
├── src/                       # 源代码 / Source code
│   ├── ai/                   # AI和LLM集成模块 / AI and LLM integration modules
│   ├── analysis/             # 数据分析和处理模块 / Data analysis and processing modules
│   ├── visualization/        # 数据可视化组件 / Data visualization components
│   ├── export/               # 报告导出功能 / Report export functionality
│   ├── utils/                # 工具函数和服务 / Utility functions and services
│   └── tasks/                # 后台任务处理 / Background task processing
├── templates/                # HTML模板 / HTML templates
├── static/                   # 静态资源 / Static resources
└── tests/                    # 测试文件 / Test files
```

## 🚀 快速开始 / Quick Start

### 环境要求 / Prerequisites

- Python 3.8+
- macOS / Linux / Windows
- 8GB+ RAM（推荐）/ 8GB+ RAM (recommended)
- 2GB+ 可用磁盘空间 / 2GB+ available disk space

### 安装步骤 / Installation Steps

1. **克隆项目 / Clone the project**
```bash
git clone https://github.com/your-username/regional-industrial-dashboard.git
cd regional-industrial-dashboard
```

2. **创建虚拟环境 / Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或者 / or
venv\Scripts\activate     # Windows
```

3. **安装依赖 / Install dependencies**
```bash
pip install -r requirements.txt
```

4. **配置API密钥 / Configure API keys**
创建一个 `config.json` 文件在项目根目录，包含您的API密钥：
Create a `config.json` file in the project root with your API keys:

```json
{
  "api_keys": {
    "kimi": "your_kimi_api_key",
    "google_gemini": "your_google_gemini_api_key",
    "google_map": "your_google_maps_api_key",
    "baidu_map": "your_baidu_map_api_key",
    "baidu_ernie": "your_baidu_ernie_api_key"
  }
}
```

5. **运行应用 / Run the application**
```bash
python app.py
```

6. **访问应用 / Access the application**
打开浏览器访问：`http://localhost:5000`
Open your browser and visit: `http://localhost:5000`

## 📋 使用指南 / Usage Guide

### 1. 文件上传与分析 / File Upload and Analysis

1. 点击"开始分析"按钮或访问上传页面 / Click the "Start Analysis" button or visit the upload page
2. 支持的文件格式 / Supported file formats：
   - `.txt` - 纯文本文件 / Plain text files
   - `.md` - Markdown 文件 / Markdown files
   - `.json` - JSON 格式数据 / JSON format data
   - `.docx` - Word 文档 / Word documents
   - `.pdf` - PDF 文件 / PDF files
3. 拖拽文件到上传区域或点击选择文件 / Drag files to the upload area or click to select files
4. 选择分析选项（默认全部启用）/ Select analysis options (all enabled by default)
5. 点击"开始分析" / Click "Start Analysis"

### 2. 分析结果查看 / View Analysis Results

分析完成后，系统将自动跳转到结果页面，包含：
After analysis is complete, the system will automatically redirect to the results page, including:

- **核心要点**: 文档的关键信息摘要 / **Key Points**: Key information summary of the document
- **可视化图表**: / **Visualization Charts**:
  - 内容分类分布（饼图）/ Content classification distribution (pie chart)
  - AI应用潜力分析（雷达图）/ AI application potential analysis (radar chart)
  - 关键词频次分析（柱状图）/ Keyword frequency analysis (bar chart)
  - 文档统计概览（条形图）/ Document statistics overview (bar chart)
- **分类分析详情**: 按类别展示的详细内容 / **Category Analysis Details**: Detailed content displayed by category
- **AI应用机会**: 按场景分析的AI应用潜力和建议 / **AI Application Opportunities**: AI application potential and recommendations analyzed by scenario

## ⚙️ 配置说明 / Configuration

### 分析类别配置 / Analysis Category Configuration

默认分析类别包括 / Default analysis categories include:
- 产业概述 / Industry Overview
- 政策环境 / Policy Environment
- 市场规模 / Market Size
- 重点企业 / Key Enterprises
- 技术趋势 / Technology Trends
- 发展机遇 / Development Opportunities
- 挑战风险 / Challenges and Risks
- 未来展望 / Future Outlook

### AI应用场景配置 / AI Application Scenario Configuration

默认AI应用场景包括 / Default AI application scenarios include:
- 智能制造 / Smart Manufacturing
- 数据分析 / Data Analysis
- 自动化流程 / Process Automation
- 预测性维护 / Predictive Maintenance
- 供应链优化 / Supply Chain Optimization
- 客户服务 / Customer Service
- 质量控制 / Quality Control

可以在设置页面根据需要添加、修改或删除类别和场景。
You can add, modify, or delete categories and scenarios as needed on the settings page.

## 🔧 技术架构 / Technology Stack

### 后端技术栈 / Backend Technology Stack

- **Flask**: Web框架 / Web framework
- **jieba**: 中文分词和词性标注 / Chinese word segmentation and POS tagging
- **pandas**: 数据处理和分析 / Data processing and analysis
- **plotly**: 交互式图表生成 / Interactive chart generation
- **python-docx**: Word文档处理 / Word document processing
- **PyPDF2**: PDF文件处理 / PDF file processing
- **openpyxl**: Excel文件处理 / Excel file processing
- **reportlab**: PDF报告生成 / PDF report generation
- **openai**: AI模型集成 / AI model integration
- **google-generativeai**: Google Gemini API集成 / Google Gemini API integration

### 前端技术栈 / Frontend Technology Stack

- **Tailwind CSS**: 样式框架 / Styling framework
- **Font Awesome**: 图标库 / Icon library
- **Plotly.js**: 图表渲染 / Chart rendering
- **Vanilla JavaScript**: 交互逻辑 / Interactive logic

## 📊 示例数据 / Sample Data

项目包含示例数据文件：`data/input/sample_ai_industry_analysis.md`

This project includes sample data file: `data/input/sample_ai_industry_analysis.md`

这是一份关于成都市人工智能产业发展的分析报告，展示了系统的分析能力。您可以：
This is an analysis report on the development of artificial intelligence industry in Chengdu, demonstrating the system's analysis capabilities. You can:

1. 上传此示例文件进行测试 / Upload this sample file for testing
2. 查看分析结果和可视化图表 / View analysis results and visualization charts
3. 了解系统的功能特性 / Understand the system's features

## 🔍 故障排除 / Troubleshooting

### 常见问题 / Common Issues

**Q: 上传文件后分析失败？** / **Q: Analysis fails after uploading a file?**
A: 检查文件格式是否支持，文件是否损坏，确保文件内容包含中文文本。
A: Check if the file format is supported, if the file is corrupted, and ensure the file content contains Chinese text.

**Q: 图表显示异常？** / **Q: Charts display abnormally?**
A: 检查浏览器是否支持JavaScript，确保网络连接正常加载Plotly.js。
A: Check if the browser supports JavaScript and ensure network connection loads Plotly.js properly.

**Q: 中文分词效果不佳？** / **Q: Chinese word segmentation is not effective?**
A: 系统已集成jieba分词并加载了行业术语词典，如需优化可在代码中添加自定义词汇。
A: The system has integrated jieba segmentation and loaded industry terminology dictionaries. Custom vocabulary can be added in the code for optimization.

**Q: 内存不足错误？** / **Q: Memory insufficient error?**
A: 减小上传文件大小（建议<16MB），或增加系统内存配置。
A: Reduce the uploaded file size (recommended <16MB) or increase system memory configuration.

**Q: WeChat功能显示 'wechatsogou library not available'？** / **Q: WeChat feature shows 'wechatsogou library not available'?**
A: 该提示表示wechatsogou库未安装，系统使用模拟实现。要启用真实功能，请运行：pip install wechatsogou
A: This message indicates the wechatsogou library is not installed, the system uses mock implementation. To enable real functionality, run: pip install wechatsogou

## 🧪 测试 / Testing

运行测试套件：
Run the test suite:

## 📱 微信公众号功能 / WeChat Public Account Feature

### 功能特性 / Features

- **自动抓取**: 系统启动时自动抓取指定微信公众号的最新文章 / **Auto Fetch**: Automatically fetch latest articles from specified WeChat accounts when the system starts
- **智能检索**: 在政策智能检索中集成微信公众号内容 / **Smart Search**: Integrate WeChat account content into policy smart search
- **配置管理**: 通过配置文件管理需要监控的公众号 / **Configuration Management**: Manage monitored accounts via configuration file
- **数据存储**: 自动将抓取的文章存储到本地数据库 / **Data Storage**: Automatically store fetched articles in local database
- **定时更新**: 每日定时自动更新微信公众号内容 / **Scheduled Updates**: Automatic daily updates of WeChat account content
- **智能匹配**: 按地区和行业标签智能匹配相关内容 / **Smart Matching**: Smart matching of relevant content by region and industry tags

### 配置方法 / Configuration Method

1. **编辑微信公众号配置文件** / Edit WeChat account configuration file:
   ```bash
   # 配置文件路径 / Configuration file path
   data/wechat_accounts_config.json
   ```

2. **配置格式** / Configuration format:
   ```json
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
     }
   ]
   ```

### 安装 wechatsogou / Installing wechatsogou

为了启用真实的微信公众号内容抓取，需要安装 wechatsogou 库：
To enable real WeChat account content fetching, install the wechatsogou library:

```bash
pip install wechatsogou
```

如果安装失败，系统会使用模拟实现，不影响主要功能。
If installation fails, the system will use mock implementation without affecting main functionality.

### 后台任务 / Background Tasks

系统使用 Celery 运行后台任务：
The system uses Celery to run background tasks:

1. **启动 Celery worker** (for background tasks):
   ```bash
   celery -A src.tasks.celery_app worker --loglevel=info
   ```

2. **启动 Celery beat** (for scheduled tasks):
   ```bash
   celery -A src.tasks.celery_app beat --loglevel=info
   ```

```bash
pytest
```

## 🤝 贡献指南 / Contribution Guide

我们欢迎各种形式的贡献！
We welcome all forms of contributions!

### 如何贡献 / How to Contribute

1. Fork 本项目 / Fork this project
2. 创建特性分支 / Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 提交更改 / Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 / Push to the branch (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request / Create a Pull Request

### 贡献类别 / Contribution Categories

- 🐛 Bug 修复 / Bug fixes
- ✨ 新功能开发 / New feature development
- 📝 文档改进 / Documentation improvements
- 🎨 UI/UX 优化 / UI/UX optimization
- ⚡ 性能优化 / Performance optimization
- 🧪 测试用例 / Test cases

## 📄 许可证 / License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎖️ 致谢 / Acknowledgements

- 感谢 [Flask](https://flask.palletsprojects.com/) 提供优秀的Web框架 / Thanks to [Flask](https://flask.palletsprojects.com/) for providing an excellent web framework
- 感谢 [jieba](https://github.com/fxsjy/jieba) 提供中文分词支持 / Thanks to [jieba](https://github.com/fxsjy/jieba) for Chinese word segmentation support
- 感谢 [Plotly](https://plotly.com/python/) 提供强大的可视化能力 / Thanks to [Plotly](https://plotly.com/python/) for powerful visualization capabilities
- 感谢 [Tailwind CSS](https://tailwindcss.com/) 提供优雅的样式框架 / Thanks to [Tailwind CSS](https://tailwindcss.com/) for an elegant styling framework

## 📞 联系方式 / Contact

- 项目维护者: [Your Name]
- 邮箱: your.email@example.com
- 项目地址: https://github.com/your-username/regional-industrial-dashboard

---
⭐ 如果这个项目对您有帮助，请给我们一个 Star！
⭐ If this project is helpful to you, please give us a Star!