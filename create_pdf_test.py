#!/usr/bin/env python3
"""
Create a sample PDF file with POI data for testing
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import random

# List of sample companies, universities, and research institutes
companies = [
    "华为技术有限公司", "阿里巴巴集团", "腾讯科技有限公司", "百度公司", "京东集团", 
    "美团点评", "字节跳动", "滴滴出行", "小米科技", "联想集团", "海尔集团", "格力电器",
    "美的集团", "比亚迪", "宁德时代", "隆基绿能", "阳光电源", "汇川技术", "恒瑞医药"
]

universities = [
    "北京大学", "清华大学", "复旦大学", "上海交通大学", "浙江大学", "中国科学技术大学",
    "南京大学", "华中科技大学", "中山大学", "西安交通大学", "北京航空航天大学", 
    "北京理工大学", "哈尔滨工业大学", "西北工业大学", "电子科技大学", "北京邮电大学",
    "大连理工大学", "东南大学", "天津大学", "南开大学"
]

research_institutes = [
    "中国科学院", "中国社会科学院", "中国工程院", "中科院计算技术研究所", "中科院自动化研究所",
    "中科院半导体研究所", "中科院物理研究所", "中科院化学研究所", "中科院生物物理研究所", 
    "中科院上海光机所", "中科院光电技术研究所", "中国医学科学院", "中国农业科学院",
    "中国林业科学研究院", "中国水产科学研究院", "中国热带农业科学院", "中国建筑材料科学研究总院",
    "中国钢研科技集团", "中国有研科技集团", "中国航天科技集团"
]

# Chinese provinces and cities
regions = [
    "北京市", "上海市", "天津市", "重庆市", "河北省", "山西省", "辽宁省", "吉林省", 
    "黑龙江省", "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省", "河南省", 
    "湖北省", "湖南省", "广东省", "海南省", "四川省", "贵州省", "云南省", "陕西省", 
    "甘肃省", "青海省", "台湾省", "内蒙古自治区", "广西壮族自治区", "西藏自治区", 
    "宁夏回族自治区", "新疆维吾尔自治区", "香港特别行政区", "澳门特别行政区"
]

def create_pdf_poi_list(filename, count=1000):
    """Create a PDF file with POI data."""
    # Create the PDF
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Add title
    title = Paragraph("企业、高校、科研院所清单", styles['Title'])
    elements.append(title)
    elements.append(Paragraph(" ", styleN))  # Spacer
    
    # Create data for table
    data = [
        ['序号', '名称', '类型', '地址', '行政区域']
    ]
    
    for i in range(min(count, 1000)):  # Limit to 1000 to keep PDF manageable
        entity_type = random.choice(['企业', '高校', '科研院所'])
        
        if entity_type == '企业':
            name = random.choice(companies) + f"有限公司{i+1:04d}"
        elif entity_type == '高校':
            name = f"{random.choice(universities)}第{i+1:04d}分校"
        else:  # 研究院所
            name = f"{random.choice(research_institutes)}第{i+1:04d}分院"
        
        region = random.choice(regions)
        street_num = random.randint(1, 999)
        address = f"{region}某区某街道{street_num}号"
        
        data.append([
            str(i+1),
            name,
            entity_type,
            address,
            region
        ])
    
    # Create table
    table = Table(data)
    
    # Add style to table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Build the PDF
    doc.build(elements)

if __name__ == "__main__":
    # Create a sample PDF with 1000 POIs
    create_pdf_poi_list('test_data/test_data_large.pdf')
    print("PDF file created: test_data/test_data_large.pdf")