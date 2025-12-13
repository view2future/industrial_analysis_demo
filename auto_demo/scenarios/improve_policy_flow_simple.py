#!/usr/bin/env python3
"""
Script to improve the policy analysis flow with longer waits
"""

def improve_policy_analysis_flow():
    """Improve the policy analysis flow in the comprehensive demo"""
    demo_yaml_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/scenarios/comprehensive_demo.yaml"
    
    # Read the current content
    with open(demo_yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic section and fix the flow
    old_flow = """  - action: click
    selector: "a[href*='policy']"
    description: "点击'政策解读'按钮"
    subtitle: "模块四：智能政策解读助手，不仅是搜索，更是解读"
    fallback:
      - selector: "text=政策解读"

  - action: wait
    duration: 5
    description: "等待政策分析页面完全加载"
    subtitle: "政策分析页面初始化完成，检索功能就绪"

  # Make sure the search tab is active (in case there are multiple tabs)
  - action: click
    selector: "#search-tab"
    description: "确保智能检索标签页激活"
    subtitle: "切换到政策智能检索界面"
    optional: true  # This might already be active

  - action: wait
    duration: 2
    description: "等待检索界面加载"
    subtitle: "检索界面加载完成，输入框已就绪"

  - action: click
    selector: "#searchPoliciesBtn"
    description: "点击'开始检索'"
    subtitle: "多维政策检索引擎，覆盖央地各级产业政策文件\""""
    
    new_flow = """  - action: click
    selector: "a[href*='policy']"
    description: "点击'政策解读'按钮"
    subtitle: "模块四：智能政策解读助手，不仅是搜索，更是解读"
    fallback:
      - selector: "text=政策解读"

  - action: wait
    duration: 8
    description: "等待政策分析页面完全加载"
    subtitle: "政策分析页面初始化完成，检索功能就绪"

  # Wait for content to be ready before trying to click tabs
  - action: wait
    duration: 3
    description: "等待页面内容初始化"
    subtitle: "页面内容初始化完成"

  # Make sure the search tab is active (in case there are multiple tabs)
  - action: click
    selector: "#search-tab"
    description: "确保智能检索标签页激活"
    subtitle: "切换到政策智能检索界面"
    optional: true  # This might already be active

  - action: wait
    duration: 4
    description: "等待检索界面加载"
    subtitle: "检索界面加载完成，输入框已就绪"

  - action: click
    selector: "#searchPoliciesBtn"
    description: "点击'开始检索'"
    subtitle: "多维政策检索引擎，覆盖央地各级产业政策文件\""""
    
    # Replace the old flow with the new flow
    updated_content = content.replace(old_flow, new_flow)
    
    # Write back the updated content
    with open(demo_yaml_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Successfully updated comprehensive_demo.yaml with longer waits for policy analysis!")


if __name__ == "__main__":
    improve_policy_analysis_flow()