#!/usr/bin/env python3
"""
Final Validation Test for Regional Industrial Dashboard Application
Tests all file types processing and core functionality.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import application modules
from src.analysis.text_processor import TextProcessor
from src.visualization.dashboard_generator import DashboardGenerator

def test_file_processing():
    """Test processing of all supported file types."""
    print("🧪 Testing file processing for all supported formats...")
    
    # Sample test content
    sample_text = """
    区域产业发展分析报告
    
    产业概述：
    人工智能产业是当前最具发展潜力的战略性新兴产业之一。近年来，随着大数据、云计算等技术的快速发展，
    人工智能在各个领域的应用不断深化，形成了良好的发展态势。
    
    政策环境：
    国家出台了一系列支持人工智能发展的政策措施，包括《新一代人工智能发展规划》等重要文件，
    为产业发展提供了强有力的政策保障。
    
    市场规模：
    据统计，2025年中国人工智能市场规模达到5000亿元人民币，预计未来五年年均增长率将保持在25%以上。
    """
    
    processor = TextProcessor()
    
    # Test TXT file processing
    print("\n📄 Testing TXT file processing...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(sample_text)
        txt_file_path = f.name
    
    try:
        txt_result = processor.analyze_file(txt_file_path)
        assert txt_result is not None, "TXT file processing should return result"
        assert 'categories' in txt_result, "Result should contain categories"
        print("✅ TXT file processing test passed")
        
        # Test dashboard generation with TXT result
        generator = DashboardGenerator()
        dashboard_data = generator.generate_dashboard_data(txt_result)
        assert dashboard_data is not None, "Dashboard generation should return data"
        assert 'title' in dashboard_data, "Dashboard should have title"
        assert 'summary' in dashboard_data, "Dashboard should have summary"
        print("✅ Dashboard generation from TXT data test passed")
        
    finally:
        os.unlink(txt_file_path)
    
    # Test MD file processing
    print("\n📝 Testing MD file processing...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(sample_text)
        md_file_path = f.name
    
    try:
        md_result = processor.analyze_file(md_file_path)
        assert md_result is not None, "MD file processing should return result"
        assert 'categories' in md_result, "Result should contain categories"
        print("✅ MD file processing test passed")
    finally:
        os.unlink(md_file_path)
    
    # Test JSON file processing
    print("\n🔍 Testing JSON file processing...")
    json_content = {"content": sample_text, "title": "测试报告"}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(json_content, f, ensure_ascii=False, indent=2)
        json_file_path = f.name
    
    try:
        json_result = processor.analyze_file(json_file_path)
        assert json_result is not None, "JSON file processing should return result"
        assert 'categories' in json_result, "Result should contain categories"
        print("✅ JSON file processing test passed")
    finally:
        os.unlink(json_file_path)
    
    print("\n🎉 All file processing tests passed!")

def test_error_handling():
    """Test error handling scenarios."""
    print("\n🛡️  Testing error handling...")
    
    processor = TextProcessor()
    generator = DashboardGenerator()
    
    # Test processing non-existent file
    result = processor.analyze_file("/non/existent/file.txt")
    assert result is None, "Should return None for non-existent file"
    
    # Test dashboard generation with empty data
    empty_result = generator.generate_dashboard_data({})
    assert empty_result is not None, "Should handle empty data gracefully"
    assert 'title' in empty_result, "Empty dashboard should still have title"
    
    print("✅ Error handling test passed!")

def main():
    """Run all validation tests."""
    print("🚀 Starting final validation testing...")
    print("=" * 60)
    
    try:
        test_file_processing()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 All validation tests passed! The application is functioning correctly.")
        return 0
    except Exception as e:
        print(f"\n❌ Validation test failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())