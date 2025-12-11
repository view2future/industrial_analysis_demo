#!/usr/bin/env python3
"""
Script to generate 500 random enterprise records for testing
"""

import sys
import os
sys.path.append(os.getcwd())

from app import db, app
from src.models.enterprise_models import Enterprise
from datetime import datetime, timedelta
import random
import json

def generate_test_data():
    print("Generating 500 random enterprise records...")

    # Sample data for generation
    enterprise_names = [
        "智算科技", "云创智能", "数智未来", "慧眼科技", "智能制造", "创新视界", "云知声", "慧联科技",
        "智行科技", "数通科技", "慧达科技", "云启科技", "智能物联", "慧眼识别", "智造未来",
        "数智云", "云智科技", "慧影科技", "智联科技", "数慧科技", "云慧科技", "智图科技",
        "慧算科技", "智云科技", "数影科技", "云视科技", "智控科技", "慧桥科技", "智汇科技",
        "数海科技", "云脑科技", "智感科技", "慧通科技", "智达科技", "数链科技", "云图科技",
        "智网科技", "慧芯科技", "智云物联", "数智通", "云慧视", "智算云", "慧影识别",
        "智联物联", "数慧云", "云智通", "智图慧", "慧算云", "智控通", "慧桥云", "智汇通",
        "数海云", "云脑通", "智感通", "慧通云", "智达云", "数链通", "云图通", "智网通",
        "慧芯云", "智云通", "数影通", "云视通", "智控云", "慧桥通", "智汇云", "数海通",
        "云脑云", "智感通", "慧通达", "智达通", "数链云", "云图达", "智网通", "慧芯达",
        "智云达", "数影达", "云视达", "智控达", "慧桥达", "智汇达", "数海达", "云脑达"
    ]

    ai_platforms = ["飞桨", "文心"]
    quarters = ["2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3"]
    partner_levels = ["认证级", "优选级", "无"]
    priorities = ["P0", "P1", "P2"]
    locations = [
        "北京海淀区", "上海浦东新区", "深圳南山区", "广州天河区", "杭州西湖区",
        "成都高新区", "武汉东湖高新区", "西安高新区", "南京雨花台区", "苏州工业园区",
        "重庆渝北区", "天津滨海新区", "青岛崂山区", "大连高新区", "厦门软件园",
        "长沙岳麓区", "合肥高新区", "福州软件园", "济南高新区", "沈阳浑南区"
    ]
    industries = [
        ["人工智能", "智能制造"], ["云计算", "大数据"], ["物联网", "5G"], ["人工智能", "计算机视觉"],
        ["区块链", "金融科技"], ["人工智能", "语音识别"], ["智能制造", "工业4.0"], ["人工智能", "自然语言处理"],
        ["人工智能", "医疗科技"], ["大数据", "智慧城市"], ["人工智能", "金融科技"], ["云计算", "边缘计算"],
        ["人工智能", "自动驾驶"], ["物联网", "智能硬件"], ["人工智能", "机器人"], ["大数据", "商业智能"],
        ["人工智能", "教育科技"], ["云计算", "容器技术"], ["人工智能", "安防监控"], ["大数据", "精准营销"]
    ]
    task_directions = [
        "智能问答", "OCR识别", "目标检测", "语音识别", "自然语言处理", "图像识别",
        "推荐系统", "预测分析", "智能客服", "数据挖掘", "知识图谱", "情感分析",
        "行为识别", "智能诊断", "自动化测试", "智能调度", "路径规划", "智能决策",
        "风险评估", "质量检测"
    ]
    enterprise_backgrounds = [
        "专注于人工智能技术的研发与应用，拥有丰富的行业经验",
        "领先的智能制造解决方案提供商，服务众多知名企业",
        "致力于大数据分析和处理技术的创新型企业",
        "在物联网领域拥有核心技术，产品覆盖多个行业",
        "专业的AI技术服务商，为客户提供定制化解决方案",
        "专注计算机视觉技术研发，技术水平行业领先",
        "提供完整的云计算服务，助力企业数字化转型",
        "在语音识别领域有深厚积累，技术成熟稳定",
        "专注自然语言处理技术，产品广泛应用于多个场景",
        "提供端到端的智能化解决方案，服务覆盖全产业链"
    ]
    usage_scenarios = [
        "构建智能客服系统，提升客户服务效率50%",
        "开发产品质量检测系统，降低不良品率至0.1%",
        "实现生产流程智能优化，提升生产效率25%",
        "构建智能推荐引擎，提高用户转化率30%",
        "开发数据驱动的决策系统，优化业务流程",
        "实现智能语音交互，提升用户体验满意度",
        "构建预测性维护系统，降低设备故障率40%",
        "开发图像识别系统，提升检测精度至99.5%",
        "实现智能调度系统，优化资源配置效率",
        "构建风险评估模型，提升风控准确性"
    ]
    ai_products = [
        "2024-05 智能质检系统", "2024-07 智能客服平台", "2024-09 推荐引擎",
        "2025-01 智能诊断工具", "2025-03 OCR识别SDK", "2025-05 风控模型",
        "2025-06 智能调度系统", "2025-08 预测分析平台", "2025-10 智能客服产品",
        "2025-12 智能质检系统"
    ]
    contacts = [
        "张经理（技术总监）13800138000", "李总监（产品负责人）13900139000",
        "王总（CTO）13700137000", "刘总（销售总监）13600136000",
        "陈总（CEO）13500135000", "赵总监（项目经理）13400134000",
        "孙经理（技术负责人）13300133000", "周总监（运营总监）13200132000",
        "吴经理（解决方案）13100131000", "郑总（商务总监）13000130000"
    ]

    # Clear existing enterprise data
    Enterprise.query.delete()
    db.session.commit()

    # Generate 500 enterprises ensuring unique names
    enterprises = []
    used_names = set()

    for i in range(500):
        # Generate unique enterprise name
        enterprise_name = f"{random.choice(enterprise_names)}有限公司"
        counter = 1
        original_name = enterprise_name
        while enterprise_name in used_names:
            enterprise_name = f"{original_name[:-3]}{counter}有限公司"
            counter += 1
        used_names.add(enterprise_name)

        # Generate other enterprise data
        ai_platform = random.choice(ai_platforms)
        lead_inbound_time = random.choice(quarters)
        partner_level = random.choice(partner_levels) if random.random() > 0.3 else None
        priority = random.choice(priorities)
        base_location = random.choice(locations)
        registered_capital = random.randint(100, 20000)  # In units of 10,000
        employee_count = random.randint(10, 1000)
        enterprise_background = random.choice(enterprise_backgrounds)
        industry = random.choice(industries)
        task_direction = random.choice(task_directions)
        contact_info = random.choice(contacts)
        usage_scenario = random.choice(usage_scenarios)

        # Decide if ai_products should be empty
        ai_products_val = random.choice(ai_products) if random.random() > 0.6 else ""

        # Create progress records (random number of progress updates)
        progress = []
        num_progress = random.randint(0, 8)  # 0 to 8 progress records
        for j in range(num_progress):
            # Create progress records with random dates in the past year
            days_ago = random.randint(0, 365)
            progress_time = datetime.utcnow() - timedelta(days=days_ago)  # Use the imported datetime
            progress_content = f"第{j+1}阶段进展完成，{random.choice(['技术对接', '方案评审', '合同签署', '系统部署', '需求沟通', '产品试用', '商务谈判', '高层会面'])}成功"

            progress.append({
                "content": progress_content,
                "updateTime": progress_time.isoformat()
            })

        # Sort progress by date (newest first)
        progress.sort(key=lambda x: x['updateTime'], reverse=True)

        enterprise = Enterprise(
            enterprise_name=enterprise_name,
            ai_platform=ai_platform,
            lead_inbound_time=lead_inbound_time,
            partner_level=partner_level,
            ai_products=ai_products_val,
            priority=priority,
            base_location=base_location,
            registered_capital=registered_capital,
            employee_count=employee_count,
            enterprise_background=enterprise_background,
            industry=','.join(industry),
            task_direction=task_direction,
            contact_info=contact_info,
            usage_scenario=usage_scenario,
            progress=progress
        )

        enterprises.append(enterprise)

    # Add to database
    db.session.add_all(enterprises)
    db.session.commit()
    
    print(f"Successfully generated {len(enterprises)} enterprise records!")

    # Generate random meeting data
    print("Generating random meeting records...")
    from src.models.enterprise_models import EnterpriseMeeting

    # Clear existing meeting data
    EnterpriseMeeting.query.delete()
    db.session.commit()

    meeting_types = ["外部会议", "内部会议"]
    meeting_locations = [
        "公司会议室A", "客户现场", "线上会议", "公司会议室B", "合作伙伴办公室",
        "线上会议室", "客户总部", "公司培训室", "线上视频会议", "客户研发中心"
    ]
    meeting_summaries = [
        "讨论技术方案细节，客户对我们的解决方案表示认可",
        "评审项目进展，确定下一阶段工作计划",
        "完成高层会面，确定合作意向，下一步进行技术对接",
        "产品演示成功，客户提出进一步合作需求",
        "签署合作协议，确定项目实施时间表",
        "技术对接完成，确认双方技术方案匹配",
        "商务谈判成功，确定合作模式和费用",
        "需求沟通深入，明确项目具体实施细节",
        "项目验收完成，客户满意度较高",
        "系统部署上线，进入试运行阶段"
    ]
    attendees = [
        ["张经理", "李总监", "王总"],
        ["项目经理", "技术总监", "产品经理"],
        ["商务经理", "技术专家", "销售总监"],
        ["客户方负责人", "技术负责人"],
        ["项目组全体成员"],
        ["双方高层领导"],
        ["技术团队"],
        ["商务团队", "技术团队"],
        ["客户方技术团队"],
        ["双方项目负责人"]
    ]

    meetings = []
    for i in range(200):  # Generate 200 random meetings
        meeting_type = random.choice(meeting_types)

        # For external meetings, link to an existing enterprise
        enterprise = None
        enterprise_name = ""
        if meeting_type == "外部会议":
            # Randomly select an enterprise for external meetings
            enterprise = random.choice(enterprises)
            enterprise_name = enterprise.enterprise_name
        else:
            enterprise_name = "内部会议"

        # Generate meeting data
        meeting_time = datetime.utcnow() - timedelta(days=random.randint(0, 180))  # Within last 6 months
        meeting_location = random.choice(meeting_locations)
        meeting_summary = random.choice(meeting_summaries)
        attendees_list = ", ".join(random.choice(attendees))

        meeting = EnterpriseMeeting(
            meeting_type=meeting_type,
            enterprise_id=enterprise.id if enterprise else None,
            enterprise_name=enterprise_name,
            attendees=attendees_list,
            meeting_time=meeting_time,
            meeting_location=meeting_location,
            meeting_summary=meeting_summary
        )

        meetings.append(meeting)

    # Add meetings to database
    db.session.add_all(meetings)
    db.session.commit()

    print(f"Successfully generated {len(meetings)} meeting records!")

if __name__ == "__main__":
    with app.app_context():
        generate_test_data()