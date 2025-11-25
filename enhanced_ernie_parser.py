import logging
from typing import Dict, List
from ernie_bot_client import ErnieBotClient

logger = logging.getLogger(__name__)

class EnhancedErniePolicyParser:
    def __init__(self):
        self.ernie_client = ErnieBotClient()
    
    def parse_policy_document(self, document_text: str) -> Dict:
        """Parse policy document using ERNIE Bot"""
        try:
            # Get structured information from ERNIE Bot
            ernie_result = self.ernie_client.extract_policy_info(document_text)

            if "error" in ernie_result:
                logger.error(f"ERNIE Bot parsing failed: {ernie_result['error']}")
                return self._fallback_parsing(document_text)

            # Organize the results into our expected format
            structured_data = self._organize_ernie_result(ernie_result, document_text)

            return structured_data

        except Exception as e:
            logger.error(f"Error in ERNIE Bot parsing: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._fallback_parsing(document_text)
    
    def _organize_ernie_result(self, ernie_result: Dict, original_text: str) -> Dict:
        """Organize ERNIE Bot results into our expected format"""
        # Map ERNIE result to our structure
        # Handle different possible key variations (including new structured format)
        title = (ernie_result.get('basic_info', {}).get('政策标题') or
                ernie_result.get('basic_info', {}).get('title') or
                ernie_result.get('title') or
                ernie_result.get('政策标题') or
                '未知政策标题')

        issuing_authority = (ernie_result.get('basic_info', {}).get('发文机关') or
                           ernie_result.get('basic_info', {}).get('issuing_authority') or
                           ernie_result.get('issuing_authority') or
                           ernie_result.get('发文机关') or
                           '未知')

        publication_date = (ernie_result.get('basic_info', {}).get('发布日期') or
                          ernie_result.get('basic_info', {}).get('publication_date') or
                          ernie_result.get('publication_date') or
                          ernie_result.get('发布日期') or
                          '')

        applicable_regions = (ernie_result.get('basic_info', {}).get('适用区域') or
                            ernie_result.get('basic_info', {}).get('applicable_regions') or
                            ernie_result.get('applicable_regions') or
                            ernie_result.get('适用区域') or
                            [])

        if isinstance(applicable_regions, str):
            applicable_regions = [applicable_regions]

        key_industries = (ernie_result.get('basic_info', {}).get('重点产业') or
                         ernie_result.get('basic_info', {}).get('key_industries') or
                         ernie_result.get('key_industries') or
                         ernie_result.get('重点产业') or
                         [])

        if isinstance(key_industries, str):
            key_industries = [key_industries]

        metadata = {
            'title': title,
            'issuing_authority': issuing_authority,
            'publication_date': publication_date,
            'applicable_regions': applicable_regions,
            'key_industries': key_industries
        }

        # Extract summary if available in new format
        summary_text = (ernie_result.get('summary') or
                       ernie_result.get('摘要') or
                       self.ernie_client.generate_summary(original_text))

        # Extract provisions (support measures)
        provisions = []
        support_measures = (ernie_result.get('support_measures') or
                           ernie_result.get('支持措施') or
                           ernie_result.get('basic_info', {}).get('support_measures') or
                           ernie_result.get('basic_info', {}).get('支持措施') or
                           [])

        if isinstance(support_measures, str):
            provisions = [{'description': support_measures}]
        elif isinstance(support_measures, list):
            for item in support_measures:
                if isinstance(item, dict):
                    provisions.append(item)
                else:
                    provisions.append({'description': str(item)})

        # Extract requirements
        requirements = []
        raw_requirements = (ernie_result.get('requirements') or
                           ernie_result.get('要求条件') or
                           ernie_result.get('基本要求') or
                           [])

        if isinstance(raw_requirements, str):
            requirements = [{'requirement': raw_requirements, 'type': 'positive'}]
        elif isinstance(raw_requirements, list):
            for item in raw_requirements:
                if isinstance(item, dict):
                    requirements.append(item)
                else:
                    requirements.append({'requirement': str(item), 'type': 'positive'})

        # Extract quantitative data (with priority to the dedicated quantitative_indicators field)
        quantitative_indicators = ernie_result.get('quantitative_indicators', []) or ernie_result.get('量化指标', [])

        # Extract from various possible fields
        amounts = (ernie_result.get('特定金额') or
                  ernie_result.get('specific_amounts') or
                  ernie_result.get('amounts') or
                  [])

        if isinstance(amounts, str):
            amounts = [amounts]

        # Combine amounts with quantitative indicators
        if isinstance(quantitative_indicators, list):
            # Extract amounts from quantitative indicators if they contain amount information
            for indicator in quantitative_indicators:
                if isinstance(indicator, str) and any(keyword in indicator.lower() for keyword in ['元', '万元', '千', '百', '亿', '万']):
                    amounts.append(indicator)

        thresholds = (ernie_result.get('门槛') or
                     ernie_result.get('thresholds') or
                     [])

        if isinstance(thresholds, str):
            thresholds = [thresholds]

        ratios = (ernie_result.get('比例') or
                 ernie_result.get('ratios') or
                 [])

        if isinstance(ratios, str):
            ratios = [ratios]

        quantitative_data = {
            'amounts': amounts,
            'thresholds': thresholds,
            'ratios': ratios,
            'quantitative_indicators': quantitative_indicators,  # Store dedicated quantitative indicators
            'time_periods': []
        }

        # Extract timeline
        timeline_events = []
        time_nodes = (ernie_result.get('timeline') or
                     ernie_result.get('时间节点') or
                     ernie_result.get('时间安排') or
                     [])

        if isinstance(time_nodes, list):
            for node in time_nodes:
                if isinstance(node, dict):
                    timeline_events.append({
                        'date': node.get('date', ''),
                        'event': node.get('event', str(node)),
                        'type': node.get('type', 'event')
                    })
                else:
                    timeline_events.append({
                        'date': '',
                        'event': str(node),
                        'type': 'event'
                    })

        # Use ERNIE to generate additional content
        key_points = self.ernie_client.extract_key_points(original_text)
        if key_points == ["要点提取失败"]:
            # Fallback to the content if extraction failed
            key_points = [original_text[:200] + "..." if len(original_text) > 200 else original_text]

        # If we have a dedicated summary from the structured response, use it
        if not isinstance(summary_text, str):
            summary_text = self.ernie_client.generate_summary(original_text)

        return {
            'metadata': metadata,
            'summary': summary_text,
            'key_points': [summary_text] + key_points[:5],  # Include summary as first key point, with more points for quant indicators
            'provisions': provisions,
            'requirements': requirements,
            'quantitative_data': quantitative_data,
            'timeline': timeline_events,
            'full_text': original_text,
            'analysis': {
                'industry_relevance': {
                    'value_chain': {
                        'upstream': metadata['key_industries'][:3] if metadata['key_industries'] else [],
                        'midstream': metadata['key_industries'][1:4] if len(metadata['key_industries']) > 1 else [],
                        'downstream': metadata['key_industries'][2:5] if len(metadata['key_industries']) > 2 else []
                    },
                    'related_industries': metadata['key_industries']
                },
                'policy_strength': {
                    'funding_level': '高' if any('高' in str(item) or '千万' in str(item) or '1000' in str(item) for item in quantitative_data['amounts']) else '中',
                    'measure_diversity': len(provisions),
                    'support_comprehensiveness': '全面' if len(provisions) > 2 else '部分'
                },
                'timeliness_score': 85,  # Default score; would be calculated based on date
                'regional_match_score': 80  # Default score; would be calculated based on region
            }
        }
    
    def _fallback_parsing(self, document_text: str) -> Dict:
        """Fallback to basic parsing if ERNIE Bot fails"""
        logger.warning("Falling back to basic parsing due to ERNIE Bot error")
        
        # For now, return a basic structure
        return {
            'metadata': {
                'title': 'ERNIE Bot 解析失败 - 使用基础分析',
                'issuing_authority': '未知',
                'publication_date': '',
                'applicable_regions': [],
                'key_industries': []
            },
            'key_points': ['ERNIE Bot 文档解析失败，请稍后重试'],
            'provisions': [],
            'requirements': [],
            'quantitative_data': {'amounts': [], 'thresholds': [], 'ratios': [], 'time_periods': []},
            'timeline': [],
            'full_text': document_text,
            'analysis': {
                'industry_relevance': {'value_chain': {'upstream': [], 'midstream': [], 'downstream': []}, 'related_industries': []},
                'policy_strength': {'funding_level': '未知', 'measure_diversity': 0, 'support_comprehensiveness': '未知'},
                'timeliness_score': 0,
                'regional_match_score': 0
            }
        }