#!/usr/bin/env python3
"""
New Modules Test Script
Test newly added modules: Map Visualizer, Trend Analyzer, Comparison Analyzer
"""

import os
import sys
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("🧪 新模块测试 - 地图可视化、趋势分析、对比分析")
print("=" * 60)

total_tests = 0
passed_tests = 0
failed_tests = 0

# Test 1: Map Visualizer
print("\n✓ 测试 1: 地图可视化模块")
total_tests += 1
try:
    from src.visualization.map_visualizer import MapVisualizer
    
    visualizer = MapVisualizer()
    
    # Test province map
    province_data = {"四川": 100, "北京": 120, "上海": 110}
    province_map = visualizer.generate_province_map(province_data, "产业分布")
    assert 'title' in province_map, "Province map should have title"
    assert 'series' in province_map, "Province map should have series"
    print(f"  - 省份地图生成成功 ({len(province_data)} 个省份)")
    
    # Test 3D bar chart
    bar_data = [
        {"x": "人工智能", "y": "成都", "z": 100},
        {"x": "人工智能", "y": "北京", "z": 150},
        {"x": "大数据", "y": "成都", "z": 80}
    ]
    bar_3d = visualizer.generate_3d_bar_chart(bar_data, "产业对比")
    assert 'series' in bar_3d, "3D bar should have series"
    assert 'grid3D' in bar_3d, "3D bar should have 3D grid"
    print(f"  - 3D柱状图生成成功 ({len(bar_data)} 个数据点)")
    
    # Test industry network
    nodes = [
        {"id": "1", "name": "企业A", "category": 0, "value": 100},
        {"id": "2", "name": "企业B", "category": 1, "value": 80}
    ]
    links = [{"source": "1", "target": "2", "value": 10}]
    network = visualizer.generate_industry_network(nodes, links)
    assert 'series' in network, "Network should have series"
    print(f"  - 产业网络图生成成功 ({len(nodes)} 节点, {len(links)} 连接)")
    
    # Test geo scatter
    geo_data = [
        {"name": "成都", "value": [104.06, 30.67, 100]},
        {"name": "北京", "value": [116.41, 39.90, 120]}
    ]
    geo_scatter = visualizer.generate_geo_scatter(geo_data)
    assert 'geo' in geo_scatter, "Geo scatter should have geo component"
    print(f"  - 地理散点图生成成功 ({len(geo_data)} 个城市)")
    
    print("  ✅ 通过 - 地图可视化模块功能正常")
    passed_tests += 1
except Exception as e:
    print(f"  ❌ 失败 - {e}")
    import traceback
    traceback.print_exc()
    failed_tests += 1

# Test 2: Trend Analyzer
print("\n✓ 测试 2: 趋势分析模块")
total_tests += 1
try:
    from src.analysis.trend_analyzer import TrendAnalyzer
    
    analyzer = TrendAnalyzer()
    
    # Add sample reports
    test_reports = [
        {
            "id": "report1",
            "time": "2023-01-01",
            "content": "市场规模达到500亿元，增长率15%，企业200家"
        },
        {
            "id": "report2",
            "time": "2023-06-01",
            "content": "市场规模达到550亿元，增长率18%，企业220家"
        },
        {
            "id": "report3",
            "time": "2024-01-01",
            "content": "市场规模达到600亿元，增长率20%，企业250家"
        }
    ]
    
    for report in test_reports:
        analyzer.add_historical_report(
            report['id'],
            {"content": report['content']},
            report['time']
        )
    
    print(f"  - 添加了 {len(test_reports)} 份历史报告")
    
    # Test trend calculation
    trend = analyzer.calculate_trend("market_size")
    assert 'trend_direction' in trend, "Trend should have direction"
    assert 'values' in trend, "Trend should have values"
    print(f"  - 趋势分析成功: {trend['trend_direction']} (平均增长率: {trend.get('avg_growth_rate', 0):.2f}%)")
    
    # Test prediction
    prediction = analyzer.predict_future("market_size", 6)
    assert 'predicted_values' in prediction, "Should have predictions"
    assert len(prediction['predicted_values']) == 6, "Should have 6 predictions"
    print(f"  - 未来预测成功: 预测未来 {len(prediction['predicted_values'])} 个时期")
    
    # Test chart generation
    chart = analyzer.generate_trend_chart_config("market_size")
    assert 'series' in chart, "Chart should have series"
    assert 'xAxis' in chart, "Chart should have xAxis"
    print(f"  - 趋势图表配置生成成功")
    
    print("  ✅ 通过 - 趋势分析模块功能正常")
    passed_tests += 1
