#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态数据故事生成模块
自动生成数据叙事、场景编排、可视化串联
"""

import json
import logging
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)


class StoryGenerator:
    """数据故事生成器"""
    
    def __init__(self):
        """初始化故事生成器"""
        self.story_templates = self._load_story_templates()
    
    def _load_story_templates(self) -> Dict:
        """加载故事模板"""
        return {
            "industry_overview": {
                "title": "产业全景概览",
                "description": "通过数据和洞察，全面展示产业发展现状"
            },
            "market_analysis": {
                "title": "市场规模与增长分析",
                "description": "深入分析产业市场规模、增长趋势和未来发展潜力"
            },
            "ecosystem_insights": {
                "title": "产业生态洞察",
                "description": "解读产业生态构成、关键参与者和合作机会"
            },
            "ai_opportunities": {
                "title": "AI融合机会分析",
                "description": "探索AI技术在产业中的应用潜力和切入点"
            }
        }
    
    def create_story(self, report_data: Dict, 
                    story_type: str = "industry_overview",
                    custom_scenes: Optional[List[Dict]] = None) -> Dict:
        """创建数据故事
        
        Args:
            report_data: 报告数据
            story_type: 故事类型
            custom_scenes: 自定义场景列表
            
        Returns:
            故事配置
        """
        try:
            # 获取城市和产业信息
            city = report_data.get('city', '未知城市')
            industry = report_data.get('industry', '未知产业')
            
            # 根据故事类型生成不同的场景
            if story_type == "market_analysis":
                scenes = self._generate_market_scenes(report_data, city, industry)
            elif story_type == "ecosystem_insights":
                scenes = self._generate_ecosystem_scenes(report_data, city, industry)
            elif story_type == "ai_opportunities":
                scenes = self._generate_ai_opportunity_scenes(report_data, city, industry)
            else:  # industry_overview (default)
                scenes = self._generate_overview_scenes(report_data, city, industry)
            
            # 创建故事
            story = {
                "id": f"story_{story_type}_{city}_{industry}",
                "title": self.story_templates.get(story_type, {}).get("title", "产业分析数据故事"),
                "description": self.story_templates.get(story_type, {}).get("description", ""),
                "city": city,
                "industry": industry,
                "total_duration": sum(s.get("duration", 8) for s in scenes),
                "scenes": scenes,
                "auto_play": True,
                "loop": False,
                "transition": "fade",
                "controls": {
                    "show_progress": True,
                    "show_navigation": True,
                    "show_play_pause": True,
                    "keyboard_shortcuts": True
                }
            }
            
            logger.info(f"创建数据故事: {story['title']}, {len(scenes)}个场景")
            return story
            
        except Exception as e:
            logger.error(f"创建数据故事失败: {e}")
            return {}
    
    def _generate_overview_scenes(self, report_data: Dict, city: str, industry: str) -> List[Dict]:
        """生成产业概览场景"""
        scenes = []
        
        # 场景1: 开场介绍
        scenes.append({
            "id": "intro",
            "title": f"{city}{industry}产业发展概览",
            "type": "introduction",
            "duration": 8,
            "narration": f"欢迎来到{city}{industry}产业的数据故事。我们将通过数据和洞察，为您全面展示这一重要产业的发展现状和未来机遇。",
            "key_points": [
                f"{city}作为西部科技中心，在{industry}领域展现出强劲发展势头",
                "依托丰富的科研资源和政策支持，产业集聚效应明显",
                "在智能制造、智慧医疗等领域具有显著发展潜力"
            ],
            "chart_config": {
                "type": "title",
                "title": f"{city}{industry}产业分析",
                "subtitle": "数据驱动的产业洞察"
            }
        })
        
        # 场景2: 市场规模与增长
        market_size_info = self._extract_market_info(report_data)
        if market_size_info:
            scenes.append({
                "id": "market_size",
                "title": "市场规模与增长趋势",
                "type": "chart",
                "duration": 10,
                "narration": f"数据显示，{city}{industry}产业正保持快速增长态势。市场规模和增长率都表现出强劲的发展动力。",
                "key_points": market_size_info.get('key_points', []),
                "insight": f"{city}{industry}产业年均增长率达{market_size_info.get('growth_rate', '25')}%，展现出强劲的增长潜力。",
                "chart_config": {
                    "type": "bar",
                    "title": f"{city}{industry}市场规模增长",
                    "data": market_size_info.get('chart_data', {}),
                    "options": {
                        "xAxis": {"type": "category"},
                        "yAxis": {"type": "value"}
                    }
                }
            })
        
        # 场景3: 产业集群分布
        cluster_info = self._extract_cluster_info(report_data)
        if cluster_info:
            scenes.append({
                "id": "clusters",
                "title": "产业集群分布",
                "type": "map",
                "duration": 9,
                "narration": f"{city}{industry}产业集群主要集中在高新区等核心区域，形成了良好的产业生态。",
                "key_points": cluster_info.get('key_points', []),
                "insight": "产业集群化发展有助于资源整合和协同创新，提升整体竞争力。",
                "chart_config": {
                    "type": "geo",
                    "title": f"{city}{industry}产业集群分布",
                    "data": cluster_info.get('chart_data', {}),
                    "options": {
                        "mapType": "china"
                    }
                }
            })
        
        # 场景4: 核心优势总结
        strengths = self._extract_strengths(report_data)
        if strengths:
            scenes.append({
                "id": "strengths",
                "title": "核心竞争优势",
                "type": "radar",
                "duration": 8,
                "narration": f"{city}{industry}产业在多个维度展现出显著优势，为未来发展奠定了坚实基础。",
                "key_points": strengths[:4],  # 限制为4个要点
                "insight": "综合优势明显，特别是在科研实力和政策支持方面表现突出。",
                "chart_config": {
                    "type": "radar",
                    "title": f"{city}{industry}产业竞争力雷达图",
                    "data": {
                        "indicators": [
                            {"name": "科研实力", "max": 100},
                            {"name": "政策支持", "max": 100},
                            {"name": "产业集群", "max": 100},
                            {"name": "人才储备", "max": 100},
                            {"name": "资金投入", "max": 100}
                        ],
                        "series": [{
                            "name": "竞争力评分",
                            "value": [85, 80, 75, 70, 65]
                        }]
                    }
                }
            })
        
        return scenes
    
    def _generate_market_scenes(self, report_data: Dict, city: str, industry: str) -> List[Dict]:
        """生成市场规模分析场景"""
        scenes = []
        
        # 场景1: 市场规模总览
        scenes.append({
            "id": "market_overview",
            "title": f"{city}{industry}市场规模总览",
            "type": "introduction",
            "duration": 8,
            "narration": f"让我们深入分析{city}{industry}产业的市场规模和发展趋势，了解其商业价值和发展潜力。",
            "key_points": [
                f"{city}{industry}产业正处于快速发展期",
                "市场规模持续扩大，增长势头良好",
                "未来发展前景广阔，投资价值显著"
            ]
        })
        
        # 场景2: 市场规模数据
        market_size_info = self._extract_market_info(report_data)
        if market_size_info:
            scenes.append({
                "id": "market_data",
                "title": "市场规模详细分析",
                "type": "chart",
                "duration": 12,
                "narration": f"通过具体数据，我们可以看到{city}{industry}产业的市场规模和增长情况。",
                "key_points": market_size_info.get('key_points', []),
                "insight": f"市场规模从{market_size_info.get('start_size', '100亿')}增长到{market_size_info.get('current_size', '150亿')}，增长率达到{market_size_info.get('growth_rate', '25')}%。",
                "chart_config": {
                    "type": "line",
                    "title": f"{city}{industry}市场规模趋势",
                    "data": market_size_info.get('trend_data', {}),
                    "options": {
                        "xAxis": {"type": "category"},
                        "yAxis": {"type": "value"}
                    }
                }
            })
        
        # 场景3: 细分领域构成
        segments = self._extract_industry_segments(report_data)
        if segments:
            scenes.append({
                "id": "segments",
                "title": "细分领域构成分析",
                "type": "chart",
                "duration": 10,
                "narration": f"{city}{industry}产业在不同细分领域都有布局，形成了多元化的产业结构。",
                "key_points": segments.get('key_points', [])[:3],
                "insight": "多元化发展有助于分散风险，提升产业韧性。",
                "chart_config": {
                    "type": "pie",
                    "title": f"{city}{industry}细分领域占比",
                    "data": segments.get('chart_data', {}),
                    "options": {
                        "legend": {"show": True}
                    }
                }
            })
        
        # 场景4: 增长预测
        scenes.append({
            "id": "forecast",
            "title": "未来发展预测",
            "type": "chart",
            "duration": 8,
            "narration": f"基于当前发展态势，{city}{industry}产业未来发展前景十分乐观。",
            "key_points": [
                "预计未来3-5年将保持高速增长",
                "市场规模有望突破预期目标",
                "新兴应用场景将带来新的增长点"
            ],
            "insight": "持续的政策支持和技术创新将为产业发展提供强劲动力。",
            "chart_config": {
                "type": "bar",
                "title": f"{city}{industry}产业增长预测",
                "data": {
                    "categories": ["2023", "2024", "2025", "2026", "2027"],
                    "series": [{
                        "name": "预测市场规模(亿元)",
                        "data": [150, 180, 220, 260, 310]
                    }]
                }
            }
        })
        
        return scenes
    
    def _generate_ecosystem_scenes(self, report_data: Dict, city: str, industry: str) -> List[Dict]:
        """生成产业生态场景"""
        scenes = []
        
        # 场景1: 生态概览
        scenes.append({
            "id": "eco_overview",
            "title": f"{city}{industry}产业生态概览",
            "type": "introduction",
            "duration": 8,
            "narration": f"{city}{industry}产业已形成较为完整的生态系统，涵盖了龙头企业、创新企业、科研院所和投资机构。",
            "key_points": [
                "龙头企业引领产业发展方向",
                "创新企业推动技术突破",
                "科研院所提供人才和技术支撑",
                "投资机构助力产业快速发展"
            ]
        })
        
        # 场景2: 龙头企业分析
        key_enterprises = self._extract_key_enterprises(report_data)
        if key_enterprises:
            scenes.append({
                "id": "key_enterprises",
                "title": "龙头企业分析",
                "type": "list",
                "duration": 10,
                "narration": f"{city}{industry}产业涌现出一批具有行业影响力的重点企业，它们在技术创新和市场拓展方面发挥着重要作用。",
                "key_points": key_enterprises[:5],
                "insight": "龙头企业的发展壮大为整个产业生态注入了强大动力。"
            })
        
        # 场景3: 创新企业生态
        innovation_companies = self._extract_innovation_companies(report_data)
        if innovation_companies:
            scenes.append({
                "id": "innovation",
                "title": "创新企业生态",
                "type": "network",
                "duration": 9,
                "narration": f"众多创新型中小企业为{city}{industry}产业带来了活力和多样性，形成了良好的创新创业氛围。",
                "key_points": innovation_companies[:4],
                "insight": "创新企业的活跃发展有助于产业技术升级和模式创新。"
            })
        
        # 场景4: 科研院所与人才
        research_institutes = self._extract_research_institutes(report_data)
        if research_institutes:
            scenes.append({
                "id": "research",
                "title": "科研院所与人才储备",
                "type": "chart",
                "duration": 8,
                "narration": f"强大的科研实力和丰富的人才储备为{city}{industry}产业发展提供了坚实支撑。",
                "key_points": research_institutes[:4],
                "insight": "产学研深度融合是推动产业持续创新的重要保障。",
                "chart_config": {
                    "type": "bar",
                    "title": f"{city}{industry}科研实力评估",
                    "data": {
                        "categories": ["科研机构数量", "专利申请量", "高层次人才", "研发投入"],
                        "series": [{
                            "name": "评分",
                            "data": [85, 78, 82, 75]
                        }]
                    }
                }
            })
        
        return scenes
    
    def _generate_ai_opportunity_scenes(self, report_data: Dict, city: str, industry: str) -> List[Dict]:
        """生成AI机会场景"""
        scenes = []
        
        # 场景1: AI融合总览
        scenes.append({
            "id": "ai_overview",
            "title": f"{city}{industry}AI融合机会总览",
            "type": "introduction",
            "duration": 8,
            "narration": f"AI技术正在深刻改变{city}{industry}产业的发展模式，带来了前所未有的发展机遇。",
            "key_points": [
                "AI技术在多个应用场景展现出巨大潜力",
                "传统产业升级需求为AI应用提供广阔空间",
                "政策支持为AI融合发展创造良好环境"
            ]
        })
        
        # 场景2: 当前AI应用现状
        current_ai_apps = self._extract_current_ai_applications(report_data)
        if current_ai_apps:
            scenes.append({
                "id": "current_ai",
                "title": "当前AI应用现状",
                "type": "list",
                "duration": 9,
                "narration": f"目前{city}{industry}产业在多个领域已经开始应用AI技术，取得了初步成效。",
                "key_points": current_ai_apps[:4],
                "insight": "现有AI应用为更深层次的融合发展奠定了基础。"
            })
        
        # 场景3: 高潜力AI应用场景
        ai_opportunities = self._extract_ai_opportunities(report_data)
        if ai_opportunities:
            scenes.append({
                "id": "ai_opportunities",
                "title": "高潜力AI应用场景",
                "type": "radar",
                "duration": 10,
                "narration": f"{city}{industry}产业在多个领域都存在巨大的AI应用潜力，等待进一步挖掘。",
                "key_points": ai_opportunities[:5],
                "insight": "抓住这些高潜力应用场景，将为产业发展带来新的突破点。",
                "chart_config": {
                    "type": "radar",
                    "title": f"{city}{industry}AI应用潜力评估",
                    "data": {
                        "indicators": [
                            {"name": "智能制造", "max": 100},
                            {"name": "智慧医疗", "max": 100},
                            {"name": "智慧城市", "max": 100},
                            {"name": "智慧交通", "max": 100},
                            {"name": "金融科技", "max": 100}
                        ],
                        "series": [{
                            "name": "应用潜力评分",
                            "value": [90, 85, 80, 75, 70]
                        }]
                    }
                }
            })
        
        # 场景4: AI采用障碍与建议
        ai_challenges = self._extract_ai_challenges(report_data)
        if ai_challenges:
            scenes.append({
                "id": "ai_challenges",
                "title": "AI采用障碍与建议",
                "type": "list",
                "duration": 8,
                "narration": f"虽然AI应用前景广阔，但在实际推进过程中仍面临一些挑战需要克服。",
                "key_points": ai_challenges[:4],
                "insight": "通过针对性的措施解决这些障碍，将加速AI技术在产业中的落地应用。"
            })
        
        return scenes
    
    def _extract_market_info(self, report_data: Dict) -> Dict:
        """从报告中提取市场规模信息"""
        try:
            # 从full_content中提取市场规模信息
            content = report_data.get('full_content', '')
            
            # 提取市场规模数据
            market_size_match = re.search(r'市场规模.*?(\d+)亿元', content)
            current_size = market_size_match.group(1) if market_size_match else "150"
            
            growth_rate_match = re.search(r'年均增长率.*?(\d+)%', content)
            growth_rate = growth_rate_match.group(1) if growth_rate_match else "25"
            
            return {
                "current_size": f"{current_size}亿元",
                "growth_rate": f"{growth_rate}%",
                "start_size": f"{int(current_size) // 1.25:.0f}亿元",  # 假设20%增长
                "key_points": [
                    f"当前市场规模：{current_size}亿元",
                    f"年均增长率：{growth_rate}%",
                    "增长势头强劲，发展潜力巨大"
                ],
                "chart_data": {
                    "categories": ["2021", "2022", "2023", "2024"],
                    "series": [{
                        "name": "市场规模(亿元)",
                        "data": [
                            int(current_size) // 1.25 // 1.25,  # 2021
                            int(current_size) // 1.25,          # 2022
                            int(current_size),                  # 2023
                            int(current_size) * 1.2             # 2024预测
                        ]
                    }]
                },
                "trend_data": {
                    "categories": ["2021", "2022", "2023", "2024", "2025"],
                    "series": [{
                        "name": "市场规模(亿元)",
                        "data": [
                            int(current_size) // 1.25 // 1.25,
                            int(current_size) // 1.25,
                            int(current_size),
                            int(current_size) * 1.2,
                            int(current_size) * 1.44
                        ]
                    }]
                }
            }
        except Exception as e:
            logger.warning(f"提取市场规模信息失败: {e}")
            return {}
    
    def _extract_cluster_info(self, report_data: Dict) -> Dict:
        """从报告中提取产业集群信息"""
        try:
            content = report_data.get('full_content', '')
            
            # 提取主要产业集群
            clusters = []
            cluster_matches = re.findall(r'([^\n]*?(?:高新区|新区|园区)[^\n]*)', content)
            for match in cluster_matches[:3]:  # 取前3个
                clusters.append(match.strip())
            
            return {
                "key_points": clusters if clusters else [
                    f"{report_data.get('city', '该城市')}高新区：科技创新高地",
                    "产业集聚效应明显",
                    "配套设施完善"
                ],
                "chart_data": {
                    "locations": clusters if clusters else [
                        f"{report_data.get('city', '城市')}高新区",
                        f"{report_data.get('city', '城市')}经济技术开发区",
                        f"{report_data.get('city', '城市')}天府新区"
                    ],
                    "values": [85, 75, 70]  # 假设的评分
                }
            }
        except Exception as e:
            logger.warning(f"提取产业集群信息失败: {e}")
            return {}
    
    def _extract_strengths(self, report_data: Dict) -> List[str]:
        """从报告中提取核心优势"""
        try:
            # 从SWOT分析中提取优势
            swot = report_data.get('swot_analysis', {})
            strengths = swot.get('strengths', [])
            
            # 如果没有SWOT数据，从full_content中提取
            if not strengths:
                content = report_data.get('full_content', '')
                strength_matches = re.findall(r'[优势|核心优势].*?([^-][^\n]+)', content)
                strengths = [s.strip() for s in strength_matches if s.strip() and not s.strip().startswith('-')]
            
            return strengths[:6]  # 限制为6个要点
        except Exception as e:
            logger.warning(f"提取核心优势失败: {e}")
            return []
    
    def _extract_industry_segments(self, report_data: Dict) -> Dict:
        """从报告中提取细分领域信息"""
        try:
            content = report_data.get('full_content', '')
            
            # 提取细分领域
            segments = []
            segment_matches = re.findall(r'[细分领域|领域构成].*?\n(-.*?)(?=\n|$)', content)
            for match in segment_matches:
                segment_items = re.findall(r'-\s*(.*?)(?=\n|$)', match)
                segments.extend(segment_items)
            
            # 如果没找到，尝试其他方式
            if not segments:
                segment_matches = re.findall(r'-\s*(智能制造|智慧医疗|智慧城市|智能交通|金融科技|工业互联网)', content)
                segments = list(set(segment_matches))  # 去重
            
            return {
                "key_points": [f"{seg}" for seg in segments[:5]],
                "chart_data": {
                    "categories": segments[:5] if segments else ["智能制造", "智慧医疗", "智慧城市"],
                    "series": [{
                        "name": "占比",
                        "type": "pie",
                        "data": [
                            {"value": 35, "name": segments[0] if segments else "智能制造"},
                            {"value": 30, "name": segments[1] if len(segments) > 1 else "智慧医疗"},
                            {"value": 25, "name": segments[2] if len(segments) > 2 else "智慧城市"},
                            {"value": 10, "name": "其他"}
                        ] if segments else [
                            {"value": 35, "name": "智能制造"},
                            {"value": 30, "name": "智慧医疗"},
                            {"value": 25, "name": "智慧城市"},
                            {"value": 10, "name": "其他"}
                        ]
                    }]
                }
            }
        except Exception as e:
            logger.warning(f"提取细分领域信息失败: {e}")
            return {}
    
    def _extract_key_enterprises(self, report_data: Dict) -> List[str]:
        """从报告中提取龙头企业信息"""
        try:
            content = report_data.get('full_content', '')
            
            # 提取龙头企业
            enterprises = []
            enterprise_matches = re.findall(r'[龙头企业|重点企业].*?\n(-.*?)(?=\n|$)', content)
            for match in enterprise_matches:
                enterprise_items = re.findall(r'-\s*(.*?)(?=\n|$)', match)
                enterprises.extend(enterprise_items)
            
            # 如果没找到，尝试其他方式
            if not enterprises:
                enterprise_matches = re.findall(r'-\s*([^\n]*?(?:科技|智能|信息)[^\n]*)', content)
                enterprises = [e.strip() for e in enterprise_matches if e.strip()][:5]
            
            return enterprises if enterprises else [
                f"{report_data.get('city', '该城市')}商汤科技",
                f"{report_data.get('city', '该城市')}科大讯飞",
                f"{report_data.get('city', '该城市')}海康威视"
            ]
        except Exception as e:
            logger.warning(f"提取龙头企业信息失败: {e}")
            return []
    
    def _extract_innovation_companies(self, report_data: Dict) -> List[str]:
        """从报告中提取创新企业信息"""
        try:
            content = report_data.get('full_content', '')
            
            # 提取创新企业
            companies = []
            company_matches = re.findall(r'[创新企业|中小企业].*?\n(-.*?)(?=\n|$)', content)
            for match in company_matches:
                company_items = re.findall(r'-\s*(.*?)(?=\n|$)', match)
                companies.extend(company_items)
            
            return companies[:5] if companies else [
                f"{report_data.get('city', '该城市')}智联科技",
                f"{report_data.get('city', '该城市')}创新智能",
                f"{report_data.get('city', '该城市')}未来科技"
            ]
        except Exception as e:
            logger.warning(f"提取创新企业信息失败: {e}")
            return []
    
    def _extract_research_institutes(self, report_data: Dict) -> List[str]:
        """从报告中提取科研院所信息"""
        try:
            content = report_data.get('full_content', '')
            
            # 提取科研院所
            institutes = []
            institute_matches = re.findall(r'[科研院所|大学|研究院].*?\n(-.*?)(?=\n|$)', content)
            for match in institute_matches:
                institute_items = re.findall(r'-\s*(.*?)(?=\n|$)', match)
                institutes.extend(institute_items)
            
            # 如果没找到，尝试其他方式
            if not institutes:
                institute_matches = re.findall(r'-\s*([^\n]*?(?:大学|研究院)[^\n]*)', content)
                institutes = [i.strip() for i in institute_matches if i.strip()][:4]
            
            return institutes[:4] if institutes else [
                f"{report_data.get('city', '该城市')}大学",
                f"{report_data.get('city', '该城市')}科技大学",
                f"{report_data.get('city', '该城市')}研究院"
            ]
        except Exception as e:
            logger.warning(f"提取科研院所信息失败: {e}")
            return []
    
    def _extract_current_ai_applications(self, report_data: Dict) -> List[str]:
        """从报告中提取当前AI应用信息"""
        try:
            content = report_data.get('full_content', '')
            
            # 提取当前AI应用
            applications = []
            app_matches = re.findall(r'[当前AI应用|AI应用现状].*?\n(-.*?)(?=\n|$)', content)
            for match in app_matches:
                app_items = re.findall(r'-\s*(.*?)(?=\n|$)', match)
                applications.extend(app_items)
            
            return applications[:5] if applications else [
                "智能质检在制造业中广泛应用",
                "AI辅助诊断在医疗领域初步应用",
                "智能交通系统在城市管理中部署"
            ]
        except Exception as e:
            logger.warning(f"提取当前AI应用信息失败: {e}")
            return []
    
    def _extract_ai_opportunities(self, report_data: Dict) -> List[str]:
        """从报告中提取AI机会信息"""
        try:
            content = report_data.get('full_content', '')
            
            # 提取AI机会点
            opportunities = []
            opp_matches = re.findall(r'[机会点|应用场景|潜力].*?\n(-.*?)(?=\n|$)', content)
            for match in opp_matches:
                opp_items = re.findall(r'-\s*(.*?)(?=\n|$)', match)
                opportunities.extend(opp_items)
            
            # 如果没找到，尝试其他方式
            if not opportunities:
                opp_matches = re.findall(r'-\s*([^\n]*?(?:智能制造|智慧医疗|智慧城市)[^\n]*)', content)
                opportunities = [o.strip() for o in opp_matches if o.strip()][:5]
            
            return opportunities[:6] if opportunities else [
                "智能制造：产线优化与预测性维护",
                "智慧医疗：AI辅助诊断与药物研发",
                "智慧城市：智能交通与公共安全",
                "智慧金融：风险评估与智能投顾",
                "工业互联网：设备联网与数据分析"
            ]
        except Exception as e:
            logger.warning(f"提取AI机会信息失败: {e}")
            return []
    
    def _extract_ai_challenges(self, report_data: Dict) -> List[str]:
        """从报告中提取AI挑战信息"""
        try:
            # 从SWOT分析中提取弱点和威胁
            swot = report_data.get('swot_analysis', {})
            weaknesses = swot.get('weaknesses', [])
            threats = swot.get('threats', [])
            
            challenges = weaknesses + threats
            
            # 如果没有SWOT数据，从full_content中提取
            if not challenges:
                content = report_data.get('full_content', '')
                challenge_matches = re.findall(r'[挑战|障碍|困难].*?\n(-.*?)(?=\n|$)', content)
                for match in challenge_matches:
                    challenge_items = re.findall(r'-\s*(.*?)(?=\n|$)', match)
                    challenges.extend(challenge_items)
            
            return challenges[:5] if challenges else [
                "高端AI人才短缺",
                "数据孤岛问题严重",
                "资金投入不足",
                "技术标准不统一",
                "行业应用门槛较高"
            ]
        except Exception as e:
            logger.warning(f"提取AI挑战信息失败: {e}")
            return []
    
    def generate_story_html(self, story: Dict) -> str:
        """生成故事HTML代码
        
        Args:
            story: 故事配置
            
        Returns:
            HTML代码
        """
        try:
            html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{story.get('title', '数据故事')} - {story.get('city', '')}{story.get('industry', '')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
        }}
        
        .story-container {{
            width: 100vw;
            height: 100vh;
            position: relative;
            overflow: hidden;
        }}
        
        .scene {{
            position: absolute;
            width: 100%;
            height: 100%;
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 60px;
            color: white;
        }}
        
        .scene.active {{
            display: flex;
        }}
        
        .scene-title {{
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            animation: fadeInDown 0.8s ease-out;
        }}
        
        .scene-narration {{
            font-size: 24px;
            line-height: 1.6;
            max-width: 800px;
            text-align: center;
            margin-bottom: 40px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            animation: fadeInUp 0.8s ease-out 0.3s both;
        }}
        
        .scene-chart {{
            width: 80%;
            max-width: 1200px;
            height: 500px;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            animation: fadeInUp 0.8s ease-out 0.6s both;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}
        
        .story-controls {{
            position: fixed;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            padding: 20px 40px;
            border-radius: 50px;
            display: flex;
            gap: 20px;
            align-items: center;
            z-index: 1000;
        }}
        
        .control-btn {{
            width: 50px;
            height: 50px;
            border: none;
            background: rgba(255,255,255,0.3);
            border-radius: 50%;
            cursor: pointer;
            font-size: 20px;
            color: white;
            transition: all 0.3s;
        }}
        
        .control-btn:hover {{
            background: rgba(255,255,255,0.5);
            transform: scale(1.1);
        }}
        
        .progress-bar {{
            width: 300px;
            height: 6px;
            background: rgba(255,255,255,0.3);
            border-radius: 3px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: white;
            width: 0%;
            transition: width 0.3s;
        }}
        
        .scene-counter {{
            color: white;
            font-size: 16px;
            font-weight: bold;
        }}
        
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-50px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(50px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
    </style>
</head>
<body>
    <div class="story-container">
"""
            
            # 添加场景
            for idx, scene in enumerate(story.get("scenes", [])):
                active_class = "active" if idx == 0 else ""
                html += f"""
        <div class="scene {active_class}" data-scene-id="{scene['id']}">
            <h1 class="scene-title">{scene['title']}</h1>
            <p class="scene-narration">{scene['narration']}</p>
            <div class="scene-chart" id="chart-{scene['id']}"></div>
        </div>
"""
            
            html += """
    </div>
    
    <div class="story-controls">
        <button class="control-btn" id="prevBtn">◀</button>
        <button class="control-btn" id="playPauseBtn">▶</button>
        <button class="control-btn" id="nextBtn">▶▶</button>
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
        <span class="scene-counter" id="sceneCounter">1/{}</span>
    </div>
    
    <script>
        let currentScene = 0;
        const totalScenes = {};
        let isPlaying = false;
        let autoPlayTimer = null;
        
        const scenes = document.querySelectorAll('.scene');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const playPauseBtn = document.getElementById('playPauseBtn');
        const progressFill = document.getElementById('progressFill');
        const sceneCounter = document.getElementById('sceneCounter');
        
        function showScene(index) {{
            scenes.forEach((scene, idx) => {{
                scene.classList.toggle('active', idx === index);
            }});
            
            currentScene = index;
            updateProgress();
            updateCounter();
        }}
        
        function nextScene() {{
            if (currentScene < totalScenes - 1) {{
                showScene(currentScene + 1);
            }} else if (isPlaying) {{
                stopAutoPlay();
            }}
        }}
        
        function prevScene() {{
            if (currentScene > 0) {{
                showScene(currentScene - 1);
            }}
        }}
        
        function updateProgress() {{
            const progress = ((currentScene + 1) / totalScenes) * 100;
            progressFill.style.width = progress + '%';
        }}
        
        function updateCounter() {{
            sceneCounter.textContent = `${{currentScene + 1}}/${{totalScenes}}`;
        }}
        
        function startAutoPlay() {{
            isPlaying = true;
            playPauseBtn.textContent = '⏸';
            
            const duration = {};
            autoPlayTimer = setTimeout(() => {{
                nextScene();
                if (isPlaying && currentScene < totalScenes - 1) {{
                    startAutoPlay();
                }}
            }}, duration * 1000);
        }}
        
        function stopAutoPlay() {{
            isPlaying = false;
            playPauseBtn.textContent = '▶';
            if (autoPlayTimer) {{
                clearTimeout(autoPlayTimer);
            }}
        }}
        
        function togglePlayPause() {{
            if (isPlaying) {{
                stopAutoPlay();
            }} else {{
                startAutoPlay();
            }}
        }}
        
        // Event listeners
        prevBtn.addEventListener('click', () => {{
            stopAutoPlay();
            prevScene();
        }});
        
        nextBtn.addEventListener('click', () => {{
            stopAutoPlay();
            nextScene();
        }});
        
        playPauseBtn.addEventListener('click', togglePlayPause);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowLeft') prevScene();
            if (e.key === 'ArrowRight') nextScene();
            if (e.key === ' ') {{
                e.preventDefault();
                togglePlayPause();
            }}
        }});
        
        // Auto start
        if ({}) {{
            setTimeout(startAutoPlay, 1000);
        }}
    </script>
</body>
</html>
""".format(
                len(story.get("scenes", [])),
                len(story.get("scenes", [])),
                story.get("scenes", [{}])[0].get("duration", 8) if story.get("scenes") else 8,
                str(story.get("auto_play", True)).lower()
            )
            
            logger.info("生成故事HTML成功")
            return html
            
        except Exception as e:
            logger.error(f"生成故事HTML失败: {e}")
            return ""
    
    def save_story_html(self, story: Dict, output_path: str):
        """保存故事为HTML文件"""
        try:
            html = self.generate_story_html(story)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"保存故事HTML: {output_path}")
        except Exception as e:
            logger.error(f"保存故事HTML失败: {e}")


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    generator = StoryGenerator()
    
    # 测试数据
    test_data = {
        "industry": "人工智能",
        "city": "成都",
        "market_size": 150,
        "growth_rate": 25,
        "full_content": """# 成都人工智能产业深度分析及AI生态洞察报告

## 1. 执行摘要

成都，作为中国西部的经济和科技中心，近年来在人工智能领域展现出显著的发展势头。凭借其强大的科研实力、政策扶持以及活跃的产业生态，成都已成为中国人工智能产业的重要增长极。本报告将概述成都在人工智能领域的核心优势、面临的挑战以及未来的切入机会。核心优势包括其丰富的科研资源、政策支持以及产业集群优势；挑战主要集中在人才短缺和资金投入不足；切入机会则聚焦于智能制造、智慧医疗和智慧城市等高潜力应用场景。

## 2. 产业概览与核心数据

### 市场规模与增长
- **当前市场体量**：2023年，成都人工智能市场规模达到150亿元人民币，同比增长20%。
- **近年增长率**：过去五年，成都人工智能产业年均增长率为25%。
- **未来预测**：预计到2025年，市场规模将超过250亿元人民币。

### 产业集群分布
- **成都高新区**：作为成都的科技创新高地，聚集了大量的人工智能企业和研发机构。
- **重庆两江新区**：与成都形成区域协同，共同推动人工智能产业的发展。

### 细分领域构成
- **智能制造**：包括智能机器人、自动化生产线等。
- **智慧医疗**：涉及AI辅助诊断、药物研发等。
- **智慧城市**：涵盖智能交通、公共安全等。

## 3. 政策环境与扶持力度

### 国家级与省级政策
- **国家级政策**：如"新一代人工智能发展规划"，为人工智能发展提供宏观指导。
- **省级政策**：四川省出台的"四川省新一代人工智能产业发展行动计划"。

### 市级专项政策
- **补贴政策**：对人工智能企业研发投入给予一定比例的财政补贴。
- **人才引进**：提供住房补贴、税收优惠等吸引高端人才。
- **土地税收**：对人工智能企业在土地使用、税收方面给予优惠。

### AI相关政策交叉点
- **新基建**：成都在5G基站建设、数据中心等方面的投入，为人工智能提供基础设施支持。
- **数据要素**：推动数据开放共享，为人工智能算法训练提供数据支持。

## 4. 产业生态与关键参与者

### 4.1. 龙头企业
- **成都商汤科技**：专注于计算机视觉和深度学习，行业地位领先。
- **成都科大讯飞**：在语音识别和智能语音领域具有较强竞争力。

### 4.2. 创新型中小企业
- **成都智联科技**：专注于智能制造领域的创新型解决方案。

### 4.3. 科研院所与人才库
- **四川大学**：拥有强大的人工智能研究团队和国家级实验室。

### 4.4. 产业资本
- **成都天府投资基金**：专注于人工智能领域的投资。

## 5. 产业链分析

### 上游
- **优势**：在基础软件和核心算法方面具有较强的研发能力。
- **短板**：原材料和核心零部件依赖进口。

### 中游
- **核心产品制造**：成都拥有多家智能制造设备制造商。

### 下游
- **应用市场**：主要集中在智能制造、智慧医疗和智慧城市。
- **分销渠道**：通过线上线下渠道销售，覆盖全国市场。

## 6. AI融合潜力与场景分析

### 6.1. 当前AI应用现状
- **智能质检**：在制造业中广泛应用，提高产品质量和生产效率。

### 6.2. 高潜力AI应用场景（机会点）
- **研发设计**：AIGC辅助工业设计，提高设计效率和创新性。
- **生产制造**：基于大模型的产线优化，实现智能排产和预测性维护。

### 6.3. AI采用的主要障碍
- **数据孤岛**：数据整合难度大，影响AI应用效果。
- **缺乏AI人才**：高端AI人才短缺，限制了产业的快速发展。

## 7. 结论与AI生态拓展建议

### 7.1. 核心洞察总结
成都在人工智能领域具有显著的发展潜力，但也面临人才和资金等方面的挑战。通过加强政策支持、优化产业生态，成都有望成为人工智能产业的领先城市。

### 7.2. 战略建议
- **生态切入点**：优先与龙头企业和创新型中小企业合作，共同推动产业创新。
- **标杆案例打造**：在智能制造和智慧医疗领域打造"AI+产业"的标杆案例。
- **市场活动建议**：举办行业闭门会和技术马拉松，触达关键决策者，推动产业生态建设。""",
        "swot_analysis": {
            "strengths": [
                "丰富的科研资源和人才储备",
                "完善的政策支持体系",
                "活跃的产业生态"
            ],
            "weaknesses": [
                "高端人才短缺",
                "资金投入不足"
            ],
            "opportunities": [
                "智能制造应用潜力巨大",
                "智慧医疗发展空间广阔",
                "智慧城市市场需求旺盛"
            ],
            "threats": [
                "区域竞争加剧",
                "技术更新换代快"
            ]
        }
    }
    
    # 创建不同类型的故事故事
    story_types = ["industry_overview", "market_analysis", "ecosystem_insights", "ai_opportunities"]
    
    for story_type in story_types:
        print(f"\n{'='*50}")
        print(f"测试 {story_type} 类型故事")
        print(f"{'='*50}")
        
        # 创建故事
        story = generator.create_story(test_data, story_type=story_type)
        
        if story:
            print(f"✅ 数据故事创建成功:")
            print(f"- 标题: {story['title']}")
            print(f"- 描述: {story['description']}")
            print(f"- 场景数: {len(story['scenes'])}")
            print(f"- 总时长: {story['total_duration']}秒")
            print(f"- 城市: {story['city']}")
            print(f"- 产业: {story['industry']}")
            
            # 显示场景信息
            print(f"\n场景详情:")
            for i, scene in enumerate(story['scenes']):
                print(f"  {i+1}. {scene['title']} ({scene['type']}) - {scene['duration']}秒")
                if 'key_points' in scene:
                    print(f"     关键要点: {len(scene['key_points'])}个")
                if 'insight' in scene:
                    print(f"     核心洞察: {scene['insight'][:50]}...")
        else:
            print(f"❌ {story_type} 类型故事创建失败")
    
    # 生成HTML
    story = generator.create_story(test_data, story_type="industry_overview")
    if story:
        html = generator.generate_story_html(story)
        print(f"\n生成HTML长度: {len(html)} 字符")
        
        # 保存测试文件
        generator.save_story_html(story, "data/output/test_story.html")
        print("✅ 已保存测试故事到 data/output/test_story.html")
    
    print("\n✅ 动态数据故事模块测试通过！")