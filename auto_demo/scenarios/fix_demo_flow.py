#!/usr/bin/env python3
"""
Script to fix the flow in comprehensive_demo.yaml to navigate back to home before clicking map dashboard
"""

def fix_demo_flow():
    """Fix the flow in comprehensive_demo.yaml to return to home page before clicking map dashboard"""
    demo_yaml_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/scenarios/comprehensive_demo.yaml"
    
    # Read the current content
    with open(demo_yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic section and fix the flow
    old_flow = """  - action: scroll_smooth
    direction: "down"
    duration: 5
    description: "浏览解析结果（下半部分）"
    subtitle: "核心结论自动提炼，辅助您快速进行科学决策"

  # 5. 地图看板功能 (Map Dashboard)
  - action: click
    selector: "a[href='/poi-map-visualization']"
    description: "点击'地图看板'按钮"
    subtitle: "模块三：GIS地理信息可视化看板，透视产业空间布局"
    fallback:
      - selector: "a[href*='poi-map']"
      - selector: "text=地图看板""""
    
    new_flow = """  - action: scroll_smooth
    direction: "down"
    duration: 5
    description: "浏览解析结果（下半部分）"
    subtitle: "核心结论自动提炼，辅助您快速进行科学决策"

  # Return to home page to access main navigation
  - action: navigate
    url: "/"
    description: "返回首页，访问主导航菜单"
    subtitle: "返回平台主页，准备进入地图可视化模块"
  
  - action: wait
    duration: 3
    description: "等待首页加载"
    subtitle: "主界面加载完成，导航菜单已就绪"

  # 5. 地图看板功能 (Map Dashboard)
  - action: click
    selector: "a[href='/poi-map-visualization']"
    description: "点击'地图看板'按钮"
    subtitle: "模块三：GIS地理信息可视化看板，透视产业空间布局"
    fallback:
      - selector: "a[href*='poi-map']"
      - selector: "text=地图看板"""
    
    # Replace the old flow with the new flow
    updated_content = content.replace(old_flow, new_flow)
    
    # Write back the updated content
    with open(demo_yaml_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Successfully updated comprehensive_demo.yaml to navigate back to home before map dashboard!")


if __name__ == "__main__":
    fix_demo_flow()