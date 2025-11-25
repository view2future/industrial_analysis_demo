#!/usr/bin/env python3
"""Investment Value Evaluation Module"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class InvestmentEvaluator:
    """Evaluate investment value of industries."""
    
    def evaluate(self, report_data: Dict) -> Dict:
        """Evaluate investment value based on report content."""
        try:
            content = report_data.get('full_content', '')
            
            # Simple scoring based on keywords
            scores = {
                'policy_support': self._score_policy(content),
                'market_size': self._score_market(content),
                'tech_maturity': self._score_technology(content),
                'competition': self._score_competition(content)
            }
            
            overall_score = sum(scores.values()) / len(scores)
            
            # Investment recommendation
            if overall_score >= 8:
                recommendation = '强烈推荐'
                level = 'high'
            elif overall_score >= 6:
                recommendation = '建议投资'
                level = 'medium'
            else:
                recommendation = '谨慎观望'
                level = 'low'
            
            return {
                'scores': scores,
                'overall_score': round(overall_score, 2),
                'recommendation': recommendation,
                'level': level
            }
        except Exception as e:
            logger.error(f"Error evaluating investment: {e}")
            return self._get_default_evaluation()
    
    def _score_policy(self, text: str) -> float:
        """Score policy support (0-10)."""
        positive_keywords = ['政策支持', '优惠政策', '补贴', '扶持', '鼓励']
        score = min(10, sum(2 for kw in positive_keywords if kw in text))
        return score
    
    def _score_market(self, text: str) -> float:
        """Score market size (0-10)."""
        positive_keywords = ['市场规模', '增长', '扩大', '需求旺盛']
        score = min(10, sum(2 for kw in positive_keywords if kw in text))
        return score
    
    def _score_technology(self, text: str) -> float:
        """Score technology maturity (0-10)."""
        positive_keywords = ['技术成熟', '创新', '领先', '突破']
        score = min(10, sum(2 for kw in positive_keywords if kw in text))
        return score
    
    def _score_competition(self, text: str) -> float:
        """Score competition level (0-10, higher is better = less competition)."""
        negative_keywords = ['竞争激烈', '红海', '过度竞争']
        penalty = sum(2 for kw in negative_keywords if kw in text)
        return max(0, 8 - penalty)
    
    def _get_default_evaluation(self) -> Dict:
        """Return default evaluation."""
        return {
            'scores': {
                'policy_support': 5.0,
                'market_size': 5.0,
                'tech_maturity': 5.0,
                'competition': 5.0
            },
            'overall_score': 5.0,
            'recommendation': '数据不足',
            'level': 'unknown'
        }
