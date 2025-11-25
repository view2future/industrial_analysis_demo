import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HybridPolicyParser:
    def __init__(self):
        # Initialize Kimi parser if config is available
        try:
            from src.ai.kimi_policy_parser import KimiPolicyParser
            self.kimi_parser = KimiPolicyParser()
        except ImportError as e:
            logger.warning(f"Kimi parser not available: {e}")
            self.kimi_parser = None

        # Initialize ERNIE parser if config is available
        try:
            from enhanced_ernie_parser import EnhancedErniePolicyParser
            self.ernie_parser = EnhancedErniePolicyParser()
        except ImportError as e:
            logger.warning(f"ERNIE Bot parser not available: {e}")
            self.ernie_parser = None

        # Initialize traditional parser (local NLP model)
        try:
            from enhanced_parser import PolicyDocumentParser
            self.traditional_parser = PolicyDocumentParser()
        except ImportError as e:
            logger.error(f"Traditional parser not available: {e}")
            raise

    def parse_policy_document(self, document_text: str, llm_service: str = 'kimi') -> Dict:
        """
        Parse policy document using hybrid approach
        Supports multiple services: 'kimi', 'ernie', 'traditional'
        """
        if llm_service == 'kimi' and self.kimi_parser is not None:
            # Try Kimi first as requested
            try:
                logger.info("Using Kimi for policy analysis...")
                kimi_result = self.kimi_parser.parse_policy_document(document_text)
                
                # If Kimi parsing worked well, return its results
                if kimi_result.get('metadata', {}).get('title', '') != 'Kimi解析失败 - 使用本地解析':
                    # Enhance with traditional parsing elements for completeness
                    try:
                        traditional_result = self.traditional_parser.extract_structured_content(document_text)

                        # Combine results, prioritizing Kimi's accuracy but adding traditional elements
                        enhanced_result = kimi_result.copy()

                        # Add document structure from traditional parser if not available in Kimi result
                        if not enhanced_result.get('document_structure'):
                            enhanced_result['document_structure'] = traditional_result.get('sections', [])

                        # Add relationships if not available in Kimi result
                        if 'relationships' not in enhanced_result or not enhanced_result.get('relationships'):
                            enhanced_result['relationships'] = traditional_result.get('relationships', [])

                        # Add entities if not available in Kimi result
                        if 'entities' not in enhanced_result or not enhanced_result.get('entities'):
                            enhanced_result['entities'] = traditional_result.get('entities', {})

                        return enhanced_result
                    except Exception as e:
                        logger.warning(f"Traditional enhancement failed: {e}")
                        # If traditional parsing fails, return just the Kimi result
                        return kimi_result
                else:
                    logger.warning("Kimi failed, falling back to other parsers")
            except Exception as e:
                logger.warning(f"Kimi parsing failed: {e}")
        
        if llm_service == 'ernie' and self.ernie_parser is not None:
            # Try ERNIE Bot as second option
            try:
                logger.info("Using ERNIE for policy analysis...")
                ernie_result = self.ernie_parser.parse_policy_document(document_text)

                # If ERNIE Bot parsing worked well (not fallback), return its results
                if not ernie_result.get('metadata', {}).get('title', '').startswith('ERNIE Bot 解析失败'):
                    # Enhance with traditional parsing elements for completeness
                    try:
                        traditional_result = self.traditional_parser.extract_structured_content(document_text)

                        # Combine results, prioritizing ERNIE's accuracy but adding traditional elements
                        enhanced_result = ernie_result.copy()

                        # Add document structure from traditional parser if not available in ERNIE result
                        if not enhanced_result.get('document_structure'):
                            enhanced_result['document_structure'] = traditional_result.get('sections', [])

                        # Add relationships if not available in ERNIE result
                        if 'relationships' not in enhanced_result or not enhanced_result.get('relationships'):
                            enhanced_result['relationships'] = traditional_result.get('relationships', [])

                        return enhanced_result
                    except:
                        # If traditional parsing fails, return just the ERNIE result
                        return ernie_result
            except Exception as e:
                logger.warning(f"ERNIE Bot parsing failed: {e}")

        # If Kimi or ERNIE failed, use traditional parser (local NLP model)
        logger.info("Using local NLP model for policy analysis...")
        if self.traditional_parser:
            traditional_result = self.traditional_parser.extract_structured_content(document_text)
            return self._convert_traditional_to_standard_format(traditional_result, document_text)
        else:
            # Ultimate fallback
            return {
                'metadata': {
                    'title': '解析失败',
                    'issuing_authority': '未知',
                    'publication_date': '',
                    'applicable_regions': [],
                    'key_industries': []
                },
                'key_points': ['文档解析失败'],
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

    def _convert_traditional_to_standard_format(self, traditional_result: Dict, original_text: str) -> Dict:
        """Convert traditional parser results to standard format"""
        return {
            'metadata': traditional_result.get('metadata', {}),
            'document_structure': traditional_result.get('sections', []),
            'entities': traditional_result.get('entities', {}),
            'provisions': traditional_result.get('provisions', []),
            'requirements': traditional_result.get('requirements', []),
            'conditions': traditional_result.get('conditions', []),
            'quantitative_data': traditional_result.get('quantitative_data', {}),
            'timeline': traditional_result.get('timeline', []),
            'relationships': traditional_result.get('relationships', []),
            'key_points': [original_text[:500]] if original_text else ['无内容'],  # Fallback summary
            'analysis': {
                'industry_relevance': {
                    'value_chain': {
                        'upstream': traditional_result['metadata']['key_industries'][:3] if traditional_result['metadata']['key_industries'] else [],
                        'midstream': traditional_result['metadata']['key_industries'][1:4] if len(traditional_result['metadata']['key_industries']) > 1 else [],
                        'downstream': traditional_result['metadata']['key_industries'][2:5] if len(traditional_result['metadata']['key_industries']) > 2 else []
                    },
                    'related_industries': traditional_result['metadata']['key_industries']
                },
                'policy_strength': {
                    'funding_level': '中',
                    'measure_diversity': len(traditional_result.get('provisions', [])),
                    'support_comprehensiveness': '部分' if len(traditional_result.get('provisions', [])) > 0 else '未知'
                },
                'timeliness_score': 75,  # Default score
                'regional_match_score': 70  # Default score
            },
            'full_text': original_text
        }