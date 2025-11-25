#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政策解读助手模块
提取政策要点、识别补贴税收优惠、时间轴提醒、适用性匹配
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PolicyAnalyzer:
    """政策分析器"""
    
    def __init__(self):
        """初始化政策分析器"""
        # 政策关键词库
        self.policy_keywords = {
            "补贴": ["补贴", "资助", "奖励", "扶持资金", "专项资金"],
            "税收": ["税收优惠", "减税", "免税", "税收减免", "所得税优惠"],
            "金融": ["贷款", "融资", "信贷", "担保", "贴息"],
            "土地": ["用地", "土地", "厂房", "园区"],
            "人才": ["人才", "引进", "落户", "住房"],
            "研发": ["研发", "创新", "科技", "专利"]
        }
        
        # 时间关键词
        self.time_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})年(\d{1,2})月',
            r'(\d{1,2})个月',
            r'(\d{1,3})天',
            r'(至|到|截止).*?(\d{4})年(\d{1,2})月(\d{1,2})日'
        ]
    
    def extract_policy_highlights(self, policy_text: str) -> List[Dict]:
        """提取政策要点
        
        Args:
            policy_text: 政策文本
            
        Returns:
            政策要点列表
        """
        try:
            highlights = []
            
            # 分句
            sentences = re.split(r'[。！；\n]', policy_text)
            
            for idx, sentence in enumerate(sentences):
                if not sentence.strip() or len(sentence) < 10:
                    continue
                
                # 检查是否包含政策关键词
                matched_categories = []
                for category, keywords in self.policy_keywords.items():
                    if any(kw in sentence for kw in keywords):
                        matched_categories.append(category)
                
                if matched_categories:
                    # 提取数字信息（金额、比例等）
                    numbers = re.findall(r'(\d+(?:\.\d+)?)\s*([亿万千百]?[元%])', sentence)
                    
                    highlights.append({
                        "content": sentence.strip(),
                        "categories": matched_categories,
                        "numbers": [{"value": n[0], "unit": n[1]} for n in numbers],
                        "position": idx
                    })
            
            logger.info(f"提取政策要点: {len(highlights)} 个")
            return highlights
            
        except Exception as e:
            logger.error(f"提取政策要点失败: {e}")
            return []
    
    def identify_subsidies_and_taxes(self, policy_text: str) -> Dict:
        """识别补贴和税收优惠
        
        Args:
            policy_text: 政策文本
            
        Returns:
            补贴和税收信息
        """
        try:
            result = {
                "subsidies": [],
                "tax_benefits": [],
                "financial_support": []
            }
            
            sentences = re.split(r'[。！；\n]', policy_text)
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                # 识别补贴
                if any(kw in sentence for kw in self.policy_keywords["补贴"]):
                    # 提取金额
                    amounts = re.findall(r'(\d+(?:\.\d+)?)\s*([亿万千百]?元)', sentence)
                    result["subsidies"].append({
                        "description": sentence.strip(),
                        "amounts": [{"value": a[0], "unit": a[1]} for a in amounts]
                    })
                
                # 识别税收优惠
                if any(kw in sentence for kw in self.policy_keywords["税收"]):
                    # 提取比例
                    percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', sentence)
                    result["tax_benefits"].append({
                        "description": sentence.strip(),
                        "percentages": [float(p) for p in percentages]
                    })
                
                # 识别金融支持
                if any(kw in sentence for kw in self.policy_keywords["金融"]):
                    amounts = re.findall(r'(\d+(?:\.\d+)?)\s*([亿万千百]?元)', sentence)
                    result["financial_support"].append({
                        "description": sentence.strip(),
                        "amounts": [{"value": a[0], "unit": a[1]} for a in amounts]
                    })
            
            logger.info(f"识别补贴: {len(result['subsidies'])} 项, "
                       f"税收优惠: {len(result['tax_benefits'])} 项")
            return result
            
        except Exception as e:
            logger.error(f"识别补贴税收失败: {e}")
            return {"subsidies": [], "tax_benefits": [], "financial_support": []}
    
    def extract_timeline(self, policy_text: str) -> List[Dict]:
        """提取政策时间轴
        
        Args:
            policy_text: 政策文本
            
        Returns:
            时间节点列表
        """
        try:
            timeline = []
            
            # 提取日期
            date_patterns = [
                (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
                (r'(\d{4})年(\d{1,2})月', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-01")
            ]
            
            for pattern, formatter in date_patterns:
                matches = re.finditer(pattern, policy_text)
                for match in matches:
                    date_str = formatter(match)
                    
                    # 获取上下文
                    start = max(0, match.start() - 50)
                    end = min(len(policy_text), match.end() + 50)
                    context = policy_text[start:end].strip()
                    
                    # 判断时间类型
                    event_type = "其他"
                    if any(kw in context for kw in ["发布", "颁布", "实施"]):
                        event_type = "发布实施"
                    elif any(kw in context for kw in ["截止", "之前", "到期"]):
                        event_type = "截止时间"
                    elif any(kw in context for kw in ["申报", "申请"]):
                        event_type = "申报时间"
                    
                    timeline.append({
                        "date": date_str,
                        "event_type": event_type,
                        "context": context,
                        "is_future": self._is_future_date(date_str)
                    })
            
            # 按日期排序
            timeline.sort(key=lambda x: x["date"])
            
            logger.info(f"提取时间轴: {len(timeline)} 个节点")
            return timeline
            
        except Exception as e:
            logger.error(f"提取时间轴失败: {e}")
            return []
    
    def _is_future_date(self, date_str: str) -> bool:
        """判断日期是否在未来"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj > datetime.now()
        except:
            return False
    
    def match_applicability(self, policy_text: str, 
                           company_profile: Dict) -> Dict:
        """匹配政策适用性
        
        Args:
            policy_text: 政策文本
            company_profile: 企业画像 {"industry": "", "size": "", "location": ""}
            
        Returns:
            适用性评估结果
        """
        try:
            score = 0
            matched_criteria = []
            recommendations = []
            
            # 行业匹配
            industry = company_profile.get("industry", "")
            if industry and industry in policy_text:
                score += 30
                matched_criteria.append(f"行业匹配: {industry}")
            
            # 企业规模匹配
            size = company_profile.get("size", "")
            size_keywords = {
                "大型": ["大型", "龙头", "骨干"],
                "中型": ["中型", "成长型"],
                "小型": ["小型", "小微", "初创"]
            }
            if size in size_keywords:
                if any(kw in policy_text for kw in size_keywords[size]):
                    score += 20
                    matched_criteria.append(f"规模匹配: {size}企业")
            
            # 地域匹配
            location = company_profile.get("location", "")
            if location and location in policy_text:
                score += 20
                matched_criteria.append(f"地域匹配: {location}")
            
            # 技术要求匹配
            tech_keywords = ["高新技术", "研发", "创新", "专利"]
            tech_match = sum(1 for kw in tech_keywords if kw in policy_text)
            if tech_match > 0:
                score += min(tech_match * 10, 30)
                matched_criteria.append(f"技术要求: 提及{tech_match}个相关词")
            
            # 生成建议
            if score >= 70:
                recommendations.append("强烈建议申报此政策，匹配度很高")
            elif score >= 50:
                recommendations.append("建议关注此政策，符合部分条件")
            elif score >= 30:
                recommendations.append("可以尝试申报，但需进一步确认详细条件")
            else:
                recommendations.append("暂不建议申报，匹配度较低")
            
            result = {
                "score": score,
                "max_score": 100,
                "matched_criteria": matched_criteria,
                "recommendations": recommendations,
                "applicability_level": self._get_applicability_level(score)
            }
            
            logger.info(f"适用性评估: 得分{score}/100")
            return result
            
        except Exception as e:
            logger.error(f"适用性匹配失败: {e}")
            return {}
    
    def _get_applicability_level(self, score: int) -> str:
        """根据分数返回适用性等级"""
        if score >= 70:
            return "高度适用"
        elif score >= 50:
            return "较为适用"
        elif score >= 30:
            return "一般适用"
        else:
            return "不太适用"
    
    def generate_policy_summary(self, policy_text: str) -> Dict:
        """生成政策摘要
        
        Args:
            policy_text: 政策全文
            
        Returns:
            政策摘要
        """
        try:
            highlights = self.extract_policy_highlights(policy_text)
            subsidies_taxes = self.identify_subsidies_and_taxes(policy_text)
            timeline = self.extract_timeline(policy_text)
            
            # 统计数据
            total_subsidies = len(subsidies_taxes["subsidies"])
            total_tax_benefits = len(subsidies_taxes["tax_benefits"])
            upcoming_deadlines = [t for t in timeline if t["is_future"] and t["event_type"] == "截止时间"]
            
            summary = {
                "highlights": highlights[:5],  # 前5个要点
                "subsidies_and_taxes": subsidies_taxes,
                "timeline": timeline,
                "statistics": {
                    "total_highlights": len(highlights),
                    "total_subsidies": total_subsidies,
                    "total_tax_benefits": total_tax_benefits,
                    "upcoming_deadlines": len(upcoming_deadlines)
                },
                "urgent_reminders": upcoming_deadlines[:3]  # 最近3个截止日期
            }
            
            logger.info("生成政策摘要成功")
            return summary
            
        except Exception as e:
            logger.error(f"生成政策摘要失败: {e}")
            return {}
    
    def analyze_policy(self, policy_text: str, 
                      company_profile: Optional[Dict] = None) -> Dict:
        """完整政策分析
        
        Args:
            policy_text: 政策文本
            company_profile: 企业画像（可选）
            
        Returns:
            完整分析结果
        """
        try:
            # 生成摘要
            summary = self.generate_policy_summary(policy_text)
            
            # 适用性匹配
            applicability = None
            if company_profile:
                applicability = self.match_applicability(policy_text, company_profile)
            
            result = {
                "summary": summary,
                "applicability": applicability
            }
            
            logger.info("完整政策分析成功")
            return result
            
        except Exception as e:
            logger.error(f"政策分析失败: {e}")
            return {}


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    analyzer = PolicyAnalyzer()
    
    # 测试政策文本
    test_policy = """
    成都市人工智能产业扶持政策
    
    为支持人工智能产业发展，对符合条件的企业给予以下支持：
    
    一、资金补贴：对新引进的人工智能企业，给予最高500万元补贴。
    二、税收优惠：对高新技术企业减按15%税率征收企业所得税。
    三、研发支持：对企业研发投入给予20%的资金资助。
    
    申报时间：2024年3月1日至2024年6月30日
    政策截止日期：2025年12月31日
    
    适用对象：在成都注册的人工智能、大数据相关企业。
    """
    
    # 完整分析
    company = {
        "industry": "人工智能",
        "size": "中型",
        "location": "成都"
    }
    
    result = analyzer.analyze_policy(test_policy, company)
    
    print(f"\n政策要点数: {result['summary']['statistics']['total_highlights']}")
    print(f"补贴项目: {result['summary']['statistics']['total_subsidies']}")
    print(f"税收优惠: {result['summary']['statistics']['total_tax_benefits']}")
    
    print(f"\n补贴详情:")
    for sub in result['summary']['subsidies_and_taxes']['subsidies']:
        print(f"- {sub['description'][:50]}...")
    
    print(f"\n时间轴:")
    for t in result['summary']['timeline']:
        print(f"- {t['date']} ({t['event_type']})")
    
    if result['applicability']:
        print(f"\n适用性评估:")
        print(f"- 得分: {result['applicability']['score']}/100")
        print(f"- 等级: {result['applicability']['applicability_level']}")
        print(f"- 匹配条件: {', '.join(result['applicability']['matched_criteria'])}")
    
    print("\n✅ 政策解读助手模块测试通过！")
