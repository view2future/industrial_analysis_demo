#!/usr/bin/env python3
"""
Script to fix the flow in comprehensive_demo.yaml to navigate back to home before clicking policy analysis
"""

def fix_policy_flow():
    """Fix the flow to navigate back to home before clicking policy analysis"""
    demo_yaml_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/scenarios/comprehensive_demo.yaml"
    
    # Read the current content
    with open(demo_yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic section and fix the flow
    old_flow = """  - action: wait
    duration: 5
    description: "等待POI加载"
    subtitle: "企业机构精准落点，一图统览区域产业生态全貌"

  # 6. 政策解读功能 (Policy Interpretation)
  - action: click
    selector: "a[href*='policy']"
    description: "点击'政策解读'按钮"
    subtitle: "模块四：智能政策解读助手，不仅是搜索，更是解读"
    fallback:
      - selector: "text=政策解读\""""
    
    new_flow = """  - action: wait
    duration: 5
    description: "等待POI加载"
    subtitle: "企业机构精准落点，一图统览区域产业生态全貌"

  # Return to home page to access main navigation
  - action: navigate
    url: "/"
    description: "返回首页，访问主导航菜单"
    subtitle: "返回平台主页，准备进入政策解读模块"
  
  - action: wait
    duration: 3
    description: "等待首页加载"
    subtitle: "主界面加载完成，导航菜单已就绪"

  # 6. 政策解读功能 (Policy Interpretation)
  - action: click
    selector: "a[href*='policy']"
    description: "点击'政策解读'按钮"
    subtitle: "模块四：智能政策解读助手，不仅是搜索，更是解读"
    fallback:
      - selector: "text=政策解读\""""
    
    # Replace the old flow with the new flow
    # More precise replacement since the quotes are tricky
    if old_flow.replace('\\"', '"') in content:
        updated_content = content.replace(old_flow.replace('\\"', '"'), new_flow.replace('\\"', '"'))
    else:
        # Alternative: just replace the core section without the problematic quotes
        old_core = """  - action: wait
    duration: 5
    description: "等待POI加载"
    subtitle: "企业机构精准落点，一图统览区域产业生态全貌"

  # 6. 政策解读功能 (Policy Interpretation)
  - action: click
    selector: "a[href*='policy']"
    description: "点击'政策解读'按钮"
    subtitle: "模块四：智能政策解读助手，不仅是搜索，更是解读"
    fallback:
      - selector: "text=政策解读"""
        
        new_core = """  - action: wait
    duration: 5
    description: "等待POI加载"
    subtitle: "企业机构精准落点，一图统览区域产业生态全貌"

  # Return to home page to access main navigation
  - action: navigate
    url: "/"
    description: "返回首页，访问主导航菜单"
    subtitle: "返回平台主页，准备进入政策解读模块"
  
  - action: wait
    duration: 3
    description: "等待首页加载"
    subtitle: "主界面加载完成，导航菜单已就绪"

  # 6. 政策解读功能 (Policy Interpretation)
  - action: click
    selector: "a[href*='policy']"
    description: "点击'政策解读'按钮"
    subtitle: "模块四：智能政策解读助手，不仅是搜索，更是解读"
    fallback:
      - selector: "text=政策解读"""
        
        updated_content = content.replace(old_core, new_core)
    
    # Write back the updated content
    with open(demo_yaml_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Successfully updated comprehensive_demo.yaml to navigate back to home before policy analysis!")


if __name__ == "__main__":
    fix_policy_flow()