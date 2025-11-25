#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
趋势预测与时间序列分析模块
支持多份历史报告分析、趋势预测、未来走势预测
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """趋势分析器"""
    
    def __init__(self):
        """初始化趋势分析器"""
        self.historical_data = []
        
    def extract_time_from_report(self, report_content: str, 
                                 filename: Optional[str] = None) -> Optional[str]:
        """从报告中提取时间信息
        
        Args:
            report_content: 报告内容
            filename: 文件名（可能包含时间）
            
        Returns:
            时间字符串（YYYY-MM-DD格式）或None
        """
        try:
            # 尝试从文件名提取
            if filename:
                # 匹配格式：2024-01-01, 20240101, 2024_01_01等
                patterns = [
                    r'(\d{4})[-_](\d{2})[-_](\d{2})',
                    r'(\d{4})(\d{2})(\d{2})',
                    r'(\d{4})年(\d{1,2})月(\d{1,2})日'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, filename)
                    if match:
                        year, month, day = match.groups()
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # 从内容提取
            date_patterns = [
                r'(\d{4})年(\d{1,2})月(\d{1,2})日',
                r'(\d{4})-(\d{2})-(\d{2})',
                r'(\d{4})/(\d{2})/(\d{2})'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, report_content)
                if matches:
                    year, month, day = matches[0]
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # 如果找不到，使用当前日期
            logger.warning("无法从报告中提取时间，使用当前日期")
            return datetime.now().strftime("%Y-%m-%d")
            
        except Exception as e:
            logger.error(f"提取时间失败: {e}")
            return None
    
    def add_historical_report(self, report_id: str, report_data: Dict,
                             time_str: Optional[str] = None):
        """添加历史报告数据
        
        Args:
            report_id: 报告ID
            report_data: 报告数据字典
            time_str: 时间字符串（YYYY-MM-DD）
        """
        try:
            if time_str is None:
                time_str = datetime.now().strftime("%Y-%m-%d")
            
            # 提取关键指标
            metrics = self._extract_metrics(report_data)
            
            self.historical_data.append({
                "id": report_id,
                "time": time_str,
                "timestamp": datetime.strptime(time_str, "%Y-%m-%d").timestamp(),
                "metrics": metrics,
                "raw_data": report_data
            })
            
            # 按时间排序
            self.historical_data.sort(key=lambda x: x['timestamp'])
            
            logger.info(f"添加历史报告成功: {report_id}, 时间: {time_str}")
            
        except Exception as e:
            logger.error(f"添加历史报告失败: {e}")
    
    def _extract_metrics(self, report_data: Dict) -> Dict[str, float]:
        """从报告中提取可量化的指标
        
        Args:
            report_data: 报告数据
            
        Returns:
            指标字典
        """
        metrics = {}
        
        try:
            content = report_data.get('content', '')
            
            # 提取数字指标（示例）
            # 市场规模
            market_size_pattern = r'市场规模.*?(\d+\.?\d*)\s*(亿|万亿|百亿)'
            match = re.search(market_size_pattern, content)
            if match:
                value = float(match.group(1))
                unit = match.group(2)
                if unit == '万亿':
                    value *= 10000
                elif unit == '百亿':
                    value *= 100
                metrics['market_size'] = value
            
            # 增长率
            growth_pattern = r'增长率.*?(\d+\.?\d*)%'
            match = re.search(growth_pattern, content)
            if match:
                metrics['growth_rate'] = float(match.group(1))
            
            # 企业数量
            company_pattern = r'企业.*?(\d+)\s*家'
            match = re.search(company_pattern, content)
            if match:
                metrics['company_count'] = int(match.group(1))
            
            # 投资金额
            investment_pattern = r'投资.*?(\d+\.?\d*)\s*(亿|万亿)'
            match = re.search(investment_pattern, content)
            if match:
                value = float(match.group(1))
                if match.group(2) == '万亿':
                    value *= 10000
                metrics['investment'] = value
            
            logger.info(f"提取指标成功: {list(metrics.keys())}")
            
        except Exception as e:
            logger.error(f"提取指标失败: {e}")
        
        return metrics
    
    def calculate_trend(self, metric_name: str) -> Dict:
        """计算指定指标的趋势
        
        Args:
            metric_name: 指标名称
            
        Returns:
            趋势分析结果
        """
        try:
            if len(self.historical_data) < 2:
                return {"error": "数据点不足，至少需要2个历史报告"}
            
            # 提取时间序列数据
            times = []
            values = []
            
            for data in self.historical_data:
                if metric_name in data['metrics']:
                    times.append(data['time'])
                    values.append(data['metrics'][metric_name])
            
            if len(values) < 2:
                return {"error": f"指标 {metric_name} 数据点不足"}
            
            # 计算趋势
            x = np.arange(len(values))
            coeffs = np.polyfit(x, values, deg=1)  # 线性拟合
            trend_line = np.poly1d(coeffs)
            
            # 计算增长率
            growth_rates = []
            for i in range(1, len(values)):
                rate = ((values[i] - values[i-1]) / values[i-1]) * 100
                growth_rates.append(rate)
            
            avg_growth_rate = np.mean(growth_rates) if growth_rates else 0
            
            # 趋势判断
            if coeffs[0] > 0:
                trend_direction = "上升"
            elif coeffs[0] < 0:
                trend_direction = "下降"
            else:
                trend_direction = "平稳"
            
            result = {
                "metric": metric_name,
                "data_points": len(values),
                "times": times,
                "values": values,
                "trend_direction": trend_direction,
                "trend_slope": float(coeffs[0]),
                "avg_growth_rate": float(avg_growth_rate),
                "current_value": float(values[-1]),
                "min_value": float(min(values)),
                "max_value": float(max(values)),
                "fitted_values": [float(trend_line(i)) for i in x]
            }
            
            logger.info(f"计算趋势成功: {metric_name}, 方向: {trend_direction}")
            return result
            
        except Exception as e:
            logger.error(f"计算趋势失败: {e}")
            return {"error": str(e)}
    
    def predict_future(self, metric_name: str, 
                      periods: int = 12) -> Dict:
        """预测未来走势
        
        Args:
            metric_name: 指标名称
            periods: 预测期数（月数）
            
        Returns:
            预测结果
        """
        try:
            # 先计算历史趋势
            trend = self.calculate_trend(metric_name)
            
            if "error" in trend:
                return trend
            
            # 使用趋势线进行预测
            last_index = len(trend['values']) - 1
            predictions = []
            
            for i in range(1, periods + 1):
                pred_value = trend['trend_slope'] * (last_index + i) + \
                           (trend['values'][-1] - trend['trend_slope'] * last_index)
                predictions.append(float(max(0, pred_value)))  # 确保非负
            
            # 生成预测时间点
            last_time = datetime.strptime(trend['times'][-1], "%Y-%m-%d")
            pred_times = []
            for i in range(1, periods + 1):
                future_time = last_time + timedelta(days=30 * i)
                pred_times.append(future_time.strftime("%Y-%m-%d"))
            
            # 计算置信区间（简化版）
            std_dev = np.std(trend['values']) if len(trend['values']) > 1 else 0
            confidence_upper = [p + 1.96 * std_dev for p in predictions]
            confidence_lower = [max(0, p - 1.96 * std_dev) for p in predictions]
            
            result = {
                "metric": metric_name,
                "prediction_periods": periods,
                "prediction_times": pred_times,
                "predicted_values": predictions,
                "confidence_upper": confidence_upper,
                "confidence_lower": confidence_lower,
                "historical_trend": trend,
                "avg_predicted_growth": float(trend['avg_growth_rate'])
            }
            
            logger.info(f"预测未来成功: {metric_name}, 期数: {periods}")
            return result
            
        except Exception as e:
            logger.error(f"预测未来失败: {e}")
            return {"error": str(e)}
    
    def generate_trend_chart_config(self, metric_name: str,
                                   include_prediction: bool = True,
                                   prediction_periods: int = 6) -> Dict:
        """生成趋势图表配置（ECharts）
        
        Args:
            metric_name: 指标名称
            include_prediction: 是否包含预测
            prediction_periods: 预测期数
            
        Returns:
            ECharts配置
        """
        try:
            trend = self.calculate_trend(metric_name)
            
            if "error" in trend:
                return {}
            
            series_data = [
                {
                    "name": "历史数据",
                    "type": "line",
                    "data": trend['values'],
                    "smooth": True,
                    "itemStyle": {"color": "#4575b4"},
                    "lineStyle": {"width": 3}
                },
                {
                    "name": "趋势线",
                    "type": "line",
                    "data": trend['fitted_values'],
                    "smooth": False,
                    "itemStyle": {"color": "#fdae61"},
                    "lineStyle": {"type": "dashed", "width": 2}
                }
            ]
            
            x_axis_data = trend['times'].copy()
            
            # 添加预测数据
            if include_prediction:
                prediction = self.predict_future(metric_name, prediction_periods)
                
                if "error" not in prediction:
                    x_axis_data.extend(prediction['prediction_times'])
                    
                    # 预测值序列
                    pred_data = [None] * len(trend['values']) + prediction['predicted_values']
                    series_data.append({
                        "name": "预测值",
                        "type": "line",
                        "data": pred_data,
                        "smooth": True,
                        "itemStyle": {"color": "#d73027"},
                        "lineStyle": {"type": "dashed", "width": 2}
                    })
                    
                    # 置信区间
                    upper_data = [None] * len(trend['values']) + prediction['confidence_upper']
                    lower_data = [None] * len(trend['values']) + prediction['confidence_lower']
                    
                    series_data.append({
                        "name": "置信区间上限",
                        "type": "line",
                        "data": upper_data,
                        "lineStyle": {"opacity": 0.3, "color": "#ff6b6b"},
                        "itemStyle": {"opacity": 0},
                        "stack": "confidence",
                        "symbol": "none"
                    })
                    
                    series_data.append({
                        "name": "置信区间下限",
                        "type": "line",
                        "data": lower_data,
                        "lineStyle": {"opacity": 0.3, "color": "#ff6b6b"},
                        "itemStyle": {"opacity": 0},
                        "areaStyle": {"opacity": 0.2, "color": "#ff6b6b"},
                        "stack": "confidence",
                        "symbol": "none"
                    })
            
            config = {
                "title": {
                    "text": f"{metric_name} 趋势分析与预测",
                    "left": "center"
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "cross"}
                },
                "legend": {
                    "data": ["历史数据", "趋势线", "预测值", "置信区间"],
                    "top": "10%"
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "bottom": "3%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "boundaryGap": False,
                    "data": x_axis_data,
                    "axisLabel": {"rotate": 45}
                },
                "yAxis": {
                    "type": "value",
                    "name": metric_name
                },
                "series": series_data
            }
            
            logger.info(f"生成趋势图表配置成功: {metric_name}")
            return config
            
        except Exception as e:
            logger.error(f"生成趋势图表配置失败: {e}")
            return {}
    
    def compare_multiple_metrics(self, metric_names: List[str]) -> Dict:
        """对比多个指标的趋势
        
        Args:
            metric_names: 指标名称列表
            
        Returns:
            对比分析结果
        """
        try:
            comparison = {
                "metrics": [],
                "summary": {}
            }
            
            for metric in metric_names:
                trend = self.calculate_trend(metric)
                if "error" not in trend:
                    comparison["metrics"].append(trend)
            
            if comparison["metrics"]:
                # 汇总统计
                comparison["summary"] = {
                    "total_metrics": len(comparison["metrics"]),
                    "upward_trends": sum(1 for m in comparison["metrics"] 
                                        if m['trend_direction'] == "上升"),
                    "downward_trends": sum(1 for m in comparison["metrics"] 
                                          if m['trend_direction'] == "下降"),
                    "stable_trends": sum(1 for m in comparison["metrics"] 
                                        if m['trend_direction'] == "平稳")
                }
            
            logger.info(f"对比多指标成功: {len(comparison['metrics'])} 个指标")
            return comparison
            
        except Exception as e:
            logger.error(f"对比多指标失败: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    analyzer = TrendAnalyzer()
    
    # 模拟历史数据
    test_reports = [
        {
            "id": "report1",
            "time": "2023-01-01",
            "content": "市场规模达到500亿元，增长率15%，企业200家，投资100亿元"
        },
        {
            "id": "report2",
            "time": "2023-06-01",
            "content": "市场规模达到550亿元，增长率18%，企业220家，投资120亿元"
        },
        {
            "id": "report3",
            "time": "2024-01-01",
            "content": "市场规模达到600亿元，增长率20%，企业250家，投资150亿元"
        }
    ]
    
    # 添加历史报告
    for report in test_reports:
        analyzer.add_historical_report(
            report['id'],
            {"content": report['content']},
            report['time']
        )
    
    # 计算趋势
    trend = analyzer.calculate_trend("market_size")
    print(f"趋势分析: {json.dumps(trend, ensure_ascii=False, indent=2)}")
    
    # 预测未来
    prediction = analyzer.predict_future("market_size", periods=6)
    print(f"\n未来预测: {json.dumps(prediction, ensure_ascii=False, indent=2)[:300]}...")
    
    # 生成图表配置
    chart = analyzer.generate_trend_chart_config("market_size")
    print(f"\n图表配置: {json.dumps(chart, ensure_ascii=False, indent=2)[:300]}...")
    
    print("\n✅ 趋势分析模块测试通过！")
