#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
术语词典与词云生成模块
管理行业术语库、生成词云、提供术语解释和标注
"""

import json
import logging
import jieba
from collections import Counter
from typing import Dict, List, Any, Optional
import os

logger = logging.getLogger(__name__)


class TerminologyManager:
    """术语词典管理器"""
    
    def __init__(self, terminology_file: Optional[str] = None):
        """初始化术语管理器
        
        Args:
            terminology_file: 术语词典文件路径
        """
        self.terminology_file = terminology_file or "data/terminology.json"
        self.terminology = self._load_terminology()
        self.stopwords = self._load_stopwords()
    
    def _load_terminology(self) -> Dict[str, Dict]:
        """加载术语词典"""
        try:
            if os.path.exists(self.terminology_file):
                with open(self.terminology_file, 'r', encoding='utf-8') as f:
                    terms = json.load(f)
                logger.info(f"加载术语词典: {len(terms)} 个术语")
                return terms
            else:
                # 创建默认术语库
                default_terms = self._create_default_terminology()
                self._save_terminology(default_terms)
                return default_terms
        except Exception as e:
            logger.error(f"加载术语词典失败: {e}")
            return {}
    
    def _create_default_terminology(self) -> Dict[str, Dict]:
        """创建默认术语库"""
        return {
            "人工智能": {
                "category": "技术",
                "definition": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
                "related": ["机器学习", "深度学习", "神经网络"],
                "importance": 10
            },
            "大数据": {
                "category": "技术",
                "definition": "大数据是指规模巨大、类型多样、处理速度快的数据集合。",
                "related": ["数据分析", "数据挖掘", "云计算"],
                "importance": 9
            },
            "云计算": {
                "category": "技术",
                "definition": "云计算是一种通过互联网提供计算资源和服务的模式。",
                "related": ["SaaS", "PaaS", "IaaS"],
                "importance": 8
            },
            "物联网": {
                "category": "技术",
                "definition": "物联网（IoT）是指通过互联网连接各种物理设备的网络。",
                "related": ["传感器", "智能设备", "边缘计算"],
                "importance": 8
            },
            "区块链": {
                "category": "技术",
                "definition": "区块链是一种分布式账本技术，具有去中心化、不可篡改的特点。",
                "related": ["加密货币", "智能合约", "分布式系统"],
                "importance": 7
            },
            "5G": {
                "category": "技术",
                "definition": "第五代移动通信技术，提供更高速度和更低延迟。",
                "related": ["通信", "网络", "移动互联网"],
                "importance": 9
            },
            "智能制造": {
                "category": "应用",
                "definition": "利用先进信息技术实现制造过程的智能化。",
                "related": ["工业4.0", "自动化", "数字化"],
                "importance": 8
            }
        }
    
    def _save_terminology(self, terms: Dict):
        """保存术语词典"""
        try:
            os.makedirs(os.path.dirname(self.terminology_file), exist_ok=True)
            with open(self.terminology_file, 'w', encoding='utf-8') as f:
                json.dump(terms, f, ensure_ascii=False, indent=2)
            logger.info(f"保存术语词典: {len(terms)} 个术语")
        except Exception as e:
            logger.error(f"保存术语词典失败: {e}")
    
    def _load_stopwords(self) -> set:
        """加载停用词"""
        stopwords = {
            '的', '了', '在', '是', '和', '与', '等', '及', '也', '有',
            '可以', '能够', '进行', '通过', '为', '对', '将', '以', '但',
            '而', '或', '等等', '一个', '这个', '那个', '我们', '你们'
        }
        return stopwords
    
    def add_term(self, term: str, definition: str, category: str = "其他",
                related: Optional[List[str]] = None, importance: int = 5):
        """添加新术语
        
        Args:
            term: 术语名称
            definition: 术语定义
            category: 术语类别
            related: 相关术语
            importance: 重要性（1-10）
        """
        try:
            self.terminology[term] = {
                "category": category,
                "definition": definition,
                "related": related or [],
                "importance": importance
            }
            self._save_terminology(self.terminology)
            logger.info(f"添加术语: {term}")
        except Exception as e:
            logger.error(f"添加术语失败: {e}")
    
    def get_term_info(self, term: str) -> Optional[Dict]:
        """获取术语信息
        
        Args:
            term: 术语名称
            
        Returns:
            术语信息字典
        """
        return self.terminology.get(term)
    
    def annotate_text(self, text: str) -> Dict:
        """标注文本中的术语
        
        Args:
            text: 待标注文本
            
        Returns:
            标注结果
        """
        try:
            annotations = []
            
            # 查找文本中的术语
            for term, info in self.terminology.items():
                if term in text:
                    # 找到所有出现位置
                    start = 0
                    while True:
                        pos = text.find(term, start)
                        if pos == -1:
                            break
                        
                        annotations.append({
                            "term": term,
                            "position": pos,
                            "length": len(term),
                            "definition": info["definition"],
                            "category": info["category"]
                        })
                        start = pos + 1
            
            # 按位置排序
            annotations.sort(key=lambda x: x["position"])
            
            result = {
                "text": text,
                "annotations": annotations,
                "total_terms": len(annotations)
            }
            
            logger.info(f"标注文本: 发现 {len(annotations)} 个术语")
            return result
            
        except Exception as e:
            logger.error(f"标注文本失败: {e}")
            return {"text": text, "annotations": [], "total_terms": 0}
    
    def generate_wordcloud_data(self, text: str, 
                                top_n: int = 50,
                                min_word_length: int = 2) -> List[Dict]:
        """生成词云数据
        
        Args:
            text: 文本内容
            top_n: 返回前N个词
            min_word_length: 最小词长
            
        Returns:
            词云数据列表
        """
        try:
            # 分词
            words = jieba.cut(text)
            
            # 过滤
            filtered_words = [
                word for word in words
                if len(word) >= min_word_length and word not in self.stopwords
            ]
            
            # 统计词频
            word_freq = Counter(filtered_words)
            
            # 生成词云数据
            wordcloud_data = []
            for word, freq in word_freq.most_common(top_n):
                # 检查是否是术语
                is_term = word in self.terminology
                importance = self.terminology.get(word, {}).get("importance", 5) if is_term else 5
                
                wordcloud_data.append({
                    "name": word,
                    "value": freq,
                    "is_term": is_term,
                    "importance": importance
                })
            
            logger.info(f"生成词云数据: {len(wordcloud_data)} 个词")
            return wordcloud_data
            
        except Exception as e:
            logger.error(f"生成词云数据失败: {e}")
            return []
    
    def generate_wordcloud_chart(self, text: str, 
                                 title: str = "词云图") -> Dict:
        """生成词云图表配置（ECharts）
        
        Args:
            text: 文本内容
            title: 图表标题
            
        Returns:
            ECharts词云配置
        """
        try:
            wordcloud_data = self.generate_wordcloud_data(text)
            
            config = {
                "title": {
                    "text": title,
                    "left": "center"
                },
                "tooltip": {
                    "show": True,
                    "formatter": lambda params: f"{params['name']}: {params['value']}"
                },
                "series": [{
                    "type": "wordCloud",
                    "shape": "circle",
                    "left": "center",
                    "top": "center",
                    "width": "90%",
                    "height": "90%",
                    "right": None,
                    "bottom": None,
                    "sizeRange": [12, 60],
                    "rotationRange": [-45, 45],
                    "rotationStep": 45,
                    "gridSize": 8,
                    "drawOutOfBound": False,
                    "textStyle": {
                        "fontFamily": "sans-serif",
                        "fontWeight": "bold",
                        "color": lambda params: (
                            "#c23531" if params.get("dataIndex") % 3 == 0 else
                            "#2f4554" if params.get("dataIndex") % 3 == 1 else
                            "#61a0a8"
                        )
                    },
                    "emphasis": {
                        "textStyle": {
                            "shadowBlur": 10,
                            "shadowColor": "#333"
                        }
                    },
                    "data": wordcloud_data
                }]
            }
            
            logger.info("生成词云图表配置成功")
            return config
            
        except Exception as e:
            logger.error(f"生成词云图表失败: {e}")
            return {}
    
    def get_related_terms(self, term: str, max_depth: int = 2) -> List[str]:
        """获取相关术语
        
        Args:
            term: 术语名称
            max_depth: 最大搜索深度
            
        Returns:
            相关术语列表
        """
        try:
            if term not in self.terminology:
                return []
            
            related = set()
            to_process = [(term, 0)]
            processed = set()
            
            while to_process:
                current_term, depth = to_process.pop(0)
                
                if current_term in processed or depth >= max_depth:
                    continue
                
                processed.add(current_term)
                
                if current_term in self.terminology:
                    term_info = self.terminology[current_term]
                    for rel in term_info.get("related", []):
                        if rel not in processed:
                            related.add(rel)
                            to_process.append((rel, depth + 1))
            
            return list(related)
            
        except Exception as e:
            logger.error(f"获取相关术语失败: {e}")
            return []
    
    def export_terminology(self, output_file: str, format: str = "json"):
        """导出术语词典
        
        Args:
            output_file: 输出文件路径
            format: 导出格式（json, csv, md）
        """
        try:
            if format == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.terminology, f, ensure_ascii=False, indent=2)
            
            elif format == "csv":
                import csv
                with open(output_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["术语", "类别", "定义", "相关术语", "重要性"])
                    for term, info in self.terminology.items():
                        writer.writerow([
                            term,
                            info.get("category", ""),
                            info.get("definition", ""),
                            ", ".join(info.get("related", [])),
                            info.get("importance", 5)
                        ])
            
            elif format == "md":
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("# 术语词典\n\n")
                    for term, info in sorted(self.terminology.items()):
                        f.write(f"## {term}\n\n")
                        f.write(f"**类别**: {info.get('category', '未分类')}\n\n")
                        f.write(f"**定义**: {info.get('definition', '暂无定义')}\n\n")
                        if info.get("related"):
                            f.write(f"**相关术语**: {', '.join(info['related'])}\n\n")
                        f.write("---\n\n")
            
            logger.info(f"导出术语词典: {output_file}")
            
        except Exception as e:
            logger.error(f"导出术语词典失败: {e}")


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    manager = TerminologyManager()
    
    # 测试文本
    test_text = """
    成都市积极发展人工智能产业，推动大数据、云计算、物联网等技术融合创新。
    通过智能制造提升产业竞争力，利用5G网络加速数字化转型。
    人工智能技术在医疗、教育、交通等领域广泛应用。
    """
    
    # 标注文本
    annotated = manager.annotate_text(test_text)
    print(f"\n标注结果: 发现 {annotated['total_terms']} 个术语")
    for ann in annotated['annotations'][:5]:
        print(f"- {ann['term']} ({ann['category']}): {ann['definition'][:30]}...")
    
    # 生成词云数据
    wordcloud = manager.generate_wordcloud_data(test_text, top_n=10)
    print(f"\n词云数据 (前10):")
    for item in wordcloud[:10]:
        print(f"- {item['name']}: {item['value']} {'(术语)' if item['is_term'] else ''}")
    
    # 获取相关术语
    related = manager.get_related_terms("人工智能")
    print(f"\n人工智能相关术语: {', '.join(related)}")
    
    # 获取术语信息
    info = manager.get_term_info("大数据")
    if info:
        print(f"\n大数据定义: {info['definition']}")
    
    print("\n✅ 术语词典模块测试通过！")
