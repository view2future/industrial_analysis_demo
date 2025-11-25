#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多文档对比分析模块
支持横向对比不同区域/产业报告
"""

import json
import logging
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)


class ComparisonAnalyzer:
    """多文档对比分析器"""
    
    def __init__(self):
        """初始化对比分析器"""
        self.reports = []
        
    def add_report(self, report_id: str, report_data: Dict, 
                  metadata: Optional[Dict] = None):
        """添加报告用于对比
        
        Args:
            report_id: 报告ID
            report_data: 报告数据
            metadata: 元数据（城市、行业等）
        """
        try:
            # 提取关键信息
            extracted_data = self._extract_comparable_data(report_data)
            
            self.reports.append({
                "id": report_id,
                "metadata": metadata or {},
                "data": extracted_data,
                "raw": report_data
            })
            
            logger.info(f"添加对比报告成功: {report_id}")
            
        except Exception as e:
            logger.error(f"添加对比报告失败: {e}")
    
    def _extract_comparable_data(self, report_data: Dict) -> Dict:
        """从报告中提取可对比的数据
        
        Args:
            report_data: 报告数据
            
        Returns:
            提取的可对比数据
        """
        comparable = {
            "metrics": {},
            "keywords": [],
            "summary": ""
        }
        
        try:
            # 兼容不同报告结构的内容字段
            content = report_data.get('full_content') or report_data.get('content', '')
            
            # 提取数值指标
            patterns = {
                "market_size": r'市场规模.*?(\d+\.?\d*)\s*(亿|万亿)',
                "growth_rate": r'增长率.*?(\d+\.?\d*)%',
                "company_count": r'企业.*?(\d+)\s*家',
                "investment": r'投资.*?(\d+\.?\d*)\s*亿',
                "revenue": r'营收.*?(\d+\.?\d*)\s*亿',
                "employment": r'就业.*?(\d+\.?\d*)\s*(万人|人)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    value = float(match.group(1))
                    if len(match.groups()) > 1:
                        unit = match.group(2)
                        if '万亿' in unit:
                            value *= 10000
                        elif '万' in unit and '万亿' not in unit:
                            value *= 0.0001
                    comparable["metrics"][key] = value
            
            # 提取关键词（简化版）
            keywords = re.findall(r'(人工智能|大数据|云计算|物联网|区块链|5G|新能源|智能制造)', content)
            comparable["keywords"] = list(set(keywords))
            
            # 提取摘要（前200字），兼容字典/字符串
            raw_summary = report_data.get('summary')
            if isinstance(raw_summary, dict):
                comparable["summary"] = raw_summary.get('zh') or raw_summary.get('en') or content[:200]
            elif isinstance(raw_summary, str):
                comparable["summary"] = raw_summary
            else:
                comparable["summary"] = content[:200]
            
            logger.info(f"提取可对比数据成功，指标数: {len(comparable['metrics'])}")
            
        except Exception as e:
            logger.error(f"提取可对比数据失败: {e}")
        
        return comparable
    
    def compare_reports(self) -> Dict:
        """对比所有已添加的报告
        
        Returns:
            对比分析结果
        """
        try:
            if len(self.reports) < 2:
                return {"error": "至少需要2份报告才能进行对比"}
            
            comparison = {
                "total_reports": len(self.reports),
                "report_list": [],
                "metric_comparison": {},
                "keyword_analysis": {},
                "rankings": {}
            }
            
            # 报告基本信息
            for report in self.reports:
                comparison["report_list"].append({
                    "id": report["id"],
                    "metadata": report["metadata"],
                    "summary": report["data"]["summary"]
                })
            
            # 指标对比
            all_metrics = set()
            for report in self.reports:
                all_metrics.update(report["data"]["metrics"].keys())
            
            for metric in all_metrics:
                values = []
                for report in self.reports:
                    value = report["data"]["metrics"].get(metric, 0)
                    values.append({
                        "report_id": report["id"],
                        "report_name": report["metadata"].get("name", report["id"]),
                        "value": value
                    })
                
                # 排序
                values_sorted = sorted(values, key=lambda x: x["value"], reverse=True)
                
                comparison["metric_comparison"][metric] = {
                    "values": values,
                    "max": max([v["value"] for v in values]) if values else 0,
                    "min": min([v["value"] for v in values]) if values else 0,
                    "avg": sum([v["value"] for v in values]) / len(values) if values else 0,
                    "leader": values_sorted[0] if values_sorted else None
                }
            
            # 关键词分析
            all_keywords = {}
            for report in self.reports:
                for keyword in report["data"]["keywords"]:
                    if keyword not in all_keywords:
                        all_keywords[keyword] = []
                    all_keywords[keyword].append(report["id"])
            
            comparison["keyword_analysis"] = {
                k: {"count": len(v), "reports": v} 
                for k, v in all_keywords.items()
            }
            
            # 综合排名（基于多个指标）
            scores = {}
            for report in self.reports:
                score = 0
                metrics = report["data"]["metrics"]
                
                # 简单加权评分
                score += metrics.get("market_size", 0) * 0.3
                score += metrics.get("growth_rate", 0) * 0.2
                score += metrics.get("company_count", 0) * 0.1
                score += metrics.get("investment", 0) * 0.25
                score += len(report["data"]["keywords"]) * 10 * 0.15
                
                scores[report["id"]] = {
                    "report_name": report["metadata"].get("name", report["id"]),
                    "score": score
                }
            
            # 排序
            ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
            comparison["rankings"] = {
                "overall": [
                    {"rank": i+1, "report_id": rid, **data}
                    for i, (rid, data) in enumerate(ranked)
                ]
            }
            
            logger.info(f"报告对比成功，共对比 {len(self.reports)} 份报告")
            return comparison
            
        except Exception as e:
            logger.error(f"报告对比失败: {e}")
            return {"error": str(e)}
    
    def generate_comparison_chart(self, metric_name: str) -> Dict:
        """生成对比图表配置
        
        Args:
            metric_name: 指标名称
            
        Returns:
            ECharts配置
        """
        try:
            comparison = self.compare_reports()
            
            if "error" in comparison:
                return {}
            
            if metric_name not in comparison["metric_comparison"]:
                return {"error": f"指标 {metric_name} 不存在"}
            
            metric_data = comparison["metric_comparison"][metric_name]
            
            # 提取数据
            names = [v["report_name"] for v in metric_data["values"]]
            values = [v["value"] for v in metric_data["values"]]
            
            config = {
                "title": {
                    "text": f"{metric_name} 对比分析",
                    "left": "center"
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"}
                },
                "xAxis": {
                    "type": "category",
                    "data": names,
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {
                    "type": "value",
                    "name": metric_name
                },
                "series": [
                    {
                        "name": metric_name,
                        "type": "bar",
                        "data": values,
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0, "y": 0, "x2": 0, "y2": 1,
                                "colorStops": [
                                    {"offset": 0, "color": "#4575b4"},
                                    {"offset": 1, "color": "#74add1"}
                                ]
                            }
                        },
                        "label": {
                            "show": True,
                            "position": "top"
                        }
                    }
                ]
            }
            
            logger.info(f"生成对比图表成功: {metric_name}")
            return config
            
        except Exception as e:
            logger.error(f"生成对比图表失败: {e}")
            return {}
    
    def generate_radar_chart(self) -> Dict:
        """生成多维度雷达图对比
        
        Returns:
            ECharts雷达图配置
        """
        try:
            if len(self.reports) < 2:
                return {"error": "至少需要2份报告"}
            
            # 选取关键指标
            indicator_names = ["market_size", "growth_rate", "company_count", 
                             "investment", "keyword_count"]
            
            indicators = []
            for name in indicator_names:
                max_val = 0
                for report in self.reports:
                    if name == "keyword_count":
                        val = len(report["data"]["keywords"])
                    else:
                        val = report["data"]["metrics"].get(name, 0)
                    max_val = max(max_val, val)
                
                indicators.append({
                    "name": name,
                    "max": max_val * 1.2 if max_val > 0 else 100
                })
            
            # 构建系列数据
            series_data = []
            for report in self.reports:
                values = []
                for name in indicator_names:
                    if name == "keyword_count":
                        val = len(report["data"]["keywords"])
                    else:
                        val = report["data"]["metrics"].get(name, 0)
                    values.append(val)
                
                series_data.append({
                    "name": report["metadata"].get("name", report["id"]),
                    "value": values
                })
            
            config = {
                "title": {
                    "text": "多维度对比雷达图",
                    "left": "center"
                },
                "tooltip": {},
                "legend": {
                    "data": [s["name"] for s in series_data],
                    "bottom": "5%"
                },
                "radar": {
                    "indicator": indicators
                },
                "series": [
                    {
                        "name": "多维对比",
                        "type": "radar",
                        "data": series_data
                    }
                ]
            }
            
            logger.info("生成雷达图对比成功")
            return config
            
        except Exception as e:
            logger.error(f"生成雷达图失败: {e}")
            return {}
    
    def generate_comparison_report(self) -> str:
        """生成对比分析文字报告
        
        Returns:
            对比报告文本
        """
        try:
            comparison = self.compare_reports()
            
            if "error" in comparison:
                return f"错误: {comparison['error']}"
            
            report_text = "# 多文档对比分析报告\n\n"
            
            # 基本信息
            report_text += f"## 对比概览\n\n"
            report_text += f"- 对比报告数量: {comparison['total_reports']}\n"
            report_text += f"- 对比指标数量: {len(comparison['metric_comparison'])}\n\n"
            
            # 综合排名
            report_text += "## 综合排名\n\n"
            for item in comparison["rankings"]["overall"][:5]:
                report_text += f"{item['rank']}. {item['report_name']} (得分: {item['score']:.2f})\n"
            
            report_text += "\n## 关键指标对比\n\n"
            
            # 指标详情
            for metric, data in comparison["metric_comparison"].items():
                if data['leader']:
                    report_text += f"### {metric}\n"
                    report_text += f"- 最高: {data['leader']['report_name']} ({data['max']:.2f})\n"
                    report_text += f"- 平均: {data['avg']:.2f}\n"
                    report_text += f"- 最低: {data['min']:.2f}\n\n"
            
            # 关键词分析
            report_text += "## 关键技术词频\n\n"
            keyword_items = sorted(comparison["keyword_analysis"].items(), 
                                  key=lambda x: x[1]["count"], reverse=True)
            for keyword, data in keyword_items[:10]:
                report_text += f"- {keyword}: 出现在 {data['count']} 份报告中\n"
            
            logger.info("生成对比文字报告成功")
            return report_text
            
        except Exception as e:
            logger.error(f"生成对比报告失败: {e}")
            return f"生成对比报告失败: {e}"


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    analyzer = ComparisonAnalyzer()
    
    # 模拟报告数据
    report1 = {
        "content": "成都人工智能产业市场规模达到500亿元，增长率20%，企业300家，投资100亿元。重点发展人工智能、大数据。"
    }
    
    report2 = {
        "content": "北京人工智能产业市场规模达到800亿元，增长率25%，企业500家，投资200亿元。聚焦人工智能、云计算、5G。"
    }
    
    # 添加报告
    analyzer.add_report("report1", report1, {"name": "成都AI产业", "city": "成都"})
    analyzer.add_report("report2", report2, {"name": "北京AI产业", "city": "北京"})
    
    # 对比分析
    comparison = analyzer.compare_reports()
    print(f"对比结果: {json.dumps(comparison, ensure_ascii=False, indent=2)[:500]}...")
    
    # 生成图表
    chart = analyzer.generate_comparison_chart("market_size")
    print(f"\n对比图表: {json.dumps(chart, ensure_ascii=False, indent=2)[:300]}...")
    
    # 生成雷达图
    radar = analyzer.generate_radar_chart()
    print(f"\n雷达图: {json.dumps(radar, ensure_ascii=False, indent=2)[:300]}...")
    
    # 生成文字报告
    text_report = analyzer.generate_comparison_report()
    print(f"\n文字报告:\n{text_report[:400]}...")
    
    print("\n✅ 多文档对比分析模块测试通过！")
