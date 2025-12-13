#!/usr/bin/env python3
"""
Script to fix the poi_map selector in comprehensive_demo.yaml
"""

def fix_demo_yaml():
    """Fix the selector in comprehensive_demo.yaml"""
    demo_yaml_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/scenarios/comprehensive_demo.yaml"
    
    # Read the current content
    with open(demo_yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic section and fix it
    old_selector = """  # 5. 地图看板功能 (Map Dashboard)
  - action: click
    selector: "a[href*='poi_map']"
    description: "点击'地图看板'按钮"
    subtitle: "模块三：GIS地理信息可视化看板，透视产业空间布局"
    fallback:
      - selector: "text=地图看板"""
    
    new_selector = """  # 5. 地图看板功能 (Map Dashboard)
  - action: click
    selector: "a[href='/poi-map-visualization']"
    description: "点击'地图看板'按钮"
    subtitle: "模块三：GIS地理信息可视化看板，透视产业空间布局"
    fallback:
      - selector: "a[href*='poi-map']"
      - selector: "text=地图看板"""
    
    # Replace the old code with the new code
    updated_content = content.replace(old_selector, new_selector)
    
    # Write back the updated content
    with open(demo_yaml_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Successfully updated comprehensive_demo.yaml with correct selector!")


if __name__ == "__main__":
    fix_demo_yaml()