#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Policy Analysis Integration Module
Integrate web scraping with policy analysis and LLM interpretation
"""

import logging
from typing import Dict, List, Optional
from dataclasses import asdict
import json

# Import existing policy analysis functionality
from src.analysis.policy_analyzer import PolicyAnalyzer
from src.data.policy_web_scraper import PolicyWebScraper
from src.ai.llm_generator import LLMReportGenerator
from src.analysis.entity_extractor import EntityExtractor
from src.visualization.knowledge_graph_visualizer import KnowledgeGraphVisualizer


logger = logging.getLogger(__name__)


class PolicyAnalysisIntegrator:
    """
    Integrates web scraping, policy analysis, and LLM interpretation
    """

    def __init__(self, llm_service: str = 'kimi'):
        """Initialize the policy analysis integrator"""
        self.policy_analyzer = PolicyAnalyzer()
        self.scraper = PolicyWebScraper()

        # Initialize LLM generator with error handling
        try:
            self.llm_generator = LLMReportGenerator(llm_service=llm_service, config_path='config.json')
        except ValueError as e:
            if "API key not found" in str(e):
                logger.warning(f"LLM API key not configured: {e}")
                self.llm_generator = None
            else:
                raise e

        self.entity_extractor = EntityExtractor()
        self.graph_visualizer = KnowledgeGraphVisualizer()

    def analyze_policy_from_url(self, url: str, company_profile: Optional[Dict] = None) -> Dict:
        """
        Analyze policy from URL by scraping content and running analysis
        
        Args:
            url: URL to analyze
            company_profile: Optional company profile for applicability assessment
            
        Returns:
            Complete analysis result
        """
        try:
            logger.info(f"🔍 Analyzing policy from URL: {url}")
            
            # Step 1: Scrape the policy content
            scraped_result = self.scraper.scrape_policy_content(url)
            if not scraped_result or scraped_result.get('status') != 'success':
                error_msg = scraped_result.get('error', 'Unknown error') if scraped_result else 'Scraping failed'
                logger.error(f"❌ Failed to scrape content from {url}: {error_msg}")
                return {
                    'success': False,
                    'error': f'Scraping failed: {error_msg}',
                    'url': url
                }
            
            content = scraped_result['content']
            title = scraped_result['title']
            
            if not content.strip():
                logger.error(f"❌ No content found at {url}")
                return {
                    'success': False,
                    'error': 'No content found on the page',
                    'url': url
                }
            
            # Step 2: Extract entities
            logger.info("📊 Extracting entities...")
            entities = self.entity_extractor.extract_entities(content)
            
            # Step 3: Analyze policy content
            logger.info("📋 Analyzing policy content...")
            policy_analysis = self.policy_analyzer.analyze_policy(content, company_profile)
            
            # Step 4: Generate knowledge graph
            logger.info("🌐 Generating knowledge graph...")
            graph_data = self.graph_visualizer.transform_entities_to_graph(entities)
            echarts_config = self.graph_visualizer.generate_echarts_config(
                graph_data, f"{title} - 实体关系图"
            )
            
            # Step 5: Generate LLM interpretation
            logger.info("🤖 Generating LLM interpretation...")
            llm_interpretation = self._generate_llm_interpretation(content, title)

            # Step 5.5: Enhance policy analysis if LLM interpretation is available
            if llm_interpretation and 'error' not in llm_interpretation:
                # Update the policy analysis with LLM insights
                if 'summary' in llm_interpretation and llm_interpretation['summary']:
                    if 'summary' not in policy_analysis or not policy_analysis['summary']:
                        policy_analysis['summary'] = {'highlights': [], 'subsidies_and_taxes': {}, 'timeline': [], 'statistics': {}}
                    # Add LLM summary to policy analysis
                    policy_analysis['summary']['llm_summary'] = llm_interpretation['summary']
            
            # Step 6: Extract classification info
            logger.info("🏷️  Extracting classification info...")
            classification_info = self._extract_classification_info(content, title)
            
            # Step 7: Compile complete result
            result = {
                'success': True,
                'url': url,
                'title': title,
                'content': content,
                'scraped_metadata': scraped_result.get('metadata', {}),
                'policy_analysis': policy_analysis,
                'entities': entities,
                'knowledge_graph': {
                    'data': graph_data,
                    'echarts_config': echarts_config
                },
                'llm_interpretation': llm_interpretation,
                'classification': classification_info,
                'analyzed_at': scraped_result.get('scraped_at')
            }
            
            logger.info(f"✅ Successfully analyzed policy: {title[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing policy from {url}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}',
                'url': url
            }

    def _generate_llm_interpretation(self, content: str, title: str) -> Dict:
        """Generate LLM-based interpretation of the policy"""
        try:
            from src.ai.llm_generator import LLMReportGenerator

            # Load config directly to check for API keys without initializing the full generator
            import json
            import os
            from pathlib import Path

            # Try to load config directly
            config_path = Path('config.json')
            if not config_path.exists():
                logger.error("Config file not found at config.json")
                return {
                    'summary': '配置文件未找到',
                    'key_points': ['配置问题：config.json文件不存在'],
                    'support_measures': [],
                    'application_conditions': [],
                    'timeline': [],
                    'industry_impact': [],
                    'recommendations': []
                }

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            api_keys = config.get('api_keys', {})

            # Check if Kimi API key is available
            kimi_key = (
                api_keys.get('kimi')
                or api_keys.get('kimi_api_key')
                or os.environ.get('KIMI_API_KEY')
                or os.environ.get('MOONSHOT_API_KEY')
            )

            if not kimi_key:
                logger.warning("Kimi API key not found in config, skipping LLM analysis")
                return {
                    'summary': 'LLM解读服务未配置',
                    'key_points': ['要点分析待配置LLM服务后可用'],
                    'support_measures': ['支持措施分析待配置LLM服务后可用'],
                    'application_conditions': ['申请条件分析待配置LLM服务后可用'],
                    'timeline': ['时间信息分析待配置LLM服务后可用'],
                    'industry_impact': ['产业影响分析待配置LLM服务后可用'],
                    'recommendations': ['申报建议分析待配置LLM服务后可用']
                }

            # Now initialize the LLM generator knowing that the key exists
            llm_gen = LLMReportGenerator(llm_service='kimi', config_path='config.json')

            # Prepare context for LLM
            context = f"""
            请对以下政策文件进行深度解读和分析：

            政策标题：{title}

            政策内容：
            {content[:4000]}  # Limit content to avoid token issues

            请提供详细的分析报告，包括：

            1. 政策要点总结 (Executive Summary)
            - 核心目标
            - 主要支持方向
            - 重要数据指标

            2. 关键支持措施 (Support Measures)
            - 资金支持：具体金额、比例
            - 税收优惠：具体税率、减免幅度
            - 其他支持：如土地、人才、技术等

            3. 适用条件 (Application Conditions)
            - 企业资质要求
            - 行业领域限制
            - 地域要求
            - 其他条件

            4. 重要时间节点 (Timeline)
            - 政策生效时间
            - 申报截止时间
            - 预期完成时间

            5. 影响分析 (Impact Analysis)
            - 对相关产业的影响
            - 对企业的影响
            - 预期效果

            6. 申报建议 (Application Recommendations)
            - 适合的企业类型
            - 关键申报要点
            - 注意事项

            请以结构化JSON格式返回分析结果。
            """

            # Use the LLM to generate interpretation
            result = llm_gen.generate_report(
                city="政策分析",
                industry="政策解读",
                additional_context=context
            )

            if result.get('success'):
                report_content = result.get('full_content', '')
                # Extract the key information from LLM response
                interpretation = self._parse_llm_response(report_content)
                return interpretation
            else:
                logger.error(f"LLM generation failed: {result.get('error')}")
                # Return basic interpretation if LLM fails
                return {
                    'summary': 'LLM解读生成失败，使用基础分析',
                    'key_points': ['要点1', '要点2', '要点3'],
                    'support_measures': ['支持措施1', '支持措施2'],
                    'application_conditions': ['申请条件1', '申请条件2'],
                    'timeline': ['时间节点1', '时间节点2'],
                    'industry_impact': ['影响1', '影响2'],
                    'recommendations': ['建议1', '建议2']
                }

        except Exception as e:
            logger.error(f"❌ Error generating LLM interpretation: {e}")
            # Return a user-friendly response when LLM is not available
            return {
                'summary': 'LLM解读服务不可用',
                'key_points': ['政策关键要点需配置LLM服务后自动生成'],
                'support_measures': ['资金支持措施需配置LLM服务后自动生成'],
                'application_conditions': ['申请条件需配置LLM服务后自动生成'],
                'timeline': ['时间要求需配置LLM服务后自动生成'],
                'industry_impact': ['产业影响分析需配置LLM服务后自动生成'],
                'recommendations': ['申报建议需配置LLM服务后自动生成']
            }

    def _parse_llm_response(self, response_text: str) -> Dict:
        """Parse LLM response to extract structured information"""
        try:
            # Handle case where response_text is None
            if not response_text:
                logger.warning("LLM response is empty or None")
                return {
                    'summary': '政策解读',
                    'key_points': ['要点1', '要点2', '要点3'],
                    'support_measures': ['支持措施'],
                    'application_conditions': ['申请条件'],
                    'timeline': ['时间信息'],
                    'industry_impact': ['影响分析'],
                    'recommendations': ['申报建议']
                }

            # Since the LLM might return unstructured text, we'll extract key information using regex
            import re

            # Extract summary
            summary_matches = re.search(r'摘要|总结|概要[：:](.*?)(?=关键支持措施|适用条件|时间节点|$)', response_text, re.DOTALL | re.IGNORECASE)
            summary = summary_matches.group(1).strip() if summary_matches else "政策解读摘要"

            # Extract key points
            key_points_matches = re.findall(r'[•●\-](.+?)(?=\n|$)', response_text[:1000])  # First 1000 chars for key points
            key_points = [kp.strip() for kp in key_points_matches[:10] if kp and kp.strip()]  # Top 10 points

            # Extract support measures
            support_pattern = r'支持措施|资金支持|税收优惠[：:](.*?)(?=适用条件|时间节点|影响分析|$)'
            support_matches = re.search(support_pattern, response_text, re.DOTALL | re.IGNORECASE)
            support_measures = [support_matches.group(1)[:200].strip()] if support_matches and support_matches.group(1) else ["支持措施信息"]

            # Extract application conditions
            condition_pattern = r'适用条件|申报条件|资格要求[：:](.*?)(?=时间节点|影响分析|申报建议|$)'
            condition_matches = re.search(condition_pattern, response_text, re.DOTALL | re.IGNORECASE)
            application_conditions = [condition_matches.group(1)[:200].strip()] if condition_matches and condition_matches.group(1) else ["申请条件信息"]

            # Extract timeline
            timeline_pattern = r'时间节点|时间要求|截止时间[：:](.*?)(?=影响分析|申报建议|$)'
            timeline_matches = re.search(timeline_pattern, response_text, re.DOTALL | re.IGNORECASE)
            timeline = [timeline_matches.group(1)[:200].strip()] if timeline_matches and timeline_matches.group(1) else ["时间信息"]

            # Extract industry impact
            impact_pattern = r'影响分析|产业影响|预期效果[：:](.*?)(?=申报建议|总结|$)'
            impact_matches = re.search(impact_pattern, response_text, re.DOTALL | re.IGNORECASE)
            industry_impact = [impact_matches.group(1)[:200].strip()] if impact_matches and impact_matches.group(1) else ["影响分析"]

            # Extract recommendations
            rec_pattern = r'申报建议|注意事项|建议[：:](.*?)(?=$|\n\n)'
            rec_matches = re.search(rec_pattern, response_text, re.DOTALL | re.IGNORECASE)
            recommendations = [rec_matches.group(1)[:200].strip()] if rec_matches and rec_matches.group(1) else ["申报建议"]

            return {
                'summary': summary[:500],  # Limit length
                'key_points': key_points or ['政策关键要点'],
                'support_measures': support_measures,
                'application_conditions': application_conditions,
                'timeline': timeline,
                'industry_impact': industry_impact,
                'recommendations': recommendations
            }
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Return basic structure if parsing fails
            return {
                'summary': '政策解读',
                'key_points': ['要点1', '要点2', '要点3'],
                'support_measures': ['支持措施'],
                'application_conditions': ['申请条件'],
                'timeline': ['时间信息'],
                'industry_impact': ['影响分析'],
                'recommendations': ['申报建议']
            }

    def _extract_classification_info(self, content: str, title: str) -> Dict:
        """Extract classification info (region, industry, year)"""
        classification = {
            'region': self._extract_regions(content, title),
            'industry': self._extract_industries(content),
            'year': self._extract_year(content, title),
            'policy_type': self._determine_policy_type(content, title)
        }
        
        return classification

    def _extract_regions(self, content: str, title: str) -> List[str]:
        """Extract regions mentioned in the policy"""
        # Common region patterns
        region_patterns = [
            r'(?:在|对|支持|针对)(.*?)(?:市|省|区|县|州|地区|自治区|直辖市)',
            r'(.*?)(?:市|省|区|县|州|地区|自治区|直辖市)(?:发布|实施|出台)',
            r'(.*?)(?:市|省|区|县|州|地区|自治区|直辖市)[\u4e00-\u9fa5]*政策',
        ]
        
        import re
        regions = set()
        
        # Add title and content together for better extraction
        full_text = f"{title} {content}"
        
        for pattern in region_patterns:
            matches = re.findall(pattern, full_text)
            for match in matches:
                if len(match) <= 10:  # Reasonable length for region names
                    regions.add(match.strip())
        
        # Add common regions that might be mentioned differently
        common_regions = [
            "北京", "上海", "广州", "深圳", "成都", "重庆", "杭州", "南京", "武汉", "西安",
            "苏州", "天津", "青岛", "大连", "宁波", "厦门", "广州", "深圳", "成都", "西安"
        ]
        
        for region in common_regions:
            if region in full_text:
                regions.add(region)
        
        return list(regions)[:5]  # Return top 5 regions

    def _extract_industries(self, content: str) -> List[str]:
        """Extract industries mentioned in the policy"""
        # Common industry keywords
        industry_keywords = [
            "人工智能", "大数据", "云计算", "物联网", "5G", "区块链", "新能源", 
            "生物医药", "新材料", "高端制造", "数字经济", "智能制造", "集成电路",
            "新能源汽车", "生物医药", "新材料", "航空航天", "现代服务业", "现代农业",
            "信息技术", "生物技术", "新材料", "新能源", "高端装备制造", "节能环保"
        ]
        
        industries = set()
        
        for keyword in industry_keywords:
            if keyword in content:
                industries.add(keyword)
        
        return list(industries)

    def _extract_year(self, content: str, title: str) -> Optional[int]:
        """Extract the policy year"""
        import re
        
        # Look for 4-digit year patterns
        year_patterns = [
            r'(?:发布|实施|出台|执行)于?(\d{4})年',
            r'(\d{4})年(\d{1,2})月',
            r'(\d{4})年',
            r'(\d{4})-(?:\d{1,2})-(?:\d{1,2})'
        ]
        
        full_text = f"{title} {content}"
        
        for pattern in year_patterns:
            match = re.search(pattern, full_text)
            if match:
                year = int(match.group(1))
                if 1900 <= year <= 2030:  # Reasonable year range
                    return year
        
        return None

    def _determine_policy_type(self, content: str, title: str) -> str:
        """Determine the policy type"""
        type_indicators = {
            "扶持政策": ["扶持", "资助", "补贴", "奖励", "支持"],
            "税收优惠": ["税收", "减免", "优惠", "减税", "免税"],
            "准入政策": ["准入", "许可", "审批", "资质", "门槛"],
            "监管政策": ["监管", "规范", "整顿", "治理", "管理"],
            "发展规划": ["规划", "计划", "纲要", "方案", "布局"]
        }
        
        title_content = f"{title} {content}".lower()
        
        for policy_type, keywords in type_indicators.items():
            for keyword in keywords:
                if keyword in title_content:
                    return policy_type
        
        return "其他政策"

    def batch_analyze_policies(self, urls: List[str], company_profile: Optional[Dict] = None) -> List[Dict]:
        """Analyze multiple policy URLs"""
        results = []
        
        for i, url in enumerate(urls):
            logger.info(f"Progress: {i+1}/{len(urls)} - Analyzing: {url}")
            
            result = self.analyze_policy_from_url(url, company_profile)
            results.append(result)
        
        return results

    def generate_policy_summary(self, analysis_result: Dict) -> Dict:
        """Generate a comprehensive summary of policy analysis"""
        try:
            policy_analysis = analysis_result.get('policy_analysis', {})
            summary_data = policy_analysis.get('summary', {})
            
            summary = {
                "title": analysis_result.get('title', 'Unknown'),
                "highlights_count": summary_data.get('statistics', {}).get('total_highlights', 0),
                "subsidies_count": summary_data.get('statistics', {}).get('total_subsidies', 0),
                "tax_benefits_count": summary_data.get('statistics', {}).get('total_tax_benefits', 0),
                "upcoming_deadlines": summary_data.get('statistics', {}).get('upcoming_deadlines', 0),
                "regions": analysis_result.get('classification', {}).get('region', []),
                "industries": analysis_result.get('classification', {}).get('industry', []),
                "year": analysis_result.get('classification', {}).get('year'),
                "policy_type": analysis_result.get('classification', {}).get('policy_type'),
                "applicability_score": policy_analysis.get('applicability', {}).get('score', 0) if policy_analysis.get('applicability') else 0,
                "key_subsidies": [s['description'][:50] for s in summary_data.get('subsidies_and_taxes', {}).get('subsidies', [])[:3]],
                "key_deadlines": [t['date'] for t in summary_data.get('timeline', [])[:3] if t.get('is_future')],
            }
            
            return summary
        except Exception as e:
            logger.error(f"Error generating policy summary: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Test the integrator
    logging.basicConfig(level=logging.INFO)
    
    integrator = PolicyAnalysisIntegrator()
    
    # Test with a sample URL (this would be from email)
    test_url = "https://example.com/sample-policy"
    
    print(f"Testing policy analysis for: {test_url}")
    result = integrator.analyze_policy_from_url(test_url)
    
    if result.get('success'):
        print(f"✅ Analysis successful!")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Regions: {result.get('classification', {}).get('region', [])}")
        print(f"Industries: {result.get('classification', {}).get('industry', [])}")
        print(f"Year: {result.get('classification', {}).get('year')}")
        print(f"Policy Type: {result.get('classification', {}).get('policy_type')}")
    else:
        print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
    
    print("\n✅ Policy analysis integrator module ready!")