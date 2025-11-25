# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

### Development Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python industry_analysis.py
```

### Common Development Tasks
```bash
# Run the Flask application in development mode
python industry_analysis.py

# Access the application
# http://localhost:5000

# Check Python syntax and imports
python -m py_compile industry_analysis.py
python -m py_compile src/analysis/text_processor.py
python -m py_compile src/visualization/dashboard_generator.py

# Test file processing manually
python -c "from src.analysis.text_processor import TextProcessor; tp = TextProcessor(); print('TextProcessor loaded successfully')"

# Validate configuration
python -c "import json; print(json.load(open('config.json', 'r', encoding='utf-8')))"
```

### Directory Structure Commands
```bash
# Create necessary directories if they don't exist
mkdir -p data/input data/output

# List recent analysis results
ls -la data/output/

# Clean up old analysis files (older than 7 days)
find data/output -name "*.json" -mtime +7 -delete
```

## Architecture

### Application Structure
This is a Flask-based web application for regional industrial analysis with Chinese text processing capabilities. The architecture follows a modular design:

**Core Components:**
- `industry_analysis.py` - Main Flask application with routes and web interface
- `src/analysis/text_processor.py` - Text processing engine using jieba for Chinese NLP
- `src/visualization/dashboard_generator.py` - Chart generation using Plotly
- `config.json` - Configurable analysis categories and AI integration focus areas

**Data Flow:**
1. Users upload documents (.txt, .md, .json, .docx, .pdf) via web interface
2. `TextProcessor` extracts and analyzes content using Chinese NLP (jieba)
3. Content is categorized based on configurable industry categories
4. AI integration opportunities are identified and scored
5. `DashboardGenerator` creates interactive visualizations using Plotly
6. Results are saved as JSON and displayed in web dashboard

**Key Processing Features:**
- Chinese text segmentation and keyword extraction
- Industry-specific term recognition
- Content categorization by relevance scoring
- AI application opportunity analysis
- Statistical analysis and visualization generation

### Template System
The application uses Jinja2 templates with a base template pattern:
- `base.html` - Common layout and styling
- `index.html` - Dashboard home with recent analysis list
- `upload.html` - File upload interface with drag-and-drop
- `analysis.html` - Results display with charts and categorized content
- `settings.html` - Configuration management for categories and AI focus areas

### Configuration Management
The system uses `config.json` for runtime configuration:
- `categories` - Industry analysis categories (产业概述, 政策环境, etc.)
- `ai_integration_focus` - AI application scenarios (智能制造, 数据分析, etc.)

Categories and AI focus areas can be customized through the web interface at `/settings`.

## Development Notes

### Chinese Text Processing
- Uses jieba library for Chinese word segmentation
- Custom industry terminology is loaded at initialization
- Text cleaning handles Chinese punctuation and characters specifically
- Content relevance scoring is based on keyword matching with configurable categories

### File Processing Support
The system supports multiple input formats:
- `.txt`, `.md` - Plain text and Markdown
- `.json` - Structured data with text extraction
- `.docx` - Word documents via python-docx
- `.pdf` - PDF text extraction via PyPDF2

### Data Storage
- Input files: `data/input/` (timestamped filenames)
- Analysis results: `data/output/` (JSON format with visualization data)
- Configuration: `config.json` (runtime editable via web interface)

### Error Handling
The application includes comprehensive error handling:
- File upload validation and size limits (16MB max)
- Text processing error recovery
- Chart generation fallbacks
- Configuration loading with defaults

### Visualization Integration
Uses Plotly.js for interactive charts:
- Category distribution (donut charts)
- AI opportunity analysis (radar charts) 
- Keyword frequency analysis (bar charts)
- Statistical overviews

When modifying visualization code, ensure Plotly JSON serialization compatibility and Chinese character encoding support.

### Performance Considerations
- Large text files may require memory optimization
- Chinese text processing can be CPU intensive for long documents
- Consider implementing file size warnings for documents over 5MB
- Analysis results are cached as JSON files to avoid reprocessing