#!/usr/bin/env python3
"""
Script to slow down the scrolling speed for upload analysis results
"""

def slow_scroll_speed():
    """Slow down the scrolling speed for upload analysis results"""
    demo_yaml_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/scenarios/comprehensive_demo.yaml"
    
    # Read the current content
    with open(demo_yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the scroll duration from 5 to 8 seconds for upload analysis results
    # First scroll action: "浏览解析结果（上半部分）"
    content = content.replace(
        '  - action: scroll_smooth\n    direction: "down"\n    duration: 5\n    description: "浏览解析结果（上半部分）"',
        '  - action: scroll_smooth\n    direction: "down"\n    duration: 8\n    description: "浏览解析结果（上半部分）"'
    )
    
    # Second scroll action: "浏览解析结果（下半部分）" 
    content = content.replace(
        '  - action: scroll_smooth\n    direction: "down"\n    duration: 5\n    description: "浏览解析结果（下半部分）"',
        '  - action: scroll_smooth\n    direction: "down"\n    duration: 8\n    description: "浏览解析结果（下半部分）"'
    )
    
    # Write back the updated content
    with open(demo_yaml_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Successfully updated scroll durations to 8 seconds for better visibility!")


if __name__ == "__main__":
    slow_scroll_speed()