#!/usr/bin/env python3
"""
Test script to verify the fix for JSON serialization error in dashboard generator.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.visualization.dashboard_generator import DashboardGenerator

def test_empty_ai_opportunities():
    """Test that empty AI opportunities chart data is JSON serializable."""
    print("Testing empty AI opportunities chart data...")
    
    generator = DashboardGenerator()
    
    # Test with empty AI opportunities
    empty_ai_data = {}
    chart_data = generator._create_ai_radar_chart(empty_ai_data)
    
    # Verify the structure
    assert 'data' in chart_data, "Chart data should have 'data' key"
    assert 'layout' in chart_data, "Chart data should have 'layout' key"
    assert len(chart_data['data']) > 0, "Chart data should have at least one data series"
    
    # Verify that the data is serializable (this would fail before the fix)
    import json
    try:
        json.dumps(chart_data)
        print("✅ Empty AI opportunities chart data is JSON serializable")
    except TypeError as e:
        print(f"❌ Empty AI opportunities chart data is NOT JSON serializable: {e}")
        return False
    
    return True

def test_empty_pos_data():
    """Test that empty POS chart data is JSON serializable."""
    print("Testing empty POS chart data...")
    
    generator = DashboardGenerator()
    
    # Test with empty POS data
    empty_pos_data = []
    chart_data = generator._create_pos_chart(empty_pos_data)
    
    # Verify the structure
    assert 'data' in chart_data, "Chart data should have 'data' key"
    assert 'layout' in chart_data, "Chart data should have 'layout' key"
    assert len(chart_data['data']) > 0, "Chart data should have at least one data series"
    
    # Verify that the data is serializable (this would fail before the fix)
    import json
    try:
        json.dumps(chart_data)
        print("✅ Empty POS chart data is JSON serializable")
    except TypeError as e:
        print(f"❌ Empty POS chart data is NOT JSON serializable: {e}")
        return False
    
    return True

def test_dashboard_generation_with_empty_data():
    """Test dashboard generation with minimal analysis data."""
    print("Testing dashboard generation with minimal data...")
    
    generator = DashboardGenerator()
    
    # Minimal analysis result
    minimal_analysis = {
        'categories': {},
        'key_insights': [],
        'ai_opportunities': {},
        'statistics': {},
        'sentiment_analysis': {},
        'metadata': {}
    }
    
    dashboard_data = generator.generate_dashboard_data(minimal_analysis)
    
    # Verify dashboard structure
    assert 'title' in dashboard_data, "Dashboard should have title"
    assert 'summary' in dashboard_data, "Dashboard should have summary"
    assert 'charts' in dashboard_data, "Dashboard should have charts"
    
    # Verify that the dashboard data is serializable
    import json
    try:
        json.dumps(dashboard_data)
        print("✅ Dashboard data with minimal analysis is JSON serializable")
    except TypeError as e:
        print(f"❌ Dashboard data with minimal analysis is NOT JSON serializable: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting tests for dashboard generator JSON serialization fix...")
    print("=" * 60)
    
    tests = [
        test_empty_ai_opportunities,
        test_empty_pos_data,
        test_dashboard_generation_with_empty_data
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
        print("🎉 All tests passed! The JSON serialization issue has been fixed.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())