#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content-Driven Visualization Engine
Analyzes policy content and generates appropriate visualizations based on detected content patterns
"""

import re
import json
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentDrivenVisualizationEngine:
    """
    Analyzes policy content and generates content-appropriate visualizations
    """
    
    def __init__(self):
        # Define pattern categories for different types of policy content
        self.patterns = {
            'amounts': [
                r'(\d+(?:\.\d+)?)\s*([万亿千百万亿]?元)',
                r'(\d+(?:\.\d+)?)\s*[万亿千百万亿]?(?:投资|资助|补贴|奖励)',
                r'(\d+(?:\.\d+)?)\s*%.*?优惠',
            ],
            'numbers': [
                r'(\d+(?:\.\d+)?)\s*(?:家|个|项|名|台|套|部)',
                r'([一二三四五六七八九十百千万亿]+)',
            ],
            'dates': [
                r'(\d{4})年(\d{1,2})月(\d{1,2})日',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'(\d{4})年(\d{1,2})月',
            ],
            'organizations': [
                r'(?:[省市县区乡镇]+(?:政府|局|委|办|厅|部))',
                r'(?:\w+?公司|\w+?集团)',
            ],
            'industries': [
                r'(?:人工智能|大数据|云计算|物联网|5G|区块链|新能源|生物医药|新材料|高端制造|数字经济)',
            ],
            'requirements': [
                r'(?:要求|条件|标准|门槛|资格|资质).*?[是为：]\s*([^，。；\n]+)',
                r'(?:必须|需要|应当|应具备)\s*([^，。；\n]+)',
            ]
        }
    
    def analyze_policy_content(self, content: str) -> Dict:
        """
        Analyze policy content and extract structured information
        """
        analysis = {
            'amounts': self._extract_amounts(content),
            'numbers': self._extract_numbers(content),
            'dates': self._extract_dates(content),
            'organizations': self._extract_organizations(content),
            'industries': self._extract_industries(content),
            'requirements': self._extract_requirements(content),
            'content_type': self._classify_content_type(content),
            'key_themes': self._extract_key_themes(content),
            'action_items': self._extract_action_items(content)
        }
        
        return analysis
    
    def _extract_amounts(self, content: str) -> List[Dict]:
        """Extract financial amounts from content"""
        amounts = []
        for pattern in self.patterns['amounts']:
            matches = re.finditer(pattern, content)
            for match in matches:
                value = match.group(1)
                unit = match.group(2) if len(match.groups()) > 1 else '元'
                context = self._get_context(content, match.start(), 50)
                
                amounts.append({
                    'value': float(value) if self._is_numeric(value) else value,
                    'unit': unit,
                    'context': context,
                    'position': match.start()
                })
        
        return amounts
    
    def _extract_numbers(self, content: str) -> List[Dict]:
        """Extract general numbers from content"""
        numbers = []
        for pattern in self.patterns['numbers']:
            matches = re.finditer(pattern, content)
            for match in matches:
                value = match.group(1)
                context = self._get_context(content, match.start(), 50)
                
                numbers.append({
                    'value': value,
                    'context': context,
                    'position': match.start()
                })
        
        return numbers
    
    def _extract_dates(self, content: str) -> List[Dict]:
        """Extract dates from content"""
        dates = []
        for pattern in self.patterns['dates']:
            matches = re.finditer(pattern, content)
            for match in matches:
                if len(match.groups()) >= 2:
                    if len(match.groups()) == 3:  # YYYY-MM-DD or YYYY年MM月DD日
                        date_str = f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
                    elif len(match.groups()) == 2:  # YYYY年MM月
                        date_str = f"{match.group(1)}-{match.group(2).zfill(2)}-01"
                    else:
                        date_str = match.group(0)
                
                    context = self._get_context(content, match.start(), 50)
                    
                    dates.append({
                        'date': date_str,
                        'context': context,
                        'position': match.start()
                    })
        
        return dates
    
    def _extract_organizations(self, content: str) -> List[str]:
        """Extract organizations from content"""
        organizations = []
        for pattern in self.patterns['organizations']:
            matches = re.finditer(pattern, content)
            for match in matches:
                org = match.group(0)
                if org not in organizations:
                    organizations.append(org)
        
        return organizations
    
    def _extract_industries(self, content: str) -> List[str]:
        """Extract industries from content"""
        industries = []
        for pattern in self.patterns['industries']:
            matches = re.finditer(pattern, content)
            for match in matches:
                industry = match.group(0)
                if industry not in industries:
                    industries.append(industry)
        
        return industries
    
    def _extract_requirements(self, content: str) -> List[str]:
        """Extract requirements from content"""
        requirements = []
        for pattern in self.patterns['requirements']:
            matches = re.finditer(pattern, content)
            for match in matches:
                req = match.group(1).strip() if len(match.groups()) > 0 else match.group(0)
                if req and req not in requirements:
                    requirements.append(req)
        
        return requirements
    
    def _classify_content_type(self, content: str) -> str:
        """Classify the policy content type"""
        content_lower = content.lower()
        
        # Define content type indicators
        type_indicators = {
            'funding': ['资金', '补贴', '资助', '奖励', '投入', '投资', '拨款', '资助金'],
            'regulation': ['规定', '办法', '规范', '标准', '制度', '条例', '要求', '禁止'],
            'tax': ['税收', '减免', '优惠', '税率', '税额', '退税', '免税'],
            'talent': ['人才', '引进', '培养', '激励', '待遇', '落户', '住房'],
            'innovation': ['创新', '研发', '科技', '技术', '专利', '成果转化'],
            'industry': ['产业', '发展', '规划', '布局', '升级', '转型']
        }
        
        # Score each type
        type_scores = {}
        for policy_type, keywords in type_indicators.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            type_scores[policy_type] = score
        
        # Return the type with highest score
        if type_scores:
            return max(type_scores, key=type_scores.get)
        else:
            return 'general'
    
    def _extract_key_themes(self, content: str) -> List[str]:
        """Extract key themes from content"""
        # Simple keyword-based theme extraction
        theme_keywords = [
            '支持', '促进', '发展', '建设', '加强', '完善', '优化', '提升',
            '推进', '实施', '落实', '保障', '鼓励', '扶持', '引导'
        ]
        
        themes = []
        sentences = re.split(r'[。！；\n]', content)
        for sentence in sentences:
            if any(keyword in sentence for keyword in theme_keywords):
                if len(sentence.strip()) > 10:  # Only add substantial sentences
                    themes.append(sentence.strip())
                    if len(themes) >= 5:  # Limit to top 5 themes
                        break
        
        return themes
    
    def _extract_action_items(self, content: str) -> List[str]:
        """Extract action items from content"""
        action_indicators = [
            r'(?:要|需要|应当|应该|必须|务必).*?(?:加强|推进|实施|开展|建立|完善)',
            r'(?:推进|落实|实施|开展|建立|完善|加强|提升).*?(?:工作|计划|措施|方案)',
        ]
        
        actions = []
        for pattern in action_indicators:
            matches = re.finditer(pattern, content)
            for match in matches:
                action = match.group(0)
                if action not in actions and len(action) > 10:
                    actions.append(action)
        
        return actions
    
    def generate_visualization_data(self, analysis: Dict) -> Dict:
        """
        Generate visualization data based on content analysis
        """
        visualization_data = {
            'charts': {},
            'recommendations': []
        }
        
        # Generate different chart types based on content type
        content_type = analysis.get('content_type', 'general')
        
        if content_type in ['funding', 'tax', 'general']:
            # Generate financial charts if amounts are available
            if analysis['amounts']:
                visualization_data['charts']['amounts_pie'] = self._create_amounts_pie_chart(analysis['amounts'])
                visualization_data['charts']['amounts_bar'] = self._create_amounts_bar_chart(analysis['amounts'])
        
        # Generate timeline chart if dates are available
        if analysis['dates']:
            visualization_data['charts']['timeline'] = self._create_timeline_chart(analysis['dates'])
        
        # Generate industry focus chart if industries are identified
        if analysis['industries']:
            visualization_data['charts']['industries'] = self._create_industry_chart(analysis['industries'])
        
        # Generate organization chart if organizations are identified
        if analysis['organizations']:
            visualization_data['charts']['organizations'] = self._create_organization_chart(analysis['organizations'])
        
        # Generate recommendations based on content type
        visualization_data['recommendations'] = self._generate_recommendations(content_type, analysis)
        
        return visualization_data
    
    def _create_amounts_pie_chart(self, amounts: List[Dict]) -> Dict:
        """Create pie chart data for amounts"""
        # Group amounts by unit
        amount_groups = {}
        for amt in amounts:
            unit = amt.get('unit', '元')
            if unit not in amount_groups:
                amount_groups[unit] = 0
            amount_groups[unit] += amt.get('value', 0) if isinstance(amt.get('value'), (int, float)) else 0
        
        # Create pie chart data
        pie_data = []
        for unit, total in amount_groups.items():
            pie_data.append({
                'name': unit,
                'value': total
            })
        
        return {
            'type': 'pie',
            'title': '资金支持分布',
            'data': pie_data
        }
    
    def _create_amounts_bar_chart(self, amounts: List[Dict]) -> Dict:
        """Create bar chart data for amounts"""
        # Use context as x-axis for top amounts
        top_amounts = sorted(amounts, key=lambda x: x.get('value', 0) if isinstance(x.get('value'), (int, float)) else 0, reverse=True)[:5]
        
        bar_data = {
            'xAxis': [amt.get('context', '')[:20] + '...' for amt in top_amounts],
            'yAxis': [amt.get('value', 0) for amt in top_amounts]
        }
        
        return {
            'type': 'bar',
            'title': '主要资金支持项目',
            'data': bar_data
        }
    
    def _create_timeline_chart(self, dates: List[Dict]) -> Dict:
        """Create timeline chart data"""
        timeline_data = []
        for date_info in dates:
            timeline_data.append({
                'date': date_info.get('date', ''),
                'event': date_info.get('context', '')[:30] + '...'
            })
        
        return {
            'type': 'timeline',
            'title': '政策时间轴',
            'data': timeline_data
        }
    
    def _create_industry_chart(self, industries: List[str]) -> Dict:
        """Create industry focus chart"""
        industry_counts = {}
        for industry in industries:
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        industry_data = []
        for industry, count in industry_counts.items():
            industry_data.append({
                'name': industry,
                'value': count
            })
        
        return {
            'type': 'bar',
            'title': '重点关注行业',
            'data': industry_data
        }
    
    def _create_organization_chart(self, organizations: List[str]) -> Dict:
        """Create organization chart"""
        org_data = []
        for org in organizations[:10]:  # Limit to top 10
            org_data.append({
                'name': org,
                'value': 1  # Simple count
            })
        
        return {
            'type': 'list',
            'title': '相关组织机构',
            'data': org_data
        }
    
    def _generate_recommendations(self, content_type: str, analysis: Dict) -> List[str]:
        """Generate visualization recommendations based on content type"""
        recommendations = []
        
        # General recommendations based on content type
        if content_type == 'funding':
            recommendations.append("资金流向桑基图 - 展示资金从来源到用途的流向")
            recommendations.append("支持措施对比柱状图 - 比较不同支持措施的金额")
        elif content_type == 'regulation':
            recommendations.append("合规要求流程图 - 展示遵守政策的步骤")
            recommendations.append("关键条款词云图 - 突出重要法规条款")
        elif content_type == 'tax':
            recommendations.append("税率比较图表 - 对比不同税率优惠")
            recommendations.append("减税效果预测图 - 展示减税带来的影响")
        elif content_type == 'talent':
            recommendations.append("人才引进网络图 - 展示人才与政策的关系")
            recommendations.append("待遇对比表格 - 比较不同人才的待遇")
        
        # Add recommendations based on available data
        if analysis.get('amounts'):
            recommendations.append("财务支持可视化 - 基于提取的金额数据")
        if analysis.get('dates'):
            recommendations.append("政策时间轴 - 基于提取的时间节点")
        if analysis.get('industries'):
            recommendations.append("行业关注度图 - 基于提及的行业")
        if analysis.get('requirements'):
            recommendations.append("申请条件关系图 - 基于申请条件")
        
        return recommendations
    
    def _get_context(self, content: str, position: int, length: int = 50) -> str:
        """Get context text around a specific position"""
        start = max(0, position - length // 2)
        end = min(len(content), position + length // 2)
        return content[start:end].strip()
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a value is numeric"""
        try:
            float(value)
            return True
        except ValueError:
            return False


# Test function
def test_visualization_engine():
    """Test the visualization engine"""
    engine = ContentDrivenVisualizationEngine()
    
    test_content = """
    为支持人工智能产业发展，成都市政府发布专项政策，主要包括：
    1. 对新引进的人工智能龙头企业给予最高5000万元一次性奖励
    2. 对高新技术企业减按15%税率征收企业所得税
    3. 对企业研发投入给予30%的资金资助
    4. 实施时间：2024年1月1日起
    5. 申报截止：2024年12月31日
    政策适用于注册在成都市的各类人工智能企业
    """
    
    print("Testing Content-Driven Visualization Engine...")
    analysis = engine.analyze_policy_content(test_content)
    print(f"Content type: {analysis['content_type']}")
    print(f"Amounts found: {len(analysis['amounts'])}")
    print(f"Dates found: {len(analysis['dates'])}")
    print(f"Industries found: {analysis['industries']}")
    
    viz_data = engine.generate_visualization_data(analysis)
    print(f"Charts generated: {list(viz_data['charts'].keys())}")
    print(f"Recommendations: {len(viz_data['recommendations'])}")
    
    return analysis, viz_data


if __name__ == "__main__":
    test_visualization_engine()
    print("\n✅ Content-Driven Visualization Engine ready!")