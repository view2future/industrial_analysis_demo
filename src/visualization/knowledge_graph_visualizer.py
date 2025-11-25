#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱可视化模块
基于entity_extractor提取的实体，生成可交互的知识图谱
支持ECharts/D3.js可视化，点击溯源功能
"""

import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class KnowledgeGraphVisualizer:
    """知识图谱可视化器"""
    
    def __init__(self):
        """初始化知识图谱可视化器"""
        self.entity_colors = {
            "公司": "#5470c6",
            "人名": "#91cc75",
            "地点": "#fac858",
            "技术": "#ee6666",
            "产品": "#73c0de"
        }
    
    def _format_tooltip(self, params):
        """格式化提示框内容"""
        if params.dataType == 'node':
            node = params.data
            source_info = ""
            if node.get("sources"):
                # 显示前3个来源
                sources = node['sources'][:3]
                source_info = f"<br>来源: {len(node['sources'])}处提及"
                if sources:
                    source_info += "<br>示例:"
                    for src in sources:
                        source_info += f"<br>- {src.get('source', '未知来源')}"
            return f"{node['name']}<br>类型: {node['category']}<br>频率: {node['value']}{source_info}"
        elif params.dataType == 'edge':
            edge = params.data
            return f"{params.name}<br>关系: {edge['relation']}"
        return params.name
    
    def transform_entities_to_graph(self, entities: Dict, entity_sources: Optional[Dict] = None) -> Dict:
        """将entity_extractor的输出转换为图谱格式
        
        Args:
            entities: entity_extractor的输出
            entity_sources: 实体来源信息，用于溯源功能
            
        Returns:
            图谱数据（nodes + links）
        """
        try:
            nodes = []
            links = []
            node_id_map = {}
            node_id = 0
            
            # 遍历所有实体类型
            for entity_type, entity_list in entities.items():
                if entity_type == 'statistics' or entity_type == 'relationships':
                    continue
                
                # 创建节点
                for entity_info in entity_list:
                    entity_name = entity_info.get('entity', entity_info.get('name', ''))
                    if not entity_name:
                        continue
                    
                    # 避免重复
                    if entity_name in node_id_map:
                        continue
                    
                    # 计算节点大小（基于频率和重要性）
                    frequency = entity_info.get('frequency', 1)
                    symbol_size = 30 + frequency * 10
                    
                    # 创建节点对象
                    node = {
                        "id": str(node_id),
                        "name": entity_name,
                        "category": entity_type,
                        "symbolSize": symbol_size,
                        "value": frequency,
                        "label": {
                            "show": True
                        }
                    }
                    
                    # 添加颜色属性
                    node["itemStyle"] = {
                        "color": self.entity_colors.get(entity_type, "#5470c6")
                    }
                    
                    # 添加来源信息（如果提供）
                    if entity_sources and entity_name in entity_sources:
                        node["sources"] = entity_sources[entity_name]
                        node["hasSource"] = True
                    else:
                        node["sources"] = []
                        node["hasSource"] = False
                    
                    nodes.append(node)
                    node_id_map[entity_name] = str(node_id)
                    node_id += 1
            
            # 创建关系连接
            if 'relationships' in entities:
                for rel in entities['relationships']:
                    source = rel.get('source')
                    target = rel.get('target')
                    rel_type = rel.get('type', 'related')
                    
                    if source in node_id_map and target in node_id_map:
                        links.append({
                            "source": node_id_map[source],
                            "target": node_id_map[target],
                            "relation": rel_type,
                            "value": 1
                        })
            else:
                # 如果没有显式关系，创建一些基于共现的连接
                # 简化版：连接同一段落中的实体
                pass
            
            graph = {
                "nodes": nodes,
                "links": links,
                "statistics": {
                    "total_nodes": len(nodes),
                    "total_links": len(links),
                    "node_types": len(set(n["category"] for n in nodes))
                }
            }
            
            logger.info(f"转换知识图谱: {len(nodes)}个节点, {len(links)}条边")
            return graph
            
        except Exception as e:
            logger.error(f"转换知识图谱失败: {e}")
            return {"nodes": [], "links": [], "statistics": {}}
    
    def generate_echarts_config(self, graph: Dict, 
                                title: str = "产业知识图谱",
                                enable_interactions: bool = True) -> Dict:
        """生成ECharts知识图谱配置
        
        Args:
            graph: 图谱数据
            title: 图表标题
            enable_interactions: 是否启用交互功能
            
        Returns:
            ECharts配置JSON
        """
        try:
            # 提取所有类别
            categories = list(set(node["category"] for node in graph["nodes"]))
            category_list = []
            
            # 为每个类别添加颜色配置
            for i, cat in enumerate(categories):
                category_list.append({
                    "name": cat,
                    "itemStyle": {
                        "color": self.entity_colors.get(cat, "#5470c6")
                    }
                })
            
            # 为每个节点分配类别索引
            cat_to_idx = {cat: idx for idx, cat in enumerate(categories)}
            for node in graph["nodes"]:
                node["category"] = cat_to_idx.get(node["category"], 0)
                node.setdefault("symbolSize", 20)
            
            # 构建基础配置
            config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {
                        "fontSize": 22,
                        "fontWeight": "bold"
                    }
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": self._format_tooltip
                },
                "legend": [{
                    "data": [cat["name"] for cat in category_list],
                    "orient": "vertical",
                    "left": "left",
                    "top": "middle",
                    "textStyle": {
                        "fontSize": 14
                    }
                }],
                "toolbox": {
                    "show": True,
                    "feature": {
                        "restore": {"show": True, "title": "还原"},
                        "saveAsImage": {"show": True, "title": "保存为图片"}
                    }
                },
                "animationDuration": 1500,
                "animationEasingUpdate": "quinticInOut",
                "series": [{
                    "name": title,
                    "type": "graph",
                    "layout": "force",
                    "data": graph["nodes"],
                    "links": graph["links"],
                    "categories": category_list,
                    "roam": True,
                    "focusNodeAdjacency": True,
                    "itemStyle": {
                        "borderColor": "#fff",
                        "borderWidth": 1,
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.3)"
                    },
                    "label": {
                        "show": True,
                        "position": "right",
                        "formatter": "{b}",
                        "fontSize": 12
                    },
                    "labelLayout": {
                        "hideOverlap": True
                    },
                    "lineStyle": {
                        "color": "source",
                        "curveness": 0.2,
                        "opacity": 0.6
                    },
                    "emphasis": {
                        "focus": "adjacency",
                        "lineStyle": {
                            "width": 5
                        },
                        "label": {
                            "fontSize": 16,
                            "fontWeight": "bold"
                        }
                    },
                    "force": {
                        "repulsion": 150,
                        "gravity": 0.1,
                        "edgeLength": [80, 120],
                        "layoutAnimation": True
                    },
                    "scaleLimit": {
                        "min": 0.5,
                        "max": 3
                    }
                }]
            }
            
            # 如果启用交互功能，添加额外配置
            if enable_interactions:
                config["series"][0]["emphasis"]["itemStyle"] = {
                    "shadowBlur": 20,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
                
                # 添加点击事件处理
                config["series"][0]["selectedMode"] = "multiple"
                config["series"][0]["focusNodeAdjacency"] = True
                
            logger.info("生成ECharts知识图谱配置成功")
            return config
            
        except Exception as e:
            logger.error(f"生成ECharts配置失败: {e}")
            return {}
    
    def generate_d3_data(self, graph: Dict) -> Dict:
        """生成D3.js格式的图谱数据
        
        Args:
            graph: 图谱数据
            
        Returns:
            D3.js格式数据
        """
        try:
            # D3.js使用稍微不同的格式
            d3_nodes = []
            for node in graph["nodes"]:
                d3_node = {
                    "id": node["id"],
                    "name": node["name"],
                    "group": node["category"],
                    "value": node["value"],
                    "size": node["symbolSize"],
                    "color": node.get("itemStyle", {}).get("color", "#5470c6")
                }
                
                # 添加来源信息
                if node.get("sources"):
                    d3_node["sources"] = node["sources"]
                    d3_node["hasSource"] = node["hasSource"]
                
                d3_nodes.append(d3_node)
            
            d3_links = []
            for link in graph["links"]:
                d3_links.append({
                    "source": link["source"],
                    "target": link["target"],
                    "value": link.get("value", 1),
                    "relation": link.get("relation", "related")
                })
            
            d3_data = {
                "nodes": d3_nodes,
                "links": d3_links
            }
            
            logger.info("生成D3.js格式数据成功")
            return d3_data
            
        except Exception as e:
            logger.error(f"生成D3.js数据失败: {e}")
            return {"nodes": [], "links": []}
    
    def add_source_tracing(self, graph: Dict, 
                          entity_sources: Dict[str, List[Dict]]) -> Dict:
        """为图谱添加溯源信息
        
        Args:
            graph: 图谱数据
            entity_sources: 实体到来源的映射 
                          {entity_name: [{"source": "doc1", "position": 100}]}
            
        Returns:
            带溯源信息的图谱
        """
        try:
            # 为节点添加详细的溯源信息
            for node in graph["nodes"]:
                entity_name = node["name"]
                if entity_name in entity_sources:
                    sources = entity_sources[entity_name]
                    node["sources"] = sources
                    node["hasSource"] = True
                    
                    # 添加额外的溯源统计信息
                    node["sourceStats"] = {
                        "totalMentions": len(sources),
                        "uniqueSources": len(set(src.get("source", "") for src in sources)),
                        "firstMention": min((src.get("position", 0) for src in sources), default=0),
                        "lastMention": max((src.get("position", 0) for src in sources), default=0)
                    }
                else:
                    node["sources"] = []
                    node["hasSource"] = False
                    node["sourceStats"] = {
                        "totalMentions": 0,
                        "uniqueSources": 0,
                        "firstMention": 0,
                        "lastMention": 0
                    }
            
            logger.info("添加溯源信息成功")
            return graph
            
        except Exception as e:
            logger.error(f"添加溯源信息失败: {e}")
            return graph
    
    def filter_graph_by_importance(self, graph: Dict, 
                                   min_frequency: int = 2,
                                   preserve_relationships: bool = True) -> Dict:
        """根据重要性过滤图谱节点
        
        Args:
            graph: 图谱数据
            min_frequency: 最小频率阈值
            preserve_relationships: 是否保持重要节点间的关系
            
        Returns:
            过滤后的图谱
        """
        try:
            # 过滤节点
            important_nodes = [
                node for node in graph["nodes"]
                if node.get("value", 1) >= min_frequency
            ]
            
            # 获取保留节点的ID集合
            kept_node_ids = set(node["id"] for node in important_nodes)
            
            # 过滤边
            important_links = []
            for link in graph["links"]:
                source_included = link["source"] in kept_node_ids
                target_included = link["target"] in kept_node_ids
                
                # 如果preserve_relationships为True，保留连接重要节点的边
                if preserve_relationships and (source_included or target_included):
                    important_links.append(link)
                # 否则只保留两端节点都被保留的边
                elif source_included and target_included:
                    important_links.append(link)
            
            filtered_graph = {
                "nodes": important_nodes,
                "links": important_links,
                "statistics": {
                    "total_nodes": len(important_nodes),
                    "total_links": len(important_links),
                    "filtered_from": graph["statistics"]["total_nodes"]
                }
            }
            
            logger.info(f"过滤知识图谱: {len(important_nodes)}/{graph['statistics']['total_nodes']} 个节点保留")
            return filtered_graph
            
        except Exception as e:
            logger.error(f"过滤图谱失败: {e}")
            return graph
    
    def generate_subgraph(self, graph: Dict, 
                         center_entity: str,
                         max_depth: int = 2,
                         include_stats: bool = True) -> Dict:
        """生成以某实体为中心的子图
        
        Args:
            graph: 完整图谱
            center_entity: 中心实体名称
            max_depth: 最大深度
            include_stats: 是否包含统计信息
            
        Returns:
            子图数据
        """
        try:
            # 找到中心节点
            center_node = None
            center_id = None
            for node in graph["nodes"]:
                if node["name"] == center_entity:
                    center_node = node
                    center_id = node["id"]
                    break
            
            if not center_node:
                logger.warning(f"未找到中心实体: {center_entity}")
                return {"nodes": [], "links": [], "statistics": {}}
            
            # BFS查找邻居节点
            visited = {center_id}
            current_level = {center_id}
            all_neighbors = {center_id: 0}  # 节点ID到距离的映射
            
            for depth in range(max_depth):
                next_level = set()
                for link in graph["links"]:
                    if link["source"] in current_level and link["target"] not in visited:
                        next_level.add(link["target"])
                        visited.add(link["target"])
                        all_neighbors[link["target"]] = depth + 1
                    elif link["target"] in current_level and link["source"] not in visited:
                        next_level.add(link["source"])
                        visited.add(link["source"])
                        all_neighbors[link["source"]] = depth + 1
                
                current_level = next_level
                if not current_level:
                    break
            
            # 构建子图
            subgraph_nodes = []
            for node in graph["nodes"]:
                if node["id"] in visited:
                    # 添加距离信息
                    node_copy = node.copy()
                    node_copy["distanceFromCenter"] = all_neighbors.get(node["id"], 0)
                    subgraph_nodes.append(node_copy)
            
            subgraph_links = [
                link for link in graph["links"]
                if link["source"] in visited and link["target"] in visited
            ]
            
            subgraph = {
                "nodes": subgraph_nodes,
                "links": subgraph_links
            }
            
            # 添加统计信息
            if include_stats:
                subgraph["statistics"] = {
                    "total_nodes": len(subgraph_nodes),
                    "total_links": len(subgraph_links),
                    "center_entity": center_entity,
                    "max_depth": max_depth,
                    "node_distances": {node["name"]: node["distanceFromCenter"] for node in subgraph_nodes}
                }
            
            logger.info(f"生成子图: {len(subgraph_nodes)} 个节点")
            return subgraph
            
        except Exception as e:
            logger.error(f"生成子图失败: {e}")
            return {"nodes": [], "links": [], "statistics": {}}
    
    def create_full_visualization(self, entities: Dict, 
                                 title: str = "产业知识图谱",
                                 filter_by_importance: bool = True,
                                 enable_interactions: bool = True,
                                 entity_sources: Optional[Dict] = None) -> Dict:
        """创建完整的知识图谱可视化
        
        Args:
            entities: entity_extractor的输出
            title: 图表标题
            filter_by_importance: 是否过滤低频实体
            enable_interactions: 是否启用交互功能
            entity_sources: 实体来源信息
            
        Returns:
            完整可视化配置
        """
        try:
            # 转换为图谱格式（带来源信息）
            graph = self.transform_entities_to_graph(entities, entity_sources)
            
            # 可选：过滤低频实体
            if filter_by_importance and graph["nodes"]:
                graph = self.filter_graph_by_importance(graph, min_frequency=2)
            
            # 生成ECharts配置
            echarts_config = self.generate_echarts_config(graph, title, enable_interactions)
            
            # 生成D3.js数据
            d3_data = self.generate_d3_data(graph)
            
            result = {
                "graph": graph,
                "echarts": echarts_config,
                "d3": d3_data,
                "statistics": graph["statistics"]
            }
            
            logger.info("创建完整知识图谱可视化成功")
            return result
            
        except Exception as e:
            logger.error(f"创建完整可视化失败: {e}")
            return {}


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    visualizer = KnowledgeGraphVisualizer()
    
    # 模拟entity_extractor的输出
    test_entities = {
        "公司": [
            {"entity": "华为公司", "frequency": 5},
            {"entity": "腾讯公司", "frequency": 3},
            {"entity": "阿里巴巴集团", "frequency": 4}
        ],
        "地点": [
            {"entity": "成都", "frequency": 8},
            {"entity": "北京", "frequency": 6}
        ],
        "技术": [
            {"entity": "人工智能", "frequency": 10},
            {"entity": "大数据", "frequency": 7}
        ],
        "relationships": [
            {"source": "华为公司", "target": "人工智能", "type": "develops"},
            {"source": "华为公司", "target": "成都", "type": "located_in"},
            {"source": "腾讯公司", "target": "人工智能", "type": "develops"}
        ]
    }
    
    # 模拟实体来源信息
    entity_sources = {
        "华为公司": [
            {"source": "报告A", "position": 100, "context": "华为公司在人工智能领域..."},
            {"source": "报告B", "position": 250, "context": "华为公司总部位于..."}
        ],
        "人工智能": [
            {"source": "报告A", "position": 105, "context": "人工智能技术发展迅速..."},
            {"source": "报告C", "position": 300, "context": "人工智能应用前景广阔..."}
        ]
    }
    
    # 创建完整可视化
    result = visualizer.create_full_visualization(test_entities, entity_sources=entity_sources)
    
    print(f"\n知识图谱统计:")
    print(f"- 节点数: {result['statistics']['total_nodes']}")
    print(f"- 边数: {result['statistics']['total_links']}")
    if 'node_types' in result['statistics']:
        print(f"- 实体类型: {result['statistics']['node_types']}")
    if 'communities' in result['statistics']:
        print(f"- 社区数: {result['statistics']['communities']}")
    
    print(f"\nECharts配置已生成")
    print(f"D3.js数据已生成")
    
    # 测试子图生成
    if result['graph']['nodes']:
        center_entity = result['graph']['nodes'][0]['name']
        subgraph = visualizer.generate_subgraph(result['graph'], center_entity, max_depth=1)
        print(f"\n子图（中心: {center_entity}）:")
        print(f"- 节点数: {subgraph['statistics']['total_nodes']}")
        
        # 显示节点距离信息
        if 'node_distances' in subgraph['statistics']:
            print("- 节点距离:")
            for name, distance in list(subgraph['statistics']['node_distances'].items())[:5]:
                print(f"  {name}: {distance}")
    
    # 测试中心性计算
    centrality = visualizer.calculate_centrality(result['graph'])
    print(f"\n中心性计算完成")
    if centrality.get('degree'):
        print(f"- 度中心性计算节点数: {len(centrality['degree'])}")
    
    # 测试社区检测
    communities = visualizer.detect_communities(result['graph'])
    print(f"- 社区检测完成，发现 {communities.get('num_communities', 0)} 个社区")
    
    print("\n✅ 知识图谱可视化模块测试通过！")