except Exception as e:
    print(f"  ❌ 失败 - {e}")
    import traceback
    traceback.print_exc()
    failed_tests += 1

# Test 3: Comparison Analyzer
print("\n✓ 测试 3: 对比分析模块")
total_tests += 1
try:
    from src.analysis.comparison_analyzer import ComparisonAnalyzer
    
    analyzer = ComparisonAnalyzer()
    
    # Add sample reports
    report1 = {
        "content": "成都人工智能产业市场规模达到500亿元，增长率20%，企业300家，投资100亿元。人工智能、大数据。"
    }
    
    report2 = {
        "content": "北京人工智能产业市场规模达到800亿元，增长率25%，企业500家，投资200亿元。人工智能、云计算、5G。"
    }
    
    report3 = {
        "content": "上海人工智能产业市场规模达到650亿元，增长率22%，企业400家，投资150亿元。人工智能、物联网。"
    }
    
    analyzer.add_report("report1", report1, {"name": "成都AI", "city": "成都"})
    analyzer.add_report("report2", report2, {"name": "北京AI", "city": "北京"})
    analyzer.add_report("report3", report3, {"name": "上海AI", "city": "上海"})
    
    print(f"  - 添加了 3 份对比报告")
    
    # Test comparison
    comparison = analyzer.compare_reports()
    assert 'total_reports' in comparison, "Should have report count"
    assert comparison['total_reports'] == 3, "Should have 3 reports"
    assert 'metric_comparison' in comparison, "Should have metric comparison"
    assert 'rankings' in comparison, "Should have rankings"
    print(f"  - 对比分析成功: {comparison['total_reports']} 份报告")
    print(f"  - 对比指标数: {len(comparison['metric_comparison'])}")
    
    # Test radar chart
    radar = analyzer.generate_radar_chart()
    assert 'radar' in radar, "Radar should have radar component"
    assert 'series' in radar, "Radar should have series"
    print(f"  - 雷达图生成成功")
    
    # Test comparison chart
    if 'market_size' in comparison['metric_comparison']:
        chart = analyzer.generate_comparison_chart("market_size")
        assert 'series' in chart, "Comparison chart should have series"
        print(f"  - 对比柱状图生成成功")
    
    # Test text report
    text_report = analyzer.generate_comparison_report()
    assert len(text_report) > 0, "Should generate text report"
    assert "多文档对比分析报告" in text_report, "Should have report title"
    print(f"  - 文字报告生成成功 ({len(text_report)} 字符)")
    
    # Show top ranking
    if comparison['rankings']['overall']:
        top = comparison['rankings']['overall'][0]
        print(f"  - 综合排名第一: {top['report_name']} (得分: {top['score']:.2f})")
    
    print("  ✅ 通过 - 对比分析模块功能正常")
    passed_tests += 1
except Exception as e:
    print(f"  ❌ 失败 - {e}")
    import traceback
    traceback.print_exc()
    failed_tests += 1

# Test 4: Integration test - All modules working together
print("\n✓ 测试 4: 模块集成测试")
total_tests += 1
try:
    # Check if all modules can be imported together
    from src.visualization.map_visualizer import MapVisualizer
    from src.analysis.trend_analyzer import TrendAnalyzer
    from src.analysis.comparison_analyzer import ComparisonAnalyzer
    
    # Create instances
    map_viz = MapVisualizer()
    trend_an = TrendAnalyzer()
    comp_an = ComparisonAnalyzer()
    
    print("  - 所有模块可以同时导入和初始化")
    print("  - 地图可视化器: ✓")
    print("  - 趋势分析器: ✓")
    print("  - 对比分析器: ✓")
    
    print("  ✅ 通过 - 模块集成正常")
    passed_tests += 1
except Exception as e:
    print(f"  ❌ 失败 - {e}")
    failed_tests += 1

# Summary
print("\n" + "=" * 60)
print("📊 新模块测试总结")
print("=" * 60)
print(f"总测试项: {total_tests}")
print(f"✅ 通过: {passed_tests}")
print(f"❌ 失败: {failed_tests}")

if failed_tests == 0:
    print("\n🎉 所有新模块测试通过！")
    print("\n新增功能:")
    print("  ✅ 3D可视化与地图 (ECharts集成)")
    print("  ✅ 趋势预测与时间序列分析")
    print("  ✅ 多文档对比分析")
    print("\n这些模块已集成到 app_enhanced.py")
    print("可通过以下API端点访问:")
    print("  - /api/report/<id>/visualizations")
    print("  - /api/trend-analysis")
    print("  - /api/comparison")
else:
    print(f"\n⚠️  有 {failed_tests} 个测试失败，请检查错误信息")

print("\n" + "=" * 60)
print("✨ 测试完成！")
