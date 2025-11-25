"""
Dashboard Generation Module for Regional Industrial Analysis
Creates interactive charts and visual components from analyzed data.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

logger = logging.getLogger(__name__)

class DashboardGenerator:
    """Generate dashboard data and visualizations from analysis results."""
    
    def __init__(self):
        """Initialize dashboard generator."""
        self.colors = {
            'primary': '#2563eb',
            'secondary': '#7c3aed',
            'success': '#059669',
            'warning': '#d97706',
            'danger': '#dc2626',
            'info': '#0891b2',
            'light': '#f1f5f9',
            'dark': '#1e293b'
        }
    
    def generate_dashboard_data(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete dashboard data from analysis results."""
        try:
            dashboard_data = {
                'title': self._generate_title(analysis_result),
                'summary': self._generate_summary(analysis_result),
                'charts': self._generate_charts(analysis_result),
                'categories': self._process_categories(analysis_result.get('categories', {})),
                'key_insights': analysis_result.get('key_insights', []),
                'ai_opportunities': self._process_ai_opportunities(analysis_result.get('ai_opportunities', {})),
                'statistics': analysis_result.get('statistics', {}),
                'sentiment_analysis': analysis_result.get('sentiment_analysis', {}),
                'metadata': analysis_result.get('metadata', {}),
                'timestamp': datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return self._get_empty_dashboard()
    
    def _generate_title(self, analysis_result: Dict[str, Any]) -> str:
        """Generate dashboard title from analysis metadata."""
        metadata = analysis_result.get('metadata', {})
        source_file = metadata.get('source_file', '区域产业分析')
        
        # Extract potential region/industry from filename or content
        if '.' in source_file:
            title_base = source_file.rsplit('.', 1)[0]
        else:
            title_base = source_file
        
        # Clean up title - remove long timestamp sequences
        title_base = title_base.replace('_', ' ').replace('-', ' ')
        
        # Remove long sequences of numbers (likely timestamps)
        import re
        title_base = re.sub(r'\d{8}_?\d{6}', '', title_base).strip()
        
        # If title is still too long, extract just the meaningful part
        if len(title_base) > 30:
            # Try to extract meaningful words, removing timestamps and IDs
            words = title_base.split()
            if len(words) > 5:
                # Take first few words that are likely to be meaningful
                meaningful_words = [word for word in words if not re.match(r'^\d+$', word) and len(word) > 1]
                title_base = ' '.join(meaningful_words[:5])  # Limit to first 5 meaningful words
        
        # If we still have a very long title, use a generic one
        if len(title_base) > 50:
            title_base = "区域产业分析报告"
        
        # If title base is empty or too short, use a default
        if len(title_base.strip()) < 2:
            title_base = "区域产业分析报告"
        
        return f"{title_base} - AIPE区域产业分析小工作台"
    
    def _generate_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary from analysis results."""
        stats = analysis_result.get('statistics', {})
        categories = analysis_result.get('categories', {})
        ai_opportunities = analysis_result.get('ai_opportunities', {})
        
        # Count active categories
        active_categories = len([cat for cat in categories if categories[cat].get('content')])
        
        # Count AI opportunities
        high_priority_ai = len([opp for opp in ai_opportunities.values() 
                              if opp.get('potential_score', 0) > 70])
        
        summary = {
            'word_count': stats.get('total_words', 0),
            'reading_time': stats.get('reading_time_minutes', 0),
            'categories_analyzed': active_categories,
            'ai_opportunities': len(ai_opportunities),
            'high_priority_ai': high_priority_ai,
            'key_highlights': self._extract_key_highlights(analysis_result)
        }
        
        return summary
    
    def _extract_key_highlights(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Extract key highlights from the analysis."""
        highlights = []
        
        categories = analysis_result.get('categories', {})
        
        # Find top categories by content volume
        category_scores = []
        for cat_name, cat_data in categories.items():
            score = cat_data.get('relevance_score', 0)
            if score > 0:
                category_scores.append((cat_name, score))
        
        category_scores.sort(key=lambda x: x[1], reverse=True)
        
        if category_scores:
            top_category = category_scores[0][0]
            highlights.append(f"重点关注领域：{top_category}")
        
        # Add AI opportunity highlights
        ai_opportunities = analysis_result.get('ai_opportunities', {})
        top_ai = max(ai_opportunities.items(), 
                    key=lambda x: x[1].get('potential_score', 0), 
                    default=None)
        
        if top_ai and top_ai[1].get('potential_score', 0) > 50:
            highlights.append(f"AI应用潜力最高：{top_ai[0]}")
        
        # Add statistical highlights
        stats = analysis_result.get('statistics', {})
        if stats.get('total_words', 0) > 5000:
            highlights.append("内容详实，信息丰富")
        elif stats.get('total_words', 0) > 1000:
            highlights.append("内容适中，重点突出")
        
        return highlights[:5]  # Limit to 5 highlights
    
    def _generate_charts(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all chart data for the dashboard."""
        charts = {}
        
        try:
            # Category distribution chart
            charts['category_distribution'] = self._create_category_chart(analysis_result.get('categories', {}))
            
            # AI opportunities radar chart
            charts['ai_opportunities'] = self._create_ai_radar_chart(analysis_result.get('ai_opportunities', {}))
            
            # Keyword frequency chart
            key_insights = analysis_result.get('key_insights', [])
            keyword_data = next((insight for insight in key_insights if insight.get('type') == 'top_keywords'), None)
            if keyword_data:
                charts['keyword_frequency'] = self._create_keyword_chart(keyword_data.get('data', []))
            
            # Statistics overview
            charts['statistics_overview'] = self._create_statistics_chart(analysis_result.get('statistics', {}))
            
            # Sentiment analysis chart
            sentiment_data = analysis_result.get('sentiment_analysis', {})
            if sentiment_data and sentiment_data.get('overall_sentiment') != '未知':
                charts['sentiment_analysis'] = self._create_sentiment_chart(sentiment_data)
            
            # POS analysis chart
            pos_data = next((insight for insight in key_insights if insight.get('type') == 'pos_analysis'), None)
            if pos_data:
                charts['pos_analysis'] = self._create_pos_chart(pos_data.get('data', []))
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
        
        return charts
    
    def _create_category_chart(self, categories: Dict[str, Any]) -> Dict[str, Any]:
        """Create category distribution donut chart."""
        try:
            category_names = []
            category_scores = []
            
            for cat_name, cat_data in categories.items():
                score = cat_data.get('relevance_score', 0)
                if score > 0:
                    category_names.append(cat_name)
                    category_scores.append(score)
            
            if not category_names:
                return {'error': 'No category data available'}
            
            # Return simple data structure instead of Plotly figure
            return {
                'data': [{
                    'labels': category_names,
                    'chart_values': category_scores,
                    'type': 'pie'
                }]
            }
            
        except Exception as e:
            logger.error(f"Error creating category chart: {e}")
            return {'error': str(e)}
    
    def _create_statistics_chart(self, statistics: Dict[str, Any]) -> Dict[str, Any]:
        """Create statistics overview chart data."""
        try:
            if not statistics:
                return {'error': 'No statistics data available'}
            
            # Return simple data structure
            return {
                'data': [{
                    'labels': ['总字符数', '总词数', '文本段数', '平均段落长度', '阅读时间(分钟)', '唯一词数'],
                    'values': [
                        statistics.get('total_characters', 0),
                        statistics.get('total_words', 0),
                        statistics.get('total_segments', 0),
                        statistics.get('avg_segment_length', 0),
                        statistics.get('reading_time_minutes', 0),
                        statistics.get('unique_words', 0)
                    ],
                    'type': 'bar'
                }]
            }
            
        except Exception as e:
            logger.error(f"Error creating statistics chart: {e}")
            return {'error': str(e)}
            
            categories = list(ai_opportunities.keys())
            values = [opp.get('potential_score', 0) / 10 for opp in ai_opportunities.values()]
            
            # Return simple data structure for horizontal bar chart
            return {
                'data': [{
                    'x': values,
                    'y': categories,
                    'type': 'bar',
                    'orientation': 'h'
                }]
            }
            
        except Exception as e:
            logger.error(f"Error creating AI chart: {e}")
            return {'error': str(e)}
    
    def _create_keyword_chart(self, keyword_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create keyword frequency bar chart data."""
        try:
            if not keyword_data:
                return {'error': 'No keyword data available'}
            
            terms = [item['term'] for item in keyword_data[:10]]  # Top 10
            frequencies = [item['frequency'] for item in keyword_data[:10]]
            
            # Return simple data structure
            return {
                'data': [{
                    'x': terms,
                    'y': frequencies,
                    'type': 'bar'
                }]
            }
            
        except Exception as e:
            logger.error(f"Error creating keyword chart: {e}")
            return {'error': str(e)}
    
    def _create_sentiment_chart(self, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create sentiment analysis chart data."""
        try:
            if not sentiment_data:
                return {'error': 'No sentiment data available'}
            
            # 创建情感分析柱状图
            labels = ['积极', '中性', '消极']
            positive_count = sentiment_data.get('positive_segments', 0)
            negative_count = sentiment_data.get('negative_segments', 0)
            total_segments = sentiment_data.get('total_segments', 1)
            neutral_count = total_segments - positive_count - negative_count
            
            values = [positive_count, neutral_count, negative_count]
            
            return {
                'data': [{
                    'x': labels,
                    'y': values,
                    'type': 'bar',
                    'marker': {
                        'color': ['#059669', '#0891b2', '#dc2626']  # 绿色、蓝色、红色
                    }
                }],
                'layout': {
                    'title': '情感分析分布',
                    'xaxis': {'title': '情感倾向'},
                    'yaxis': {'title': '段落数量'}
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating sentiment chart: {e}")
            return {'error': str(e)}
    
    def _create_pos_chart(self, pos_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create chart for POS (Part of Speech) analysis."""
        if not pos_data:
            # Return empty chart data structure instead of empty dict
            return {
                'data': [{
                    'type': 'bar',
                    'x': [],
                    'y': [],
                    'marker': {
                        'color': self.colors['primary']
                    }
                }],
                'layout': {
                    'title': '词性分析统计',
                    'xaxis': {'title': '词性'},
                    'yaxis': {'title': '出现次数'}
                }
            }
        
        try:
            # Extract POS categories and counts
            categories = []
            counts = []
            
            for item in pos_data:
                categories.append(item.get('pos', 'Unknown'))
                counts.append(item.get('count', 0))
            
            if not categories:
                # Return empty chart data structure instead of empty dict
                return {
                    'data': [{
                        'type': 'bar',
                        'x': [],
                        'y': [],
                        'marker': {
                            'color': self.colors['primary']
                        }
                    }],
                    'layout': {
                        'title': '词性分析统计',
                        'xaxis': {'title': '词性'},
                        'yaxis': {'title': '出现次数'}
                    }
                }
            
            # Create bar chart data
            return {
                'data': [{
                    'type': 'bar',
                    'x': categories,
                    'y': counts,
                    'marker': {
                        'color': self.colors['primary']
                    }
                }],
                'layout': {
                    'title': '词性分析统计',
                    'xaxis': {'title': '词性'},
                    'yaxis': {'title': '出现次数'}
                }
            }
        except Exception as e:
            logger.error(f"Error creating POS chart: {e}")
            # Return empty chart data structure on error
            return {
                'data': [{
                    'type': 'bar',
                    'x': [],
                    'y': [],
                    'marker': {
                        'color': self.colors['primary']
                    }
                }],
                'layout': {
                    'title': '词性分析统计',
                    'xaxis': {'title': '词性'},
                    'yaxis': {'title': '出现次数'}
                }
            }
    
    def _process_categories(self, categories: Dict[str, Any]) -> Dict[str, Any]:
        """Process categories data for better dashboard display."""
        processed = {}
        
        for cat_name, cat_data in categories.items():
            content_items = cat_data.get('content', [])
            key_points = cat_data.get('key_points', [])
            relevance_score = cat_data.get('relevance_score', 0)
            
            processed[cat_name] = {
                'relevance_score': relevance_score,
                'content_count': len(content_items),
                'key_points': key_points,
                'top_content': [item['text'] for item in content_items[:3]],  # Top 3 most relevant
                'has_content': len(content_items) > 0,
                'priority_level': self._get_priority_level(relevance_score)
            }
        
        return processed
    
    def _process_ai_opportunities(self, ai_opportunities: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI opportunities data for dashboard display."""
        processed = {}
        
        for ai_area, opp_data in ai_opportunities.items():
            score = opp_data.get('potential_score', 0)
            
            processed[ai_area] = {
                'potential_score': score,
                'priority_level': self._get_priority_level(score),
                'recommendation': opp_data.get('recommendation', ''),
                'relevant_content': opp_data.get('relevant_content', []),
                'color': self._get_score_color(score)
            }
        
        return processed
    
    def _get_priority_level(self, score: int) -> str:
        """Get priority level based on score."""
        if score >= 70:
            return 'high'
        elif score >= 40:
            return 'medium'
        elif score > 0:
            return 'low'
        else:
            return 'none'
    
    def _get_score_color(self, score: int) -> str:
        """Get color based on score."""
        if score >= 70:
            return self.colors['success']
        elif score >= 40:
            return self.colors['warning']
        elif score > 0:
            return self.colors['info']
        else:
            return self.colors['light']
    
    def _create_ai_radar_chart(self, ai_opportunities: Dict[str, Any]) -> Dict[str, Any]:
        """Create radar chart for AI opportunities."""
        if not ai_opportunities:
            # Return empty chart data structure instead of empty dict
            return {
                'data': [{
                    'type': 'scatterpolar',
                    'r': [],
                    'theta': [],
                    'fill': 'toself',
                    'name': 'AI应用机会'
                }],
                'layout': {
                    'polar': {
                        'radialaxis': {
                            'visible': True,
                            'range': [0, 100]
                        }
                    },
                    'showlegend': False,
                    'title': 'AI应用机会雷达图'
                }
            }
        
        try:
            # Extract opportunity names and scores
            opportunities = []
            scores = []
            
            for opp_name, opp_data in ai_opportunities.items():
                opportunities.append(opp_name)
                scores.append(opp_data.get('potential_score', 0))
            
            if not opportunities:
                # Return empty chart data structure instead of empty dict
                return {
                    'data': [{
                        'type': 'scatterpolar',
                        'r': [],
                        'theta': [],
                        'fill': 'toself',
                        'name': 'AI应用机会'
                    }],
                    'layout': {
                        'polar': {
                            'radialaxis': {
                                'visible': True,
                                'range': [0, 100]
                            }
                        },
                        'showlegend': False,
                        'title': 'AI应用机会雷达图'
                    }
                }
            
            # Create radar chart data
            return {
                'data': [{
                    'type': 'scatterpolar',
                    'r': scores,
                    'theta': opportunities,
                    'fill': 'toself',
                    'name': 'AI应用机会'
                }],
                'layout': {
                    'polar': {
                        'radialaxis': {
                            'visible': True,
                            'range': [0, 100]
                        }
                    },
                    'showlegend': False,
                    'title': 'AI应用机会雷达图'
                }
            }
        except Exception as e:
            logger.error(f"Error creating AI radar chart: {e}")
            # Return empty chart data structure on error
            return {
                'data': [{
                    'type': 'scatterpolar',
                    'r': [],
                    'theta': [],
                    'fill': 'toself',
                    'name': 'AI应用机会'
                }],
                'layout': {
                    'polar': {
                        'radialaxis': {
                            'visible': True,
                            'range': [0, 100]
                        }
                    },
                    'showlegend': False,
                    'title': 'AI应用机会雷达图'
                }
            }
    
    def _get_empty_dashboard(self) -> Dict[str, Any]:
        """Get empty dashboard structure for error cases."""
        return {
            'title': '区域产业分析小工作台',
            'summary': {
                'word_count': 0,
                'reading_time': 0,
                'categories_analyzed': 0,
                'ai_opportunities': 0,
                'high_priority_ai': 0,
                'key_highlights': ['无可用数据']
            },
            'charts': {},
            'categories': {},
            'key_insights': [],
            'ai_opportunities': {},
            'statistics': {},
            'metadata': {},
            'timestamp': datetime.now().isoformat(),
            'error': 'Failed to generate dashboard data'
        }