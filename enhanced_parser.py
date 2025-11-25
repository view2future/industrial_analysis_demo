import spacy
import re
import json
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class PolicyDocumentParser:
    def __init__(self):
        # Load Chinese language model for spaCy
        try:
            self.nlp = spacy.load("zh_core_web_md")
        except OSError:
            logger.warning("Chinese spaCy model not found. Install with: python -m spacy download zh_core_web_md")
            # Fallback to basic processing if model not available
            self.nlp = None

    def extract_structured_content(self, text: str) -> Dict:
        """Extract structured information from policy document"""
        result = {
            'metadata': self.extract_metadata(text),
            'sections': self.identify_document_structure(text),
            'entities': self.extract_entities(text),
            'provisions': self.extract_policy_provisions(text),
            'requirements': self.extract_requirements(text),
            'conditions': self.extract_conditions(text),
            'quantitative_data': self.extract_quantitative_data(text),
            'timeline': self.extract_timeline_events(text),
            'relationships': self.identify_relationships(text)
        }
        return result

    def extract_metadata(self, text: str) -> Dict:
        """Extract document metadata"""
        doc = self.nlp(text[:1000]) if self.nlp else None
        
        # Title extraction
        title_match = re.search(r'(关于|关于印发|关于发布).*(政策|办法|条例|规定|意见|实施方案|指导意见|通知)', text)
        title = title_match.group(0).strip() if title_match else '未知政策标题'
        
        # Issuing authority
        authorities = []
        authority_patterns = [
            r'(?:发文机关|发布机构|发文单位|主管部门)[:：]?\s*([^\n、；；，,]+)',
            r'(?:省|市|区|县)?(?:政府|人民政府|委|局|厅|办|部|署|会)\s*(?:发布|印发|颁布|制定|公布)',
            r'(?:签发|批准)[:：]?\s*([^\n、；；，,]+)'
        ]
        
        for pattern in authority_patterns:
            matches = re.findall(pattern, text)
            authorities.extend([m.strip() for m in matches if m.strip()])
        
        # Publication date
        date_pattern = r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日|\d{4}-\d{2}-\d{2}|\d{4}/\d{2}/\d{2}'
        date_match = re.search(date_pattern, text)
        publication_date = date_match.group(0).replace('年', '-').replace('月', '-').replace('日', '') if date_match else ''
        
        # Applicable regions
        region_pattern = r'(?:适用于?|适用|覆盖|面向|针对)\s*([省市县区乡镇]+[\u4e00-\u9fa5]+\s*[省市县区乡镇]?[\u4e00-\u9fa5]*)'
        applicable_regions = list(set(re.findall(region_pattern, text)))
        
        # Key industries
        industry_pattern = r'(?:重点支持|优先发展|鼓励发展|扶持发展)\s*([^\n、；；，,，。]+)'
        key_industries = list(set([match.strip() for match in re.findall(industry_pattern, text) if match.strip()]))
        
        return {
            'title': title,
            'issuing_authority': authorities[0] if authorities else '未知',
            'publication_date': publication_date,
            'applicable_regions': applicable_regions,
            'key_industries': key_industries
        }

    def identify_document_structure(self, text: str) -> List[Dict]:
        """Identify document sections and hierarchy"""
        sections = []
        
        # Common section identifiers
        section_patterns = [
            r'(\d+\.?\d*\.?\d*)\s+([第]?[一二三四五六七八九十\d]+[章])\s*([^\n]+)',
            r'([第]?[一二三四五六七八九十\d]+[章])\s*([^\n]+)',
            r'([一二三四五六七八九十\d]+、[^\n]+)',
            r'([第]?[一二三四五六七八九十\d]+[条])\s*([^\n]+)',
            r'(?:第\s*([一二三四五六七八九十\d]+)\s*条)\s*([^\n]+)'
        ]
        
        for i, pattern in enumerate(section_patterns):
            matches = re.finditer(pattern, text)
            for match in matches:
                sections.append({
                    'level': i,
                    'identifier': match.group(1),
                    'title': match.group(2) if len(match.groups()) > 1 else '',
                    'content': match.group(0)
                })
        
        return sections

    def extract_entities(self, text: str) -> Dict:
        """Extract named entities using spaCy if available"""
        entities = {
            'organizations': [],
            'locations': [],
            'dates': [],
            'amounts': [],
            'percentages': []
        }
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'GPE', 'LOC']:
                    entities['locations' if ent.label_ in ['GPE', 'LOC'] else 'organizations'].append({
                        'text': ent.text,
                        'label': ent.label_
                    })
        
        # Extract dates using regex
        date_patterns = [
            r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{4}/\d{2}/\d{2}',
            r'(\d{4})[年]\s*第(\d{1,2})[季度]'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    date_str = '-'.join([part for part in match if part]) if any(match) else pattern
                else:
                    date_str = match
                entities['dates'].append(date_str)
        
        # Extract amounts and percentages
        amount_patterns = [
            r'([一二三四五六七八九十百千万亿\d零壹贰叁肆伍陆柒捌玖拾佰仟\d]+)(万元|万元人民币|人民币万元|元|元人民币|人民币元)',
            r'(\d+\.?\d*)\s*(%|百分点|%)'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) >= 2 and ('百分' in match[1] or '%' in match[1]):
                    entities['percentages'].append(f"{match[0]}{match[1]}")
                elif len(match) >= 2:
                    entities['amounts'].append(f"{match[0]}{match[1]}")
        
        return entities

    def extract_policy_provisions(self, text: str) -> List[Dict]:
        """Extract policy provisions and measures"""
        provisions = []
        
        # Common provision patterns
        patterns = [
            r'(?:支持|鼓励|扶持|奖励|补贴|资助)\s*([^\n、；；，,，。.]+?)(?:\s*，|\s*。|\s*；|\n)',
            r'(?:凡|对于|针对)\s*([^\n、；；，,，。.]+?)\s*(?:的\s*|，\s*)([^\n、；；，,，。.]*?)(?:可|可以|能够)\s*([^\n、；；，,，。.]*?)(?:\s*，|\s*。|\s*；|\n)',
            r'(?:符合|满足|达到)\s*([^\n、；；，,，。.]+?)\s*(?:条件|要求|标准)\s*的\s*([^\n、；；，,，。.]+?)\s*(?:可|可以|能够)\s*([^\n、；；，,，。.]*?)(?:\s*，|\s*。|\s*；|\n)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 3:
                    provisions.append({
                        'type': 'provision',
                        'condition': match[0] if match[0] else '',
                        'subject': match[1] if len(match) > 1 and match[1] else '',
                        'benefit': match[2] if len(match) > 2 and match[2] else ''
                    })
                elif isinstance(match, tuple) and len(match) > 0:
                    provisions.append({
                        'type': 'provision',
                        'description': ' '.join(match).strip()
                    })
                else:
                    provisions.append({
                        'type': 'provision',
                        'description': str(match)
                    })
        
        return provisions

    def extract_requirements(self, text: str) -> List[Dict]:
        """Extract requirements and obligations"""
        requirements = []
        
        # Requirement patterns
        req_patterns = [
            r'(?:需|需要|必须|应当|应该)\s*([^\n、；；，,，。.]+?)(?:\s*，|\s*。|\s*；|\n)',
            r'(?:要求|规定|规定要求)\s*([^\n、；；，,，。.]+?)(?:\s*，|\s*。|\s*；|\n)',
            r'(?:([^、；；，,，。.]*)?(不得|禁止|严禁)\s*([^\n、；；，,，。.]*?))'
        ]
        
        for pattern in req_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2 and match[1]:  # Has prohibition keyword
                    requirements.append({
                        'requirement': f"{match[0]}{match[1]}{match[2]}" if match[0] else f"{match[1]}{match[2]}",
                        'type': 'negative'
                    })
                elif isinstance(match, tuple) and len(match) > 0:
                    requirements.append({
                        'requirement': match[0],
                        'type': 'positive'
                    })
                else:
                    requirements.append({
                        'requirement': str(match),
                        'type': 'positive'
                    })
        
        return requirements

    def extract_conditions(self, text: str) -> List[Dict]:
        """Extract conditional statements"""
        conditions = []
        
        # Conditional patterns (if-then, when-then, upon-then)
        cond_patterns = [
            r'(?:当|当且仅当|若|如果|如|如果.*?则|若.*?则|一旦|在.*?情况下)\s*([^\n、；；，,，。.]*?)(?:，|，\s*|，\s*则\s*)\s*([^\n、；；，,，。.]*)',
            r'(?:对于|对于.*?的|针对.*?的)\s*([^\n、；；，,，。.]*)\s*(?:，\s*)?([^\n、；；，,，。.]*)',
        ]
        
        for pattern in cond_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    conditions.append({
                        'condition': match[0],
                        'result': match[1]
                    })
        
        return conditions

    def extract_quantitative_data(self, text: str) -> Dict:
        """Extract specific quantitative values and thresholds"""
        quantitative = {
            'thresholds': [],
            'ratios': [],
            'amounts': [],
            'time_periods': []
        }
        
        # Extract thresholds
        threshold_patterns = [
            r'(?:不少于|不低于|不得低于|不少于于|不得少于)\s*([^\n、；；，,，。.]*?)(?:\s*，|\s*。|\s*；|\n)',
            r'(?:不超过|不得高于|不超过于|不得多于)\s*([^\n、；；，,，。.]*?)(?:\s*，|\s*。|\s*；|\n)',
            r'(?:达到|实现|确保达到)\s*([^\n、；；，,，。.]*?)(?:\s*，|\s*。|\s*；|\n)'
        ]
        
        for pattern in threshold_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match.strip():
                    quantitative['thresholds'].append(match)
        
        # Extract ratios/percentages
        ratio_patterns = [
            r'([一二三四五六七八九十百千万\d零壹贰叁肆伍陆柒捌玖拾佰仟\d]+)(?:[％%]|百分点|%)',
            r'(?:占比|比例|份额|比重)\s*(?:为|达到|占)\s*([^\n、；；，,，。.]*?)(?:\s*，|\s*。|\s*；|\n)'
        ]
        
        for pattern in ratio_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match and (isinstance(match, str) or (isinstance(match, tuple) and match[0])):
                    value = match if isinstance(match, str) else match[0]
                    quantitative['ratios'].append(value)
        
        return quantitative

    def extract_timeline_events(self, text: str) -> List[Dict]:
        """Extract timeline events and deadlines"""
        timeline = []
        
        timeline_patterns = [
            r'(?:自|从)\s*(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2})\s*(?:起|开始)\s*([^\n、；；，,，。.]*)',
            r'(?:截止日期|有效期至|申报时间|办理期限|到期日|截至|截至日期)\s*(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2})',
            r'([^\n、；；，,，。.]*)\s*(?:于|在)\s*(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2})\s*(?:进行|执行|实施|完成)',
            r'(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2})\s*(?:为|作为|是)\s*([^\n、；；，,，。.]*)'
        ]
        
        for pattern in timeline_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    timeline.append({
                        'date': match[0],
                        'event': match[1] if match[1] else '事件',
                        'type': 'deadline' if any(keyword in match[1] for keyword in ['截止', '截至', '截至日期', '截止日期']) else 'event'
                    })
        
        return timeline

    def identify_relationships(self, text: str) -> List[Dict]:
        """Identify relationships between different parts of the document"""
        relationships = []
        
        # Relationship patterns
        relationship_patterns = [
            r'(?:与|同|和)\s*([^\n、；；，,，。.]*)\s*(?:相关|有关|相联系|相互影响)',
            r'([^\n、；；，,，。.]*)\s*(?:促进|带动|推动|支持)\s*([^\n、；；，,，。.]*)',
            r'([^\n、；；，,，。.]*)\s*(?:基于|依托|依靠)\s*([^\n、；；，,，。.]*)',
            r'([^\n、；；，,，。.]*)\s*(?:通过|经由|借助)\s*([^\n、；；，,，。.]*)\s*(?:实现|完成|达成)'
        ]
        
        for pattern in relationship_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    relationships.append({
                        'from_entity': match[0],
                        'to_entity': match[1],
                        'relationship': 'related' if any(kw in text for kw in ['相关', '有关', '相联系', '相互影响']) else
                                    'promotes' if '促进' in text else
                                    'based_on' if '基于' in text else 'achieved_through'
                    })
        
        return relationships