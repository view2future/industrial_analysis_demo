#!/usr/bin/env python3
"""
Test script to verify file creation in the same way as the celery task
"""

import json
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test parameters
report_id = "llm_report_20251104_015136"
city = "测试城市"
industry = "测试行业"

# Set up paths (same as in the celery task)
app_root_path = "/Users/wangyu94/regional-industrial-dashboard"
output_dir = Path(app_root_path) / 'data' / 'output' / 'llm_reports'
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / f"{report_id}.json"

# Create test report data (simplified version of what the celery task creates)
final_report = {
    'report_id': report_id,
    'city': city,
    'industry': industry,
    'generated_at': datetime.now().isoformat(),
    'full_content': '测试内容',
    'sections': {'section1': '内容1'},
    'summary': {
        'zh': '中文摘要',
        'en': 'English summary'
    },
    'swot_analysis': {'strengths': ['优势1']},
    'metadata': {
        'model': 'test_model',
        'llm_service': 'test',
        'user_id': 'test_user',
        'additional_context': '测试上下文'
    }
}

# Try to save the file (same as in celery task)
logger.info(f"Saving report to: {output_path}")
try:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ Report saved successfully: {output_path}")
    logger.info(f"📏 File size: {output_path.stat().st_size / 1024:.2f} KB")
    
    # Verify the file exists and can be read
    with open(output_path, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    logger.info(f"✅ File verification successful, loaded {len(loaded_data)} keys")
    
    # Clean up - remove the test file
    output_path.unlink()
    logger.info("🧹 Test file cleaned up")
    
except Exception as e:
    logger.error(f"❌ Error during file operations: {e}")
    import traceback
    logger.error(traceback.format_exc())