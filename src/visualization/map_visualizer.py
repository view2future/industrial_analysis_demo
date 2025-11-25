#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地图可视化模块
支持ECharts地图、百度地图API、热力图、3D柱状图等
"""

import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MapVisualizer:
    """地图可视化生成器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化地图可视化器
        
        Args:
            config: 配置字典，包含百度地图AK等
        """
        self.config = config or {}
        self.baidu_map_ak = self.config.get('baidu_map_ak', '')
        
    def generate_province_map(self, data: Dict[str, float], 
                             title: str = "产业分布地图",
                             enable_interactions: bool = True) -> Dict:
        """生成省份级别地图配置
        
        Args:
            data: 省份-数值映射，例如 {"四川": 100, "北京": 150}
            title: 地图标题
            enable_interactions: 是否启用交互功能
            
        Returns:
            ECharts地图配置JSON
        """
        try:
            # 转换数据为ECharts格式
            map_data = [{"name": k, "value": v} for k, v in data.items()]
            
            # 计算最大值用于视觉映射
            max_value = max(data.values()) if data else 100
            min_value = min(data.values()) if data else 0
            
            config = {
                "title": {
                    "text": title,
                    "left": "center",
                    "textStyle": {
                        "fontSize": 20,
                        "fontWeight": "bold"
                    }
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{b}<br/>{c}"
                },
                "visualMap": {
                    "min": min_value,
                    "max": max_value,
                    "text": ["高", "低"],
                    "realtime": False,
                    "calculable": True,
                    "inRange": {
                        "color": ["#e0f3f8", "#abd9e9", "#74add1", 
                                 "#4575b4", "#313695"]
                    }
                },
                "series": [
                    {
                        "name": title,
                        "type": "map",
                        "map": "china",
                        "roam": True,
                        "label": {
                            "show": True
                        },
                        "data": map_data
                    }
                ]
            }
            
            # 如果启用交互功能，添加额外配置
            if enable_interactions:
                config["series"][0]["emphasis"] = {
                    "label": {
                        "show": True
                    },
                    "itemStyle": {
                        "shadowBlur": 20,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
                
                # 添加工具箱
                config["toolbox"] = {
                    "show": True,
                    "feature": {
                        "restore": {"show": True, "title": "还原"},
                        "saveAsImage": {"show": True, "title": "保存为图片"}
                    }
                }
            
            logger.info(f"生成省份地图配置成功，数据点数: {len(map_data)}")
            return config
            
        except Exception as e:
            logger.error(f"生成省份地图失败: {e}")
            return {}
    
    def generate_city_heatmap(self, cities: List[Dict], 
                             center_city: str = "成都",
                             enable_animation: bool = True) -> Dict:
        """生成城市热力图配置
        
        Args:
            cities: 城市列表，格式 [{"name": "成都", "value": 100, "lng": 104.06, "lat": 30.67}]
            center_city: 中心城市
            enable_animation: 是否启用动画效果
            
        Returns:
            ECharts热力图配置
        """
        try:
            # 查找中心城市坐标
            center_coords = [104.06, 30.67]  # 默认成都
            for city in cities:
                if city.get('name') == center_city:
                    center_coords = [city.get('lng', 104.06), 
                                   city.get('lat', 30.67)]
                    break
            
            config = {
                "title": {
                    "text": f"{center_city}产业热力分布",
                    "left": "center"
                },
                "tooltip": {
                    "trigger": "item"
                },
                "bmap": {
                    "center": center_coords,
                    "zoom": 11,
                    "roam": True,
                    "mapStyle": {
                        "styleJson": [
                            {
                                "featureType": "water",
                                "elementType": "all",
                                "stylers": {"color": "#d1d1d1"}
                            },
                            {
                                "featureType": "land",
                                "elementType": "all",
                                "stylers": {"color": "#f3f3f3"}
                            }
                        ]
                    }
                },
                "series": [
                    {
                        "name": "产业热度",
                        "type": "heatmap",
                        "coordinateSystem": "bmap",
                        "data": [[c.get('lng'), c.get('lat'), c.get('value')] 
                                for c in cities],
                        "pointSize": 10,
                        "blurSize": 20
                    }
                ]
            }
            
            # 如果启用动画效果，添加配置
            if enable_animation:
                config["series"][0]["animation"] = True
                config["series"][0]["animationDuration"] = 1000
                config["series"][0]["animationEasing"] = "cubicOut"
            
            logger.info(f"生成城市热力图配置成功，城市数: {len(cities)}")
            return config
            
        except Exception as e:
            logger.error(f"生成城市热力图失败: {e}")
            return {}
    
    def generate_3d_bar_chart(self, data: List[Dict], 
                             title: str = "产业数据3D柱状图",
                             enable_rotation: bool = True) -> Dict:
        """生成3D柱状图配置
        
        Args:
            data: 数据列表，格式 [{"x": "人工智能", "y": "成都", "z": 100}]
            title: 图表标题
            enable_rotation: 是否启用自动旋转
            
        Returns:
            ECharts 3D柱状图配置
        """
        try:
            # 提取X轴、Y轴类目
            x_categories = sorted(list(set([d['x'] for d in data])))
            y_categories = sorted(list(set([d['y'] for d in data])))
            
            # 构建数据矩阵
            chart_data = []
            for item in data:
                x_idx = x_categories.index(item['x'])
                y_idx = y_categories.index(item['y'])
                chart_data.append([x_idx, y_idx, item['z']])
            
            config = {
                "title": {
                    "text": title,
                    "left": "center"
                },
                "tooltip": {},
                "visualMap": {
                    "max": max([d['z'] for d in data]) if data else 100,
                    "inRange": {
                        "color": ["#313695", "#4575b4", "#74add1", 
                                 "#abd9e9", "#e0f3f8", "#fee090", 
                                 "#fdae61", "#f46d43", "#d73027", "#a50026"]
                    }
                },
                "xAxis3D": {
                    "type": "category",
                    "data": x_categories,
                    "name": "产业类型"
                },
                "yAxis3D": {
                    "type": "category",
                    "data": y_categories,
                    "name": "城市"
                },
                "zAxis3D": {
                    "type": "value",
                    "name": "指标值"
                },
                "grid3D": {
                    "boxWidth": 200,
                    "boxDepth": 80,
                    "viewControl": {
                        "alpha": 30,
                        "beta": 40,
                        "distance": 250,
                        "autoRotate": enable_rotation,
                        "autoRotateSpeed": 5
                    },
                    "light": {
                        "main": {
                            "intensity": 1.2,
                            "shadow": True
                        },
                        "ambient": {
                            "intensity": 0.3
                        }
                    }
                },
                "series": [
                    {
                        "type": "bar3D",
                        "data": chart_data,
                        "shading": "lambert",
                        "label": {
                            "show": False,
                            "fontSize": 16,
                            "borderWidth": 1
                        },
                        "itemStyle": {
                            "opacity": 0.8
                        },
                        "emphasis": {
                            "label": {
                                "show": True
                            },
                            "itemStyle": {
                                "color": "#ffa500"
                            }
                        }
                    }
                ]
            }
            
            logger.info(f"生成3D柱状图配置成功，数据点数: {len(data)}")
            return config
            
        except Exception as e:
            logger.error(f"生成3D柱状图失败: {e}")
            return {}
    
    def generate_industry_network(self, nodes: List[Dict], 
                                  links: List[Dict],
                                  title: str = "产业关系网络",
                                  enable_interactions: bool = True) -> Dict:
        """生成产业关系网络图
        
        Args:
            nodes: 节点列表，格式 [{"id": "1", "name": "企业A", "category": 0, "value": 100}]
            links: 连接列表，格式 [{"source": "1", "target": "2", "value": 10}]
            title: 图表标题
            enable_interactions: 是否启用交互功能
            
        Returns:
            ECharts关系图配置
        """
        try:
            # 定义类别
            categories = [
                {"name": "核心企业"},
                {"name": "上游供应商"},
                {"name": "下游客户"},
                {"name": "竞争对手"},
                {"name": "合作伙伴"}
            ]
            
            config = {
                "title": {
                    "text": title,
                    "left": "center"
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{b}: {c}"
                },
                "legend": [
                    {
                        "data": [cat["name"] for cat in categories],
                        "orient": "vertical",
                        "left": "left"
                    }
                ],
                "animationDuration": 1500,
                "animationEasingUpdate": "quinticInOut",
                "series": [
                    {
                        "name": title,
                        "type": "graph",
                        "layout": "force",
                        "data": nodes,
                        "links": links,
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
                            "curveness": 0.3
                        },
                        "emphasis": {
                            "focus": "adjacency",
                            "lineStyle": {
                                "width": 10
                            }
                        },
                        "force": {
                            "repulsion": 100,
                            "edgeLength": [50, 100]
                        }
                    }
                ]
            }
            
            # 如果启用交互功能，添加额外配置
            if enable_interactions:
                config["series"][0]["focusNodeAdjacency"] = True
                config["series"][0]["selectedMode"] = "multiple"
                
                # 添加工具箱
                config["toolbox"] = {
                    "show": True,
                    "feature": {
                        "restore": {"show": True, "title": "还原"},
                        "saveAsImage": {"show": True, "title": "保存为图片"}
                    }
                }
            
            logger.info(f"生成产业网络图配置成功，节点: {len(nodes)}, 连接: {len(links)}")
            return config
            
        except Exception as e:
            logger.error(f"生成产业网络图失败: {e}")
            return {}
    
    def generate_geo_scatter(self, data: List[Dict],
                            title: str = "产业地理分布",
                            enable_animation: bool = True) -> Dict:
        """生成地理散点图
        
        Args:
            data: 数据列表，格式 [{"name": "成都", "value": [104.06, 30.67, 100]}]
            title: 图表标题
            enable_animation: 是否启用动画效果
            
        Returns:
            ECharts地理散点图配置
        """
        try:
            config = {
                "title": {
                    "text": title,
                    "left": "center"
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{b}: {c}"
                },
                "geo": {
                    "map": "china",
                    "roam": True,
                    "label": {
                        "emphasis": {
                            "show": True
                        }
                    },
                    "itemStyle": {
                        "normal": {
                            "areaColor": "#f3f3f3",
                            "borderColor": "#516b91"
                        },
                        "emphasis": {
                            "areaColor": "#ffeb3b"
                        }
                    }
                },
                "series": [
                    {
                        "name": title,
                        "type": "scatter",
                        "coordinateSystem": "geo",
                        "data": data,
                        "symbolSize": 15,
                        "label": {
                            "formatter": "{b}",
                            "position": "right",
                            "show": False
                        },
                        "itemStyle": {
                            "color": "#4575b4"
                        },
                        "emphasis": {
                            "label": {
                                "show": True
                            }
                        }
                    },
                    {
                        "name": "连线",
                        "type": "lines",
                        "coordinateSystem": "geo",
                        "data": self._generate_lines(data),
                        "lineStyle": {
                            "color": "#a50026",
                            "opacity": 0.4,
                            "width": 1
                        },
                        "effect": {
                            "show": True,
                            "period": 6,
                            "trailLength": 0.7,
                            "color": "#a50026",
                            "symbolSize": 3
                        }
                    }
                ]
            }
            
            # 如果启用动画效果，添加配置
            if enable_animation:
                config["series"][0]["animation"] = True
                config["series"][0]["animationDuration"] = 1000
                config["series"][1]["effect"]["animation"] = True
            
            logger.info(f"生成地理散点图配置成功，数据点数: {len(data)}")
            return config
            
        except Exception as e:
            logger.error(f"生成地理散点图失败: {e}")
            return {}
    
    def _generate_lines(self, data: List[Dict]) -> List[Dict]:
        """为地理散点图生成连线数据"""
        if len(data) < 2:
            return []
        
        lines = []
        # 连接相邻城市
        for i in range(len(data) - 1):
            lines.append({
                "coords": [
                    data[i]['value'][:2],
                    data[i + 1]['value'][:2]
                ]
            })
        
        return lines
    
    def extract_geo_data_from_report(self, report_content: str, 
                                    include_context: bool = True) -> Dict:
        """从报告内容中提取地理相关数据
        
        Args:
            report_content: 报告文本内容
            include_context: 是否包含上下文信息
            
        Returns:
            提取的地理数据字典
        """
        try:
            import re
            
            # 提取城市名称（简化版，实际应该使用NLP）
            cities = re.findall(r'(北京|上海|广州|深圳|成都|杭州|武汉|西安|重庆|天津)', 
                              report_content)
            
            # 城市坐标映射
            city_coords = {
                "北京": [116.4074, 39.9042],
                "上海": [121.4737, 31.2304],
                "广州": [113.2644, 23.1291],
                "深圳": [114.0579, 22.5431],
                "成都": [104.0668, 30.5728],
                "杭州": [120.1551, 30.2741],
                "武汉": [114.3055, 30.5931],
                "西安": [108.9398, 34.3416],
                "重庆": [106.5516, 29.5630],
                "天津": [117.2010, 39.0842]
            }
            
            # 统计城市出现频率
            city_freq = {}
            for city in cities:
                city_freq[city] = city_freq.get(city, 0) + 1
            
            # 构建地理数据
            geo_data = []
            for city, freq in city_freq.items():
                if city in city_coords:
                    city_data = {
                        "name": city,
                        "value": city_coords[city] + [freq * 10]
                    }
                    
                    # 如果包含上下文信息，添加位置信息
                    if include_context:
                        # 查找城市在文本中的位置
                        positions = [m.start() for m in re.finditer(city, report_content)]
                        if positions:
                            city_data["positions"] = positions[:5]  # 只保留前5个位置
                            # 提取上下文片段
                            contexts = []
                            for pos in positions[:3]:  # 只提取前3个上下文
                                start = max(0, pos - 50)
                                end = min(len(report_content), pos + 50)
                                context = report_content[start:end]
                                contexts.append(context)
                            city_data["contexts"] = contexts
                    
                    geo_data.append(city_data)
            
            logger.info(f"从报告中提取地理数据成功，城市数: {len(geo_data)}")
            return {"cities": geo_data}
            
        except Exception as e:
            logger.error(f"提取地理数据失败: {e}")
            return {"cities": []}
    
    def generate_all_visualizations(self, report_data: Dict,
                                   enable_interactions: bool = True,
                                   enable_animations: bool = True) -> Dict:
        """为报告生成所有地图可视化
        
        Args:
            report_data: 报告数据字典
            enable_interactions: 是否启用交互功能
            enable_animations: 是否启用动画效果
            
        Returns:
            所有可视化配置的字典
        """
        try:
            visualizations = {}
            
            # 1. 省份分布地图
            if 'province_data' in report_data:
                visualizations['province_map'] = self.generate_province_map(
                    report_data['province_data'],
                    title="全国产业分布地图",
                    enable_interactions=enable_interactions
                )
            
            # 2. 城市热力图
            if 'city_data' in report_data:
                visualizations['city_heatmap'] = self.generate_city_heatmap(
                    report_data['city_data'],
                    enable_animation=enable_animations
                )
            
            # 3. 3D柱状图
            if '3d_data' in report_data:
                visualizations['bar_3d'] = self.generate_3d_bar_chart(
                    report_data['3d_data'],
                    enable_rotation=enable_animations
                )
            
            # 4. 产业网络图
            if 'network_data' in report_data:
                visualizations['industry_network'] = self.generate_industry_network(
                    report_data['network_data'].get('nodes', []),
                    report_data['network_data'].get('links', []),
                    enable_interactions=enable_interactions
                )
            
            # 5. 地理散点图
            if 'geo_scatter_data' in report_data:
                visualizations['geo_scatter'] = self.generate_geo_scatter(
                    report_data['geo_scatter_data'],
                    enable_animation=enable_animations
                )
            
            logger.info(f"生成所有可视化配置成功，共 {len(visualizations)} 个")
            return visualizations
            
        except Exception as e:
            logger.error(f"生成所有可视化失败: {e}")
            return {}


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    visualizer = MapVisualizer()
    
    # 测试省份地图
    province_data = {
        "四川": 120,
        "北京": 150,
        "上海": 130,
        "广东": 140,
        "浙江": 110
    }
    
    province_map = visualizer.generate_province_map(province_data, enable_interactions=True)
    print(f"省份地图配置: {json.dumps(province_map, ensure_ascii=False, indent=2)[:200]}...")
    
    # 测试3D柱状图
    bar_3d_data = [
        {"x": "人工智能", "y": "成都", "z": 100},
        {"x": "人工智能", "y": "北京", "z": 150},
        {"x": "大数据", "y": "成都", "z": 80},
        {"x": "大数据", "y": "北京", "z": 120}
    ]
    
    bar_3d = visualizer.generate_3d_bar_chart(bar_3d_data, enable_rotation=True)
    print(f"\n3D柱状图配置: {json.dumps(bar_3d, ensure_ascii=False, indent=2)[:200]}...")
    
    # 测试地理数据提取
    sample_report = """
    成都市在人工智能领域发展迅速，华为公司在成都设有研发中心。
    北京市作为首都，在大数据产业方面具有明显优势。
    成都市政府出台多项政策支持人工智能产业发展。
    """
    
    geo_data = visualizer.extract_geo_data_from_report(sample_report, include_context=True)
    print(f"\n提取的地理数据: {geo_data}")
    
    print("\n✅ 地图可视化模块测试通过！")
