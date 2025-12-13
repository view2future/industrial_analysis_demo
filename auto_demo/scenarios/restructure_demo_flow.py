#!/usr/bin/env python3
"""
Script to restructure the demo flow: homepage -> upload report -> generate report -> ...
"""

def restructure_demo_flow():
    """Restructure the demo flow to have upload report before generate report"""
    demo_yaml_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/scenarios/comprehensive_demo.yaml"
    
    # Read the current content
    with open(demo_yaml_path, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # Find the sections by line numbers from grep command
    # Section indices (0-based for Python):
    # 0: Homepage starts at line 16 (index 15) - stays at beginning
    # 1: Generate Report starts at line 45 (index 44) - will be moved after upload
    # 2: Task List starts at line 104 (index 103) - will be moved after generate
    # 3: Upload Report starts at line 110 (index 109) - will be moved after homepage
    # 4: Map Dashboard starts at line 158 (index 157) - will stay after task list
    # 5: Policy Analysis starts at line 215 (index 214) - will stay at end
    
    # Find section boundaries by looking for comment lines
    section_starts = []
    for i, line in enumerate(content):
        if "# 1. 首页浏览" in line:
            section_starts.append(i)
        elif "# 2. 生成报告功能" in line:
            section_starts.append(i)
        elif "# 3. 任务列表展示" in line:
            section_starts.append(i)
        elif "# 4. 上传报告功能" in line:
            section_starts.append(i)
        elif "# 5. 地图看板功能" in line:
            section_starts.append(i)
        elif "# 6. 政策解读功能" in line:
            section_starts.append(i)
    
    # If we found all sections, restructure
    if len(section_starts) == 6:
        # Sections boundaries:
        # homepage: section_starts[0] to section_starts[1]-1
        # gen_report: section_starts[1] to section_starts[2]-1  
        # task_list: section_starts[2] to section_starts[3]-1
        # upload_report: section_starts[3] to section_starts[4]-1
        # map_dashboard: section_starts[4] to section_starts[5]-1
        # policy_analysis: section_starts[5] to end
        
        homepage_start = section_starts[0]
        gen_report_start = section_starts[1]
        task_list_start = section_starts[2]
        upload_start = section_starts[3]
        map_dashboard_start = section_starts[4]
        policy_start = section_starts[5]
        
        # Find end of each section by looking for next section or end of file
        homepage_end = gen_report_start
        gen_report_end = task_list_start
        task_list_end = upload_start
        upload_end = map_dashboard_start
        map_dashboard_end = policy_start
        policy_end = len(content)
        
        # Extract sections
        homepage_section = content[homepage_start:homepage_end]
        gen_report_section = content[gen_report_start:gen_report_end]
        task_list_section = content[task_list_start:task_list_end]
        upload_section = content[upload_start:upload_end]
        map_dashboard_section = content[map_dashboard_start:map_dashboard_end]
        policy_section = content[policy_start:policy_end]
        
        # Update section numbering in comments to reflect new order
        # Upload report (originally #4) becomes #2
        renumbered_upload = []
        for line in upload_section:
            if line.strip().startswith("# 4. 上传报告功能"):
                renumbered_upload.append(line.replace("# 4. 上传报告功能", "# 2. 上传报告功能"))
            elif "模块二：" in line and "非结构化文档智能解析" in line:
                renumbered_upload.append(line.replace("模块二：", "模块一："))
            else:
                renumbered_upload.append(line)
        
        # Generate report (originally #2) becomes #3
        renumbered_gen_report = []
        for line in gen_report_section:
            if line.strip().startswith("# 2. 生成报告功能"):
                renumbered_gen_report.append(line.replace("# 2. 生成报告功能", "# 3. 生成报告功能"))
            elif "模块一：" in line and "AI智能报告生成" in line:
                renumbered_gen_report.append(line.replace("模块一：", "模块二："))
            else:
                renumbered_gen_report.append(line)
        
        # Task list (originally #3) becomes #4
        renumbered_task_list = []
        for line in task_list_section:
            if line.strip().startswith("# 3. 任务列表展示"):
                renumbered_task_list.append(line.replace("# 3. 任务列表展示", "# 4. 任务列表展示"))
            else:
                renumbered_task_list.append(line)
        
        # Map dashboard (originally #5) becomes #5 (no change)
        # Policy analysis (originally #6) becomes #6 (no change)
        
        # Reconstruct content in new order: homepage -> upload -> gen_report -> task_list -> map_dashboard -> policy
        new_content = (content[:homepage_start] +  # Before homepage (yaml header)
                      homepage_section +
                      renumbered_upload +
                      renumbered_gen_report +
                      renumbered_task_list +
                      map_dashboard_section +
                      policy_section)
        
        # Write back the updated content
        with open(demo_yaml_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        
        print("Successfully restructured the demo flow to: Homepage -> Upload Report -> Generate Report -> Task List -> Map Dashboard -> Policy Analysis")
    else:
        print(f"Expected 6 sections but found {len(section_starts)}. Not reorganizing.")


if __name__ == "__main__":
    restructure_demo_flow()