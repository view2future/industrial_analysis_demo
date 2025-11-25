#!/usr/bin/env python3
"""
Test script to verify all improvements to the report page.
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_export_improvements():
    """Test that export improvements work correctly."""
    print("Testing export improvements...")
    
    # Load actual report data
    with open('data/output/20251105_113016_analysis.json', 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    # Check that report data has the expected structure for improved export
    expected_keys = ['title', 'summary', 'charts', 'categories', 'key_insights', 'ai_opportunities']
    for key in expected_keys:
        if key not in report_data:
            print(f"❌ Missing key {key} in report data")
            return False
    
    # Check summary structure
    if 'summary' in report_data:
        summary = report_data['summary']
        if isinstance(summary, dict):
            # Should have key metrics
            metrics_keys = ['word_count', 'reading_time', 'categories_analyzed']
            for key in metrics_keys:
                if key in summary:
                    print(f"✅ Summary has {key}: {summary[key]}")
    
    # Check categories structure
    if 'categories' in report_data:
        for cat_name, cat_data in report_data['categories'].items():
            if 'relevance_score' in cat_data:
                print(f"✅ Category {cat_name} has relevance score: {cat_data['relevance_score']}")
                break
    
    # Check AI opportunities structure
    if 'ai_opportunities' in report_data:
        for ai_name, ai_data in report_data['ai_opportunities'].items():
            if all(key in ai_data for key in ['potential_score', 'priority_level', 'recommendation']):
                print(f"✅ AI opportunity {ai_name} has complete data structure")
                break
    
    # Check charts structure
    if 'charts' in report_data:
        charts = report_data['charts']
        chart_types = ['category_distribution', 'ai_opportunities', 'keyword_frequency']
        for chart_type in chart_types:
            if chart_type in charts:
                chart_data = charts[chart_type]
                if 'data' in chart_data and len(chart_data['data']) > 0:
                    print(f"✅ Chart {chart_type} has data structure")
    
    print("✅ Export improvements test passed")
    return True

def test_pos_analysis_removal():
    """Test that POS analysis has been removed."""
    print("Testing POS analysis removal...")
    
    # Load the test result file we just generated
    with open('tests/fixtures/test_pos_removal_result.json', 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    # Check key insights for POS analysis
    if 'key_insights' in report_data:
        pos_found = False
        for insight in report_data['key_insights']:
            if isinstance(insight, dict) and insight.get('type') == 'pos_analysis':
                pos_found = True
                break
        
        if not pos_found:
            print("✅ POS analysis correctly removed from key insights")
            return True
        else:
            print("❌ POS analysis still present in key insights")
            return False
    else:
        print("❌ No key insights found")
        return False

def test_title_improvement():
    """Test that title improvement works correctly."""
    print("Testing title improvement...")
    
    from src.visualization.dashboard_generator import DashboardGenerator
    
    # Test with a long filename
    long_filename = "20251105_113016_20251105_112739_20251105_101832_wuhan_smart_manufacturing_report"
    
    analysis_result = {
        'metadata': {
            'source_file': f"{long_filename}.txt"
        }
    }
    
    generator = DashboardGenerator()
    title = generator._generate_title(analysis_result)
    
    print(f"Generated title: {title}")
    
    # Check that title is reasonably short and clean
    if len(title) <= 100 and 'AIPE区域产业分析小工作台' in title:
        # Remove the suffix to check the main part
        main_title = title.replace(' - AIPE区域产业分析小工作台', '')
        if len(main_title) <= 50:
            print("✅ Title improvement working correctly")
            return True
        else:
            print("❌ Title is still too long")
            return False
    else:
        print("❌ Title format is incorrect")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing all improvements to the report page...")
    print("=" * 60)
    
    tests = [
        test_export_improvements,
        test_pos_analysis_removal,
        test_title_improvement
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
        print("🎉 All tests passed! All improvements are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())