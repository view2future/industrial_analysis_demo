#!/usr/bin/env python3
"""
Entity Extraction Module
Extract named entities from Chinese text (enterprises, people, locations, technologies, products)
"""

import re
import logging
import jieba
import jieba.posseg as pseg
from typing import Dict, List, Set
from collections import Counter

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extract named entities from Chinese text."""
    
    def __init__(self):
        """Initialize entity extractor."""
        # Common entity patterns
        self.company_suffixes = ['公司', '集团', '企业', '科技', '有限公司', '股份', 
                                '实业', '投资', '控股', '集团公司']
        
        self.tech_keywords = ['人工智能', 'AI', '大数据', '云计算', '物联网', '5G', 
                            '区块链', '机器学习', '深度学习', '算法', '芯片', 
                            '半导体', '新能源', '智能制造', '工业互联网']
        
        self.product_keywords = ['平台', '系统', '软件', '硬件', '设备', '产品', 
                               '解决方案', '服务', '应用']
        
        # Location indicators
        self.location_indicators = ['市', '省', '区', '县', '镇', '街道', '园区', 
                                   '开发区', '高新区', '经济区']
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict]]:
        """Extract all types of entities from text.
        
        Args:
            text: Input text
        
        Returns:
            Dictionary containing different types of entities
        """
        try:
            entities = {
                'companies': self._extract_companies(text),
                'persons': self._extract_persons(text),
                'locations': self._extract_locations(text),
                'technologies': self._extract_technologies(text),
                'products': self._extract_products(text)
            }
            
            # Add statistics
            entities['statistics'] = {
                'total_entities': sum(len(v) for v in entities.values() if isinstance(v, list)),
                'companies_count': len(entities['companies']),
                'persons_count': len(entities['persons']),
                'locations_count': len(entities['locations']),
                'technologies_count': len(entities['technologies']),
                'products_count': len(entities['products'])
            }
            
            return entities
        
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return self._get_empty_entities()
    
    def _extract_companies(self, text: str) -> List[Dict]:
        """Extract company names."""
        companies = []
        seen = set()
        
        # Pattern 1: Chinese characters + company suffix
        for suffix in self.company_suffixes:
            pattern = r'[\u4e00-\u9fa5]{2,20}' + suffix
            matches = re.finditer(pattern, text)
            for match in matches:
                company = match.group()
                if company not in seen and len(company) >= 4:
                    seen.add(company)
                    companies.append({
                        'name': company,
                        'type': 'company',
                        'position': match.start(),
                        'confidence': 0.9
                    })
        
        # Pattern 2: Famous companies (simple matching)
        famous_companies = ['百度', '阿里巴巴', '腾讯', '华为', '小米', '字节跳动',
                           '美团', '京东', '滴滴', '蚂蚁', '商汤', '旷视']
        for company in famous_companies:
            if company in text and company not in seen:
                seen.add(company)
                companies.append({
                    'name': company,
                    'type': 'company',
                    'position': text.find(company),
                    'confidence': 1.0
                })
        
        return sorted(companies, key=lambda x: x['position'])
    
    def _extract_persons(self, text: str) -> List[Dict]:
        """Extract person names."""
        persons = []
        seen = set()
        
        # Use jieba POS tagging
        words = pseg.cut(text)
        
        for word, flag in words:
            # 'nr' is the POS tag for person names in jieba
            if flag == 'nr' and len(word) >= 2:
                if word not in seen:
                    seen.add(word)
                    persons.append({
                        'name': word,
                        'type': 'person',
                        'confidence': 0.8
                    })
        
        return persons
    
    def _extract_locations(self, text: str) -> List[Dict]:
        """Extract location names."""
        locations = []
        seen = set()
        
        # Use jieba POS tagging
        words = pseg.cut(text)
        
        for word, flag in words:
            # 'ns' is the POS tag for location names
            if flag == 'ns' and len(word) >= 2:
                if word not in seen:
                    seen.add(word)
                    locations.append({
                        'name': word,
                        'type': 'location',
                        'confidence': 0.85
                    })
        
        # Also check for location indicators
        for indicator in self.location_indicators:
            pattern = r'[\u4e00-\u9fa5]{2,10}' + indicator
            matches = re.finditer(pattern, text)
            for match in matches:
                location = match.group()
                if location not in seen and len(location) >= 3:
                    seen.add(location)
                    locations.append({
                        'name': location,
                        'type': 'location',
                        'confidence': 0.9
                    })
        
        return locations
    
    def _extract_technologies(self, text: str) -> List[Dict]:
        """Extract technology terms."""
        technologies = []
        seen = set()
        
        for tech in self.tech_keywords:
            if tech in text and tech not in seen:
                seen.add(tech)
                # Count occurrences for importance
                count = text.count(tech)
                technologies.append({
                    'name': tech,
                    'type': 'technology',
                    'count': count,
                    'confidence': 1.0
                })
        
        return sorted(technologies, key=lambda x: x['count'], reverse=True)
    
    def _extract_products(self, text: str) -> List[Dict]:
        """Extract product/service names."""
        products = []
        seen = set()
        
        # Pattern: tech keyword + product keyword
        for tech in self.tech_keywords:
            for prod in self.product_keywords:
                pattern = tech + '.*?' + prod
                matches = re.finditer(pattern, text)
                for match in matches:
                    product = match.group()
                    if product not in seen and len(product) <= 30:
                        seen.add(product)
                        products.append({
                            'name': product,
                            'type': 'product',
                            'confidence': 0.7
                        })
        
        return products
    
    def build_entity_graph(self, entities: Dict) -> Dict:
        """Build entity relationship graph.
        
        Args:
            entities: Extracted entities
        
        Returns:
            Graph structure for visualization
        """
        nodes = []
        links = []
        node_id = 0
        entity_to_id = {}
        
        # Create nodes
        for entity_type, entity_list in entities.items():
            if entity_type == 'statistics':
                continue
            
            for entity in entity_list:
                entity_name = entity.get('name', '')
                if entity_name and entity_name not in entity_to_id:
                    nodes.append({
                        'id': node_id,
                        'name': entity_name,
                        'type': entity_type[:-1],  # Remove 's' from plural
                        'symbolSize': 20 + entity.get('count', 0) * 5,
                        'category': entity_type
                    })
                    entity_to_id[entity_name] = node_id
                    node_id += 1
        
        # Create links based on co-occurrence (simplified)
        # In a real implementation, you'd analyze context and relationships
        
        return {
            'nodes': nodes,
            'links': links,
            'categories': [
                {'name': 'companies'},
                {'name': 'persons'},
                {'name': 'locations'},
                {'name': 'technologies'},
                {'name': 'products'}
            ]
        }
    
    def _get_empty_entities(self) -> Dict:
        """Return empty entities structure."""
        return {
            'companies': [],
            'persons': [],
            'locations': [],
            'technologies': [],
            'products': [],
            'statistics': {
                'total_entities': 0,
                'companies_count': 0,
                'persons_count': 0,
                'locations_count': 0,
                'technologies_count': 0,
                'products_count': 0
            }
        }
