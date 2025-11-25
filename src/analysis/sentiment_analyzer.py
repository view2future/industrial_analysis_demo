#!/usr/bin/env python3
"""
Sentiment Analysis Module
Analyze sentiment and emotional tone of reports
"""

import logging
from typing import Dict, List
from snownlp import SnowNLP

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment of Chinese text."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.positive_keywords = [
            '优势', '机遇', '增长', '提升', '创新', '领先', '优秀', '强大',
            '发展', '进步', '改善', '繁荣', '成功', '突破', '完善'
        ]
        
        self.negative_keywords = [
            '劣势', '威胁', '风险', '挑战', '困难', '问题', '缺陷', '不足',
            '落后', '下降', '减少', '薄弱', '危机', '障碍', '限制'
        ]
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of text.
        
        Args:
            text: Chinese text to analyze
        
        Returns:
            Dictionary with sentiment scores and analysis
        """
        try:
            if not text:
                return self._get_default_sentiment()
            
            # Use SnowNLP for Chinese sentiment analysis
            s = SnowNLP(text)
            overall_sentiment = s.sentiments
            
            # Count keywords
            positive_count = sum(1 for kw in self.positive_keywords if kw in text)
            negative_count = sum(1 for kw in self.negative_keywords if kw in text)
            
            # Calculate sentiment distribution
            total_keywords = positive_count + negative_count
            if total_keywords > 0:
                positive_ratio = positive_count / total_keywords
                negative_ratio = negative_count / total_keywords
            else:
                positive_ratio = overall_sentiment
                negative_ratio = 1 - overall_sentiment
            
            # Determine sentiment category
            if overall_sentiment > 0.6:
                category = 'positive'
                category_label = '积极'
            elif overall_sentiment < 0.4:
                category = 'negative'
                category_label = '消极'
            else:
                category = 'neutral'
                category_label = '中性'
            
            return {
                'overall_score': round(overall_sentiment, 3),
                'category': category,
                'category_label': category_label,
                'positive_ratio': round(positive_ratio, 3),
                'negative_ratio': round(negative_ratio, 3),
                'neutral_ratio': round(1 - positive_ratio - negative_ratio, 3),
                'positive_keywords_count': positive_count,
                'negative_keywords_count': negative_count,
                'confidence': round(abs(overall_sentiment - 0.5) * 2, 3)
            }
        
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return self._get_default_sentiment()
    
    def analyze_by_category(self, report_data: Dict) -> Dict:
        """Analyze sentiment by report categories.
        
        Args:
            report_data: Report data with sections
        
        Returns:
            Dictionary with sentiment analysis by category
        """
        try:
            category_sentiments = {}
            
            # Analyze different sections if available
            if 'sections' in report_data:
                for section_name, section_content in report_data['sections'].items():
                    if section_content:
                        sentiment = self.analyze_text(section_content)
                        category_sentiments[section_name] = sentiment
            
            # Overall sentiment
            full_content = report_data.get('full_content', '')
            overall_sentiment = self.analyze_text(full_content)
            
            return {
                'overall': overall_sentiment,
                'by_category': category_sentiments
            }
        
        except Exception as e:
            logger.error(f"Error in category sentiment analysis: {e}")
            return {
                'overall': self._get_default_sentiment(),
                'by_category': {}
            }
    
    def detect_risks(self, text: str, threshold: float = 0.4) -> List[str]:
        """Detect potential risks in text.
        
        Args:
            text: Text to analyze
            threshold: Sentiment threshold for risk detection
        
        Returns:
            List of detected risk indicators
        """
        risks = []
        
        # Check overall sentiment
        sentiment = self.analyze_text(text)
        if sentiment['overall_score'] < threshold:
            risks.append(f"整体情感偏负面 (得分: {sentiment['overall_score']})")
        
        # Check for specific risk keywords
        risk_keywords = {
            '高风险': ['风险高', '重大风险', '严重威胁'],
            '市场风险': ['市场波动', '需求下降', '竞争激烈'],
            '政策风险': ['政策不确定', '监管压力', '合规风险'],
            '技术风险': ['技术落后', '创新不足', '技术瓶颈'],
            '资金风险': ['资金紧张', '融资困难', '成本上升']
        }
        
        for risk_type, keywords in risk_keywords.items():
            if any(kw in text for kw in keywords):
                risks.append(f"检测到{risk_type}")
        
        return risks
    
    def _get_default_sentiment(self) -> Dict:
        """Get default sentiment structure."""
        return {
            'overall_score': 0.5,
            'category': 'neutral',
            'category_label': '中性',
            'positive_ratio': 0.33,
            'negative_ratio': 0.33,
            'neutral_ratio': 0.34,
            'positive_keywords_count': 0,
            'negative_keywords_count': 0,
            'confidence': 0.0
        }
