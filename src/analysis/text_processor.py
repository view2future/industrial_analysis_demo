"""
Text Processing Module for Regional Industrial Analysis
Handles text extraction, categorization, and content analysis.
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

import jieba
import jieba.posseg as pseg
from docx import Document
from PyPDF2 import PdfReader
import pandas as pd

logger = logging.getLogger(__name__)

class TextProcessor:
    """Process and analyze regional industrial text data."""
    
    def __init__(self, config_path: str = 'config.json'):
        """Initialize text processor with configuration."""
        self.config_path = config_path
        self.config = self._load_config()
        self.categories = self.config.get('categories', [])
        self.ai_focus = self.config.get('ai_integration_focus', [])
        
        # Initialize jieba for Chinese text processing
        jieba.initialize()
        
        # Load custom dictionaries for industry terms
        self._load_custom_dictionaries()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "categories": [
                "产业概述", "政策环境", "市场规模", "重点企业",
                "技术趋势", "发展机遇", "挑战风险", "未来展望"
            ],
            "ai_integration_focus": [
                "智能制造", "数据分析", "自动化流程", "预测性维护",
                "供应链优化", "客户服务", "质量控制"
            ]
        }
    
    def _load_custom_dictionaries(self):
        """Load custom dictionaries for better Chinese text processing."""
        # Add common industry terms
        industry_terms = [
            "人工智能", "机器学习", "深度学习", "大数据", "云计算",
            "物联网", "区块链", "5G", "工业4.0", "智能制造",
            "数字化转型", "智慧城市", "新基建", "产业链", "供应链",
            "创新驱动", "科技赋能", "数字经济", "平台经济", "共享经济"
        ]
        
        for term in industry_terms:
            jieba.add_word(term)
    
    def analyze_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a file and extract categorized content."""
        try:
            # Read file content
            content = self._read_file(file_path)
            if not content:
                logger.error(f"Failed to read content from {file_path}")
                return None
            
            # Perform analysis
            analysis_result = self._analyze_text(content)
            analysis_result['metadata'] = {
                'source_file': os.path.basename(file_path),
                'processed_at': pd.Timestamp.now().isoformat(),
                'word_count': len(content),
                'categories_found': len([cat for cat in analysis_result['categories'] if analysis_result['categories'][cat]['content']])
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return None
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """Read content from different file types."""
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Extract text content from JSON structure
                    return self._extract_text_from_json(data)
            
            elif file_ext == '.docx':
                try:
                    from docx import Document
                    doc = Document(file_path)
                    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                except ImportError:
                    logger.error("python-docx library not installed. Cannot process DOCX files.")
                    return None
                except Exception as e:
                    logger.error(f"Error processing DOCX file {file_path}: {e}")
                    return None
            
            elif file_ext == '.pdf':
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(file_path)
                    text = ''
                    for page in reader.pages:
                        text += page.extract_text() + '\n'
                    return text
                except ImportError:
                    logger.error("PyPDF2 library not installed. Cannot process PDF files.")
                    return None
                except Exception as e:
                    logger.error(f"Error processing PDF file {file_path}: {e}")
                    return None
            
            else:
                logger.error(f"Unsupported file type: {file_ext}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def _extract_text_from_json(self, data: Any) -> str:
        """Extract text content from JSON data."""
        text_parts = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    text_parts.append(f"{key}: {value}")
                elif isinstance(value, (list, dict)):
                    text_parts.append(self._extract_text_from_json(value))
        
        elif isinstance(data, list):
            for item in data:
                text_parts.append(self._extract_text_from_json(item))
        
        elif isinstance(data, str):
            text_parts.append(data)
        
        return '\n'.join(filter(None, text_parts))
    
    def _analyze_text(self, content: str) -> Dict[str, Any]:
        """Analyze text content and categorize information."""
        # Clean and prepare text
        clean_content = self._clean_text(content)
        
        # Segment text into sentences/paragraphs
        segments = self._segment_text(clean_content)
        
        # Categorize content
        categorized_content = self._categorize_content(segments)
        
        # Extract key information
        key_insights = self._extract_key_insights(clean_content)
        
        # Analyze AI integration opportunities
        ai_opportunities = self._analyze_ai_integration(clean_content)
        
        # Generate summary statistics
        stats = self._generate_statistics(clean_content, segments)
        
        # 添加情感分析
        sentiment_analysis = self._analyze_sentiment(clean_content)
        
        return {
            'categories': categorized_content,
            'key_insights': key_insights,
            'ai_opportunities': ai_opportunities,
            'statistics': stats,
            'sentiment_analysis': sentiment_analysis,
            'original_text_length': len(content),
            'processed_segments': len(segments)
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Chinese punctuation
        text = re.sub(r'[^\w\s\u4e00-\u9fff。，、；：？！""''（）【】《》〈〉]', ' ', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[。，]{2,}', '。', text)
        
        return text.strip()
    
    def _segment_text(self, text: str) -> List[str]:
        """Segment text into meaningful chunks."""
        # Split by sentences and paragraphs
        segments = []
        
        # First split by paragraphs
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Split long paragraphs by sentences
            sentences = re.split(r'[。！？]', paragraph)
            
            current_segment = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # If adding this sentence makes segment too long, save current segment
                if len(current_segment + sentence) > 200:
                    if current_segment:
                        segments.append(current_segment.strip())
                    current_segment = sentence
                else:
                    current_segment += sentence + "。"
            
            if current_segment:
                segments.append(current_segment.strip())
        
        return [seg for seg in segments if len(seg) > 20]  # Filter out very short segments
    
    def _categorize_content(self, segments: List[str]) -> Dict[str, Dict[str, Any]]:
        """Categorize text segments into predefined categories."""
        categorized = {}
        
        # Define category keywords
        category_keywords = {
            "产业概述": ["产业", "行业", "概述", "介绍", "背景", "现状", "发展历程", "规模"],
            "政策环境": ["政策", "政府", "法规", "支持", "扶持", "规划", "战略", "指导意见"],
            "市场规模": ["市场", "规模", "增长", "收入", "产值", "份额", "预测", "趋势"],
            "重点企业": ["企业", "公司", "厂商", "品牌", "龙头", "领军", "代表性", "知名"],
            "技术趋势": ["技术", "创新", "研发", "突破", "先进", "前沿", "升级", "改进"],
            "发展机遇": ["机遇", "机会", "优势", "潜力", "前景", "增长点", "新兴", "蓝海"],
            "挑战风险": ["挑战", "风险", "困难", "问题", "瓶颈", "威胁", "竞争", "压力"],
            "未来展望": ["未来", "展望", "预期", "预测", "目标", "规划", "愿景", "前景"]
        }
        
        for category in self.categories:
            categorized[category] = {
                'content': [],
                'key_points': [],
                'relevance_score': 0
            }
            
            keywords = category_keywords.get(category, [category])
            
            for segment in segments:
                # Calculate relevance score based on keyword matches
                score = 0
                for keyword in keywords:
                    score += segment.count(keyword) * 2
                    # Also check for partial matches in segmented words
                    words = jieba.lcut(segment)
                    for word in words:
                        if keyword in word or word in keyword:
                            score += 1
                
                # If segment is relevant to this category
                if score > 0:
                    categorized[category]['content'].append({
                        'text': segment,
                        'score': score
                    })
                    categorized[category]['relevance_score'] += score
            
            # Sort content by relevance score and extract key points
            categorized[category]['content'].sort(key=lambda x: x['score'], reverse=True)
            
            # Extract top key points
            if categorized[category]['content']:
                categorized[category]['key_points'] = [
                    item['text'][:100] + "..." if len(item['text']) > 100 else item['text']
                    for item in categorized[category]['content'][:3]
                ]
        
        return categorized
    
    def _extract_key_insights(self, content: str) -> List[Dict[str, Any]]:
        """Extract key insights from the content."""
        insights = []
        
        # Use jieba to extract key phrases
        words = pseg.cut(content)
        
        # Count important terms
        important_terms = {}
        for word, flag in words:
            # Focus on nouns, adjectives, and verbs
            if flag in ['n', 'nr', 'ns', 'nt', 'nz', 'a', 'ad', 'v', 'vn'] and len(word) > 1:
                important_terms[word] = important_terms.get(word, 0) + 1
        
        # Get top terms
        top_terms = sorted(important_terms.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Look for numerical data and trends with context
        numerical_insights = self._extract_numerical_insights(content)
        
        # 添加词性分析结果
        
        insights.append({'type': 'top_keywords',
            'title': '关键词分析',
            'data': [{'term': term, 'frequency': freq} for term, freq in top_terms[:10]]
        })
        
        if numerical_insights:
            insights.append({
                'type': 'numerical_data',
                'title': '数据要点',
                'data': numerical_insights[:10]
            })

        return insights
        
    def _analyze_part_of_speech(self, content: str) -> List[Dict[str, Any]]:
        return insights
        """Analyze part of speech distribution in the content.
        
        Args:
            content: Text content to analyze
            
        Returns:
            List of POS distribution data
        """
        try:
            # 使用jieba进行词性标注
            words = pseg.cut(content)
            
            # 统计词性分布
            pos_count = {}
            for word, flag in words:
                if len(word) > 1:  # 过滤单字符
                    pos_count[flag] = pos_count.get(flag, 0) + 1
            
            # 定义中文词性标签映射
            pos_mapping = {
                'n': '名词', 'nr': '人名', 'ns': '地名', 'nt': '机构团体',
                'nz': '其他专名', 'v': '动词', 'vd': '副动词', 'vn': '名动词',
                'a': '形容词', 'ad': '副形词', 'an': '名形词', 'd': '副词',
                'm': '数词', 'q': '量词', 'r': '代词', 'p': '介词',
                'c': '连词', 'u': '助词', 'xc': '其他虚词', 'w': '标点符号'
            }
            
            # 构建结果数据
            pos_data = []
            for flag, count in sorted(pos_count.items(), key=lambda x: x[1], reverse=True)[:10]:
                pos_data.append({
                    'pos_tag': flag,
                    'pos_name': pos_mapping.get(flag, flag),
                    'count': count,
                    'percentage': round(count / sum(pos_count.values()) * 100, 2)
                })
            
            return pos_data
            
        except Exception as e:
            logger.error(f"词性分析失败: {e}")
            return []
    
    def _analyze_ai_integration(self, content: str) -> Dict[str, Any]:
        """Analyze potential AI integration opportunities."""
        ai_keywords = {
            "智能制造": ["制造", "生产", "工厂", "设备", "自动化"],
            "数据分析": ["数据", "分析", "统计", "洞察", "预测"],
            "自动化流程": ["流程", "自动", "效率", "优化", "简化"],
            "预测性维护": ["维护", "保养", "故障", "检修", "监控"],
            "供应链优化": ["供应链", "物流", "库存", "采购", "配送"],
            "客户服务": ["客户", "服务", "体验", "满意", "支持"],
            "质量控制": ["质量", "检测", "控制", "标准", "合规"]
        }
        
        opportunities = {}
        
        for ai_area, keywords in ai_keywords.items():
            score = 0
            relevant_segments = []
            
            for keyword in keywords:
                matches = len(re.findall(keyword, content))
                score += matches
                
                # Find sentences containing these keywords
                sentences = re.split(r'[。！？]', content)
                for sentence in sentences:
                    if keyword in sentence and len(sentence.strip()) > 10:
                        relevant_segments.append(sentence.strip())
            
            if score > 0:
                opportunities[ai_area] = {
                    'potential_score': min(score * 10, 100),  # Normalize to 0-100
                    'relevant_content': list(set(relevant_segments))[:3],  # Remove duplicates, limit to 3
                    'recommendation': self._generate_ai_recommendation(ai_area, score)
                }
        
        return opportunities
    
    def _extract_numerical_insights(self, content: str) -> List[Dict[str, str]]:
        """Extract numerical data with context labels."""
        insights = []
        
        # Find numbers with their surrounding context (10-20 chars before)
        import re
        pattern = r'(.{0,20})(\d+(?:\.\d+)?[%万亿元美元年月人家项个])'
        matches = re.findall(pattern, content)
        
        for context, number in matches:
            # Clean context - keep Chinese chars, letters, and spaces
            clean_context = re.sub(r'[^\w\s\u4e00-\u9fff]', '', context).strip()
            if clean_context:
                # Get last few words as label
                words = clean_context.split()
                label = words[-3:] if len(words) >= 3 else words
                insights.append({
                    'label': ' '.join(label),
                    'value': number
                })
        
        # Deduplicate based on value
        seen = set()
        unique_insights = []
        for insight in insights:
            if insight['value'] not in seen:
                seen.add(insight['value'])
                unique_insights.append(insight)
        
        return unique_insights
    
    def _generate_ai_recommendation(self, ai_area: str, score: int) -> str:
        """Generate AI integration recommendations."""
        recommendations = {
            "智能制造": "考虑引入智能制造系统，通过物联网和机器学习优化生产流程",
            "数据分析": "建立数据分析平台，利用大数据和AI技术提供商业洞察",
            "自动化流程": "实施流程自动化，使用RPA和AI减少人工操作",
            "预测性维护": "部署预测性维护系统，利用传感器数据和机器学习预防设备故障",
            "供应链优化": "优化供应链管理，使用AI算法改进需求预测和库存管理",
            "客户服务": "升级客户服务体系，引入智能客服和个性化推荐系统",
            "质量控制": "强化质量控制，利用计算机视觉和机器学习自动检测产品质量"
        }
        
        base_recommendation = recommendations.get(ai_area, f"在{ai_area}领域引入AI技术")
        
        if score >= 5:
            return f"高优先级：{base_recommendation}，该领域在文档中被频繁提及"
        elif score >= 3:
            return f"中等优先级：{base_recommendation}，具有一定的应用基础"
        else:
            return f"潜在机会：{base_recommendation}，可以作为未来发展方向"
    
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of the content using SnowNLP.
        
        Args:
            content: Text content to analyze
            
        Returns:
            Sentiment analysis results
        """
        try:
            from snownlp import SnowNLP
            
            # 分段进行情感分析
            segments = self._segment_text(content)
            
            # 计算整体情感分数
            sentiment_scores = []
            positive_segments = 0
            negative_segments = 0
            
            for segment in segments:
                if len(segment.strip()) > 10:  # 只分析较长的段落
                    s = SnowNLP(segment)
                    score = s.sentiments
                    sentiment_scores.append(score)
                    
                    if score > 0.6:
                        positive_segments += 1
                    elif score < 0.4:
                        negative_segments += 1
            
            # 计算平均情感分数
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.5
            
            # 确定整体情感倾向
            if avg_sentiment > 0.6:
                overall_sentiment = "积极"
            elif avg_sentiment < 0.4:
                overall_sentiment = "消极"
            else:
                overall_sentiment = "中性"
            
            return {
                'overall_sentiment': overall_sentiment,
                'average_score': round(avg_sentiment, 3),
                'positive_segments': positive_segments,
                'negative_segments': negative_segments,
                'total_segments': len(sentiment_scores),
                'confidence': round(1 - abs(0.5 - avg_sentiment) * 2, 3)
            }
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {
                'overall_sentiment': '未知',
                'average_score': 0.5,
                'positive_segments': 0,
                'negative_segments': 0,
                'total_segments': 0,
                'confidence': 0.0
            }
    
    def _generate_statistics(self, content: str, segments: List[str]) -> Dict[str, Any]:
        """Generate content statistics."""
        word_count = len(jieba.lcut(content))
        
        # Character and word statistics
        stats = {
            'total_characters': len(content),
            'total_words': word_count,
            'total_segments': len(segments),
            'avg_segment_length': sum(len(seg) for seg in segments) // len(segments) if segments else 0,
            'reading_time_minutes': max(1, word_count // 300),  # Approximate reading time
            'unique_words': len(set(jieba.lcut(content)))  # Unique word count
        }
        
        return stats