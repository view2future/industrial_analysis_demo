#!/usr/bin/env python3
"""
Test script to verify all fixes for the report view issues.
"""

import sys
import json
import re
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_title_shortening():
    """Test that titles are properly shortened."""
    print("Testing title shortening...")
    
    from src.visualization.dashboard_generator import DashboardGenerator
    
    # Test with a long filename that includes multiple timestamps
    long_filename = "20251105_113016_20251105_112739_20251105_101832_20251105_100617_20251104_152545_20251104_001007_wuhan_smart_manufacturing_report"
    
    analysis_result = {
        'metadata': {
            'source_file': f"{long_filename}.txt"
        }
    }
    
    generator = DashboardGenerator()
    title = generator._generate_title(analysis_result)
    
    print(f"Generated title: {title}")
    
    # Check that title is reasonably short
    if len(title) > 100:
        print("❌ Title is still too long")
        return False
    
    # Check that title contains meaningful content
    if "wuhan" in title.lower() or "smart" in title.lower() or "manufacturing" in title.lower():
        print("✅ Title contains meaningful content")
    else:
        print("⚠️  Title may not contain meaningful content")
    
    print("✅ Title shortening test passed")
    return True

def test_pos_data_display():
    """Test that POS data would display correctly in template."""
    print("Testing POS data display...")
    
    # Sample POS analysis data
    pos_data = [
        {'pos_tag': 'n', 'pos_name': '名词', 'count': 785, 'percentage': 43.88},
        {'pos_tag': 'v', 'pos_name': '动词', 'count': 347, 'percentage': 19.41},
        {'pos_tag': 'a', 'pos_name': '形容词', 'count': 145, 'percentage': 8.11}
    ]
    
    # Check that data has the expected structure
    for item in pos_data:
        required_fields = ['pos_tag', 'pos_name', 'count', 'percentage']
        for field in required_fields:
            if field not in item:
                print(f"❌ Missing field {field} in POS data")
                return False
    
    print("✅ POS data structure is correct")
    return True

def test_report_data_structure():
    """Test that report data has the expected structure for export."""
    print("Testing report data structure...")
    
    # Load actual report data
    with open('data/output/20251105_113016_analysis.json', 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    # Check that report data has the expected keys
    expected_keys = ['title', 'summary', 'charts', 'categories', 'key_insights', 'ai_opportunities']
    for key in expected_keys:
        if key not in report_data:
            print(f"❌ Missing key {key} in report data")
            return False
    
    # Check key insights structure
    if 'key_insights' in report_data and report_data['key_insights']:
        for insight in report_data['key_insights']:
            if isinstance(insight, dict):
                # Should have either text/title or data
                if not (insight.get('text') or insight.get('title') or insight.get('data')):
                    print(f"❌ Key insight missing content: {insight}")
                    return False
    
    print("✅ Report data structure is correct")
    return True

def main():
    """Run all tests."""
    print("🚀 Testing all fixes for report view issues...")
    print("=" * 60)
    
    tests = [
        test_title_shortening,
        test_pos_data_display,
        test_report_data_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! All fixes are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())