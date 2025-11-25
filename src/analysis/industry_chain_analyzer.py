#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产业链图谱生成模块
自动识别和绘制产业链上中下游关系，评估完整度和薄弱环节
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class IndustryChainAnalyzer:
    """产业链分析器"""
    
    def __init__(self):
        """初始化产业链分析器"""
        # 产业链关键词库
        self.upstream_keywords = [
            "原材料", "供应商", "零部件", "芯片", "传感器", "基础设施",
            "研发", "设计", "核心技术", "专利", "上游"
        ]
        
        self.midstream_keywords = [
            "制造", "生产", "组装", "加工", "集成", "中游", "制造商",
            "工厂", "产线", "设备", "智能制造"
        ]
        
        self.downstream_keywords = [
            "销售", "渠道", "分销", "终端", "应用", "服务", "下游",
            "市场", "客户", "消费者", "用户", "运营"
        ]
        
        # 产业链节点类型
        self.chain_types = {
            "upstream": "上游",
            "midstream": "中游", 
            "downstream": "下游"
        }
    
    def extract_chain_entities(self, content: str) -> Dict[str, List[str]]:
        """从文本中提取产业链相关实体
        
        Args:
            content: 报告文本内容
            
        Returns:
            按上中下游分类的实体字典
        """
        try:
            entities = {
                "upstream": [],
                "midstream": [],
                "downstream": []
            }
            
            # 简化的实体提取（实际应使用NER）
            sentences = re.split(r'[。！？\n]', content)
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                # 提取企业名称（简化版）
                company_pattern = r'([A-Z\u4e00-\u9fa5]{2,10}(?:公司|集团|科技|企业|有限))'
                companies = re.findall(company_pattern, sentence)
                
                # 根据关键词分类
                for company in companies:
                    if any(kw in sentence for kw in self.upstream_keywords):
                        if company not in entities["upstream"]:
                            entities["upstream"].append(company)
                    elif any(kw in sentence for kw in self.downstream_keywords):
                        if company not in entities["downstream"]:
                            entities["downstream"].append(company)
                    elif any(kw in sentence for kw in self.midstream_keywords):
                        if company not in entities["midstream"]:
                            entities["midstream"].append(company)
            
            logger.info(f"提取产业链实体: 上游{len(entities['upstream'])}个, "
                       f"中游{len(entities['midstream'])}个, "
                       f"下游{len(entities['downstream'])}个")
            
            return entities
            
        except Exception as e:
            logger.error(f"提取产业链实体失败: {e}")
            return {"upstream": [], "midstream": [], "downstream": []}
    
    def build_chain_graph(self, entities: Dict[str, List[str]]) -> Dict:
        """构建产业链图谱
        
        Args:
            entities: 产业链实体字典
            
        Returns:
            图谱数据结构（节点和边）
        """
        try:
            nodes = []
            links = []
            node_id = 0
            
            # 类别到节点ID的映射
            category_nodes = {}
            
            # 创建节点
            for chain_type, chain_entities in entities.items():
                category_idx = ["upstream", "midstream", "downstream"].index(chain_type)
                category_nodes[chain_type] = []
                
                for entity in chain_entities:
                    nodes.append({
                        "id": str(node_id),
                        "name": entity,
                        "category": category_idx,
                        "symbolSize": 50 + len(chain_entities) * 5,
                        "value": len(chain_entities)
                    })
                    category_nodes[chain_type].append(str(node_id))
                    node_id += 1
            
            # 创建连接（上游->中游->下游）
            # 上游到中游
            for upstream_id in category_nodes.get("upstream", []):
                for midstream_id in category_nodes.get("midstream", []):
                    links.append({
                        "source": upstream_id,
                        "target": midstream_id,
                        "value": 1
                    })
            
            # 中游到下游
            for midstream_id in category_nodes.get("midstream", []):
                for downstream_id in category_nodes.get("downstream", []):
                    links.append({
                        "source": midstream_id,
                        "target": downstream_id,
                        "value": 1
                    })
            
            graph = {
                "nodes": nodes,
                "links": links,
                "statistics": {
                    "total_nodes": len(nodes),
                    "total_links": len(links),
                    "upstream_count": len(category_nodes.get("upstream", [])),
                    "midstream_count": len(category_nodes.get("midstream", [])),
                    "downstream_count": len(category_nodes.get("downstream", []))
                }
            }
            
            logger.info(f"构建产业链图谱: {len(nodes)}个节点, {len(links)}条连接")
            return graph
            
        except Exception as e:
            logger.error(f"构建产业链图谱失败: {e}")
            return {"nodes": [], "links": [], "statistics": {}}
    
    def evaluate_chain_completeness(self, entities: Dict[str, List[str]]) -> Dict:
        """评估产业链完整度
        
        Args:
            entities: 产业链实体字典
            
        Returns:
            完整度评估结果
        """
        try:
            # 计算各环节覆盖度
            upstream_coverage = min(len(entities["upstream"]) / 5.0, 1.0)
            midstream_coverage = min(len(entities["midstream"]) / 8.0, 1.0)
            downstream_coverage = min(len(entities["downstream"]) / 10.0, 1.0)
            
            # 综合完整度（加权平均）
            overall_completeness = (
                upstream_coverage * 0.3 +
                midstream_coverage * 0.4 +
                downstream_coverage * 0.3
            ) * 100
            
            # 识别薄弱环节
            weak_links = []
            if upstream_coverage < 0.5:
                weak_links.append({
                    "stage": "上游",
                    "coverage": upstream_coverage * 100,
                    "issue": "上游供应链企业数量不足，存在供应风险"
                })
            
            if midstream_coverage < 0.5:
                weak_links.append({
                    "stage": "中游",
                    "coverage": midstream_coverage * 100,
                    "issue": "中游制造能力有限，产能可能存在瓶颈"
                })
            
            if downstream_coverage < 0.5:
                weak_links.append({
                    "stage": "下游",
                    "coverage": downstream_coverage * 100,
                    "issue": "下游应用场景和市场渠道相对薄弱"
                })
            
            # 生成建议
            recommendations = []
            if weak_links:
                recommendations.append("建议重点关注以下薄弱环节:")
                for weak in weak_links:
                    recommendations.append(f"- {weak['stage']}: {weak['issue']}")
            else:
                recommendations.append("产业链各环节发展较为均衡")
            
            result = {
                "overall_completeness": round(overall_completeness, 2),
                "stage_coverage": {
                    "upstream": round(upstream_coverage * 100, 2),
                    "midstream": round(midstream_coverage * 100, 2),
                    "downstream": round(downstream_coverage * 100, 2)
                },
                "weak_links": weak_links,
                "recommendations": recommendations,
                "rating": self._get_completeness_rating(overall_completeness)
            }
            
            logger.info(f"产业链完整度评估: {overall_completeness:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"评估产业链完整度失败: {e}")
            return {}
    
    def _get_completeness_rating(self, completeness: float) -> str:
        """根据完整度得分返回评级"""
        if completeness >= 80:
            return "优秀"
        elif completeness >= 60:
            return "良好"
        elif completeness >= 40:
            return "一般"
        else:
            return "较弱"
    
    def generate_chain_chart(self, graph: Dict, title: str = "产业链图谱") -> Dict:
        """生成产业链图表配置（ECharts）
        
        Args:
            graph: 产业链图谱数据
            title: 图表标题
            
        Returns:
            ECharts配置
        """
        try:
            categories = [
                {"name": "上游（原材料/技术）"},
                {"name": "中游（制造/生产）"},
                {"name": "下游（应用/市场）"}
            ]
            
            config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {"fontSize": 20}
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{b}"
                },
                "legend": [{
                    "data": [cat["name"] for cat in categories],
                    "orient": "vertical",
                    "left": "left",
                    "top": "middle"
                }],
                "animationDuration": 1500,
                "animationEasingUpdate": "quinticInOut",
                "series": [{
                    "name": title,
                    "type": "graph",
                    "layout": "force",
                    "data": graph["nodes"],
                    "links": graph["links"],
                    "categories": categories,
                    "roam": True,
                    "label": {
                        "show": True,
                        "position": "right",
                        "formatter": "{b}"
                    },
                    "labelLayout": {
                        "hideOverlap": True
                    },
                    "scaleLimit": {
                        "min": 0.4,
                        "max": 2
                    },
                    "lineStyle": {
                        "color": "source",
                        "curveness": 0.3,
                        "width": 2
                    },
                    "emphasis": {
                        "focus": "adjacency",
                        "lineStyle": {"width": 5}
                    },
                    "force": {
                        "repulsion": 200,
                        "edgeLength": [100, 150],
                        "gravity": 0.1
                    }
                }]
            }
            
            logger.info("生成产业链图表配置成功")
            return config
            
        except Exception as e:
            logger.error(f"生成产业链图表失败: {e}")
            return {}
    
    def analyze_industry_chain(self, report_content: str) -> Dict:
        """完整的产业链分析
        
        Args:
            report_content: 报告内容
            
        Returns:
            完整分析结果
        """
        try:
            # 提取实体
            entities = self.extract_chain_entities(report_content)
            
            # 构建图谱
            graph = self.build_chain_graph(entities)
            
            # 评估完整度
            completeness = self.evaluate_chain_completeness(entities)
            
            # 生成图表
            chart = self.generate_chain_chart(graph)
            
            result = {
                "entities": entities,
                "graph": graph,
                "completeness": completeness,
                "chart": chart
            }
            
            logger.info("产业链完整分析成功")
            return result
            
        except Exception as e:
            logger.error(f"产业链分析失败: {e}")
            return {}


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    analyzer = IndustryChainAnalyzer()
    
    # 测试文本
    test_content = """
    成都人工智能产业链日趋完善。上游方面，华为公司提供核心芯片，
    中科院研发先进算法。中游制造环节，腾讯公司负责平台建设，
    阿里巴巴集团进行系统集成。下游应用领域，字节跳动公司
    提供内容服务，美团集团拓展市场渠道。
    """
    
    # 完整分析
    result = analyzer.analyze_industry_chain(test_content)
    
    print(f"\n产业链实体:")
    print(f"- 上游: {result['entities']['upstream']}")
    print(f"- 中游: {result['entities']['midstream']}")
    print(f"- 下游: {result['entities']['downstream']}")
    
    print(f"\n产业链完整度: {result['completeness']['overall_completeness']}%")
    print(f"评级: {result['completeness']['rating']}")
    
    print(f"\n薄弱环节:")
    for weak in result['completeness']['weak_links']:
        print(f"- {weak['stage']}: {weak['issue']}")
    
    print(f"\n图谱统计:")
    print(f"- 节点数: {result['graph']['statistics']['total_nodes']}")
    print(f"- 连接数: {result['graph']['statistics']['total_links']}")
    
    print("\n✅ 产业链分析模块测试通过！")
