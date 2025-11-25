#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政策文件处理模块
支持上传PDF/DOCX格式的政策文件，提取关键信息并进行分析
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import PyPDF2
from docx import Document

# 导入现有的政策分析器
from src.analysis.policy_analyzer import PolicyAnalyzer

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """文档类型枚举"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    UNKNOWN = "unknown"


@dataclass
class PolicyInfo:
    """政策信息数据类"""
    title: str = ""
    issuing_authority: str = ""
    release_date: str = ""
    applicable_region: str = ""
    key_industries: List[str] = None
    support_measures: List[str] = None
    funding_scale: str = ""
    quantified_indicators: List[Dict] = None
    time_nodes: List[Dict] = None
    
    def __post_init__(self):
        if self.key_industries is None:
            self.key_industries = []
        if self.support_measures is None:
            self.support_measures = []
        if self.quantified_indicators is None:
            self.quantified_indicators = []
        if self.time_nodes is None:
            self.time_nodes = []


class PolicyDocumentProcessor:
    """政策文件处理器"""
    
    def __init__(self):
        """初始化政策文件处理器"""
        self.policy_analyzer = PolicyAnalyzer()
        self.supported_types = [DocumentType.PDF, DocumentType.DOCX, DocumentType.DOC]
        
        # 关键词库用于信息提取
        self.extraction_keywords = {
            "title": ["政策", "通知", "意见", "办法", "规定"],
            "authority": ["发布", "印发", "颁布", "发文机关"],
            "region": ["地区", "区域", "省市", "区县", "适用范围"],
            "industry": ["产业", "行业", "领域", "方向"],
            "measures": ["支持", "扶持", "补贴", "奖励", "优惠"],
            "funding": ["资金", "金额", "规模", "投入", "亿元", "万元"]
        }
    
    def process_uploaded_document(self, file_path: str) -> Dict:
        """处理上传的政策文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理结果和提取的信息
        """
        try:
            # 1. 识别文件类型
            doc_type = self._identify_document_type(file_path)
            if doc_type == DocumentType.UNKNOWN:
                raise ValueError("不支持的文件格式")
            
            # 2. 解析文档内容
            content = self._extract_text_content(file_path, doc_type)
            
            # 3. 提取关键信息
            policy_info = self._extract_policy_info(content)
            
            # 4. 分析政策内容
            analysis_result = self._analyze_policy_content(content, policy_info)
            
            # 5. 生成结构化结果
            result = {
                "status": "success",
                "document_type": doc_type.value,
                "policy_info": asdict(policy_info),
                "analysis": analysis_result,
                "raw_content": content[:1000] + "..." if len(content) > 1000 else content
            }
            
            logger.info(f"✅ 政策文件处理完成: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 政策文件处理失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _identify_document_type(self, file_path: str) -> DocumentType:
        """识别文档类型"""
        try:
            _, extension = os.path.splitext(file_path)
            extension = extension.lower()
            
            if extension == '.pdf':
                return DocumentType.PDF
            elif extension == '.docx':
                return DocumentType.DOCX
            elif extension == '.doc':
                return DocumentType.DOC
            else:
                return DocumentType.UNKNOWN
                
        except Exception as e:
            logger.error(f"文件类型识别失败: {e}")
            return DocumentType.UNKNOWN
    
    def _extract_text_content(self, file_path: str, doc_type: DocumentType) -> str:
        """提取文档文本内容"""
        try:
            if doc_type == DocumentType.PDF:
                return self._extract_pdf_content(file_path)
            elif doc_type == DocumentType.DOCX:
                return self._extract_docx_content(file_path)
            elif doc_type == DocumentType.DOC:
                return self._extract_doc_content(file_path)
            else:
                raise ValueError(f"不支持的文档类型: {doc_type}")
                
        except Exception as e:
            logger.error(f"文档内容提取失败: {e}")
            raise
    
    def _extract_pdf_content(self, file_path: str) -> str:
        """提取PDF文档内容"""
        try:
            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
            return content
        except Exception as e:
            logger.error(f"PDF内容提取失败: {e}")
            raise
    
    def _extract_docx_content(self, file_path: str) -> str:
        """提取DOCX文档内容"""
        try:
            doc = Document(file_path)
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            return content
        except Exception as e:
            logger.error(f"DOCX内容提取失败: {e}")
            raise

    def _extract_doc_content(self, file_path: str) -> str:
        """提取DOC文档内容"""
        try:
            # Use mammoth as primary approach for DOC files
            import mammoth
            with open(file_path, "rb") as doc_file:
                result = mammoth.convert_to_text(doc_file)
                return result.value
        except ImportError:
            logger.warning("mammoth not available for DOC processing")
            # Fallback to docx2txt if available
            try:
                import docx2txt
                return docx2txt.process(file_path)
            except:
                logger.error("DOC content extraction failed")
                raise ValueError("无法提取DOC文档内容，请尝试转换为DOCX格式")
        except Exception as e:
            logger.error(f"DOC内容提取失败: {e}")
            raise
    
    def _extract_policy_info(self, content: str) -> PolicyInfo:
        """提取政策关键信息"""
        policy_info = PolicyInfo()
        
        try:
            # 提取标题（通常在文档开头）
            title_match = re.search(r'^(.*?)(?:政策|通知|意见|办法|规定)', content[:200])
            if title_match:
                policy_info.title = title_match.group(1).strip()
            
            # 提取发文机构
            authority_patterns = [
                r'由(.*?)发布',
                r'(.{2,10})(?:印发|发布|颁布)',
                r'发文机关[：:](.*?)\n'
            ]
            
            for pattern in authority_patterns:
                match = re.search(pattern, content)
                if match:
                    policy_info.issuing_authority = match.group(1).strip()
                    break
            
            # 提取发布日期
            date_patterns = [
                r'(\d{4})年(\d{1,2})月(\d{1,2})日',
                r'(\d{4})-(\d{1,2})-(\d{1,2})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, content)
                if match:
                    if '-' in pattern:
                        policy_info.release_date = match.group(0)
                    else:
                        year, month, day = match.groups()
                        policy_info.release_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    break
            
            # 提取适用区域
            region_patterns = [
                r'(?:适用|覆盖|针对).*?([省市县区]+)',
                r'([^，。]{1,10})(?:地区|区域|范围)',
                r'(?:在|于)([^，。]{1,10})(?:实施|执行)'
            ]
            
            for pattern in region_patterns:
                match = re.search(pattern, content)
                if match:
                    policy_info.applicable_region = match.group(1).strip()
                    break
            
            # 提取重点支持产业
            industry_matches = re.findall(r'(?:支持|发展|促进)(.*?)(?:产业|行业)', content)
            if industry_matches:
                policy_info.key_industries = [m.strip() for m in industry_matches[:5]]
            
            # 提取扶持措施
            measure_matches = re.findall(r'(?:支持|补贴|奖励|优惠).*?(?:。|；|\n)', content)
            if measure_matches:
                policy_info.support_measures = [m.strip() for m in measure_matches[:10]]
            
            # 提取资金规模
            funding_match = re.search(r'(\d+(?:\.\d+)?)[亿万千百]?元', content)
            if funding_match:
                policy_info.funding_scale = funding_match.group(0)
            
            # 提取量化指标
            policy_info.quantified_indicators = self._extract_quantified_indicators(content)
            
            # 提取时间节点
            policy_info.time_nodes = self._extract_time_nodes(content)
            
            logger.info("✅ 政策关键信息提取完成")
            return policy_info
            
        except Exception as e:
            logger.error(f"政策信息提取失败: {e}")
            return policy_info
    
    def _extract_quantified_indicators(self, content: str) -> List[Dict]:
        """提取量化指标"""
        indicators = []
        
        try:
            # 匹配各种量化指标
            patterns = [
                r'(\d+(?:\.\d+)?)[亿万千百]?元',  # 金额
                r'(\d+(?:\.\d+)?)%',  # 百分比
                r'(\d+(?:\.\d+)?)[亿万千百](?:项|个|家)',  # 数量
                r'(\d+(?:\.\d+)?)年',  # 年限
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    # 获取上下文
                    start = max(0, match.start() - 20)
                    end = min(len(content), match.end() + 20)
                    context = content[start:end].strip()
                    
                    indicators.append({
                        "value": match.group(1),
                        "unit": match.group(0)[-1] if match.group(0)[-1].isalpha() else "数量",
                        "context": context,
                        "position": match.start()
                    })
            
            # 去重并按位置排序
            seen = set()
            unique_indicators = []
            for indicator in sorted(indicators, key=lambda x: x["position"]):
                key = (indicator["value"], indicator["unit"])
                if key not in seen:
                    seen.add(key)
                    unique_indicators.append(indicator)
            
            return unique_indicators[:20]  # 限制数量
            
        except Exception as e:
            logger.error(f"量化指标提取失败: {e}")
            return indicators
    
    def _extract_time_nodes(self, content: str) -> List[Dict]:
        """提取时间节点"""
        time_nodes = []
        
        try:
            # 匹配日期格式
            date_patterns = [
                (r'(\d{4})年(\d{1,2})月(\d{1,2})日', 
                 lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
                (r'(\d{4})-(\d{1,2})-(\d{1,2})', 
                 lambda m: m.group(0)),
                (r'(\d{4})年(\d{1,2})月', 
                 lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}")
            ]
            
            for pattern, formatter in date_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    date_str = formatter(match)
                    
                    # 获取上下文
                    start = max(0, match.start() - 30)
                    end = min(len(content), match.end() + 30)
                    context = content[start:end].strip()
                    
                    # 判断时间类型
                    event_type = "其他"
                    if any(kw in context for kw in ["发布", "颁布", "实施"]):
                        event_type = "发布实施"
                    elif any(kw in context for kw in ["截止", "之前", "到期", "申报"]):
                        event_type = "截止时间"
                    elif any(kw in context for kw in ["申报", "申请"]):
                        event_type = "申报时间"
                    
                    time_nodes.append({
                        "date": date_str,
                        "event_type": event_type,
                        "context": context,
                        "is_future": self._is_future_date(date_str)
                    })
            
            # 按日期排序
            time_nodes.sort(key=lambda x: x["date"])
            
            return time_nodes
            
        except Exception as e:
            logger.error(f"时间节点提取失败: {e}")
            return time_nodes
    
    def _is_future_date(self, date_str: str) -> bool:
        """判断日期是否在未来"""
        try:
            # 处理不同日期格式
            if len(date_str) == 10:  # YYYY-MM-DD
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            elif len(date_str) == 7:  # YYYY-MM
                date_obj = datetime.strptime(date_str, "%Y-%m")
            else:
                return False
                
            return date_obj > datetime.now()
        except:
            return False
    
    def _analyze_policy_content(self, content: str, policy_info: PolicyInfo) -> Dict:
        """分析政策内容"""
        try:
            # 使用现有的政策分析器进行分析
            analysis = self.policy_analyzer.analyze_policy(content)
            
            # 添加额外的分析维度
            extended_analysis = {
                **analysis,
                "industry_correlation": self._analyze_industry_correlation(content),
                "policy_intensity": self._evaluate_policy_intensity(policy_info),
                "timeliness": self._analyze_timeliness(policy_info),
                "regional_matching": self._analyze_regional_matching(policy_info)
            }
            
            logger.info("✅ 政策内容分析完成")
            return extended_analysis
            
        except Exception as e:
            logger.error(f"政策内容分析失败: {e}")
            return {}
    
    def _analyze_industry_correlation(self, content: str) -> Dict:
        """分析产业关联度"""
        try:
            # 识别产业链上下游关系
            upstream_keywords = ["原材料", "零部件", "基础", "上游"]
            downstream_keywords = ["应用", "市场", "下游", "终端"]
            core_keywords = ["核心", "关键", "重点", "主导"]
            
            upstream_matches = sum(1 for kw in upstream_keywords if kw in content)
            downstream_matches = sum(1 for kw in downstream_keywords if kw in content)
            core_matches = sum(1 for kw in core_keywords if kw in content)
            
            return {
                "upstream_industries": upstream_matches,
                "downstream_industries": downstream_matches,
                "core_industries": core_matches,
                "total_chain_mentions": upstream_matches + downstream_matches + core_matches
            }
        except Exception as e:
            logger.error(f"产业关联度分析失败: {e}")
            return {}
    
    def _evaluate_policy_intensity(self, policy_info: PolicyInfo) -> Dict:
        """评估政策力度"""
        try:
            # 基于扶持措施数量和资金规模评估
            measure_count = len(policy_info.support_measures)
            has_funding = bool(policy_info.funding_scale)
            
            # 简单分级算法
            if measure_count >= 10 and has_funding:
                intensity_level = "高强度"
            elif measure_count >= 5 or has_funding:
                intensity_level = "中等强度"
            else:
                intensity_level = "低强度"
            
            return {
                "level": intensity_level,
                "measure_count": measure_count,
                "has_funding_support": has_funding,
                "funding_scale": policy_info.funding_scale
            }
        except Exception as e:
            logger.error(f"政策力度评估失败: {e}")
            return {}
    
    def _analyze_timeliness(self, policy_info: PolicyInfo) -> Dict:
        """分析时效性"""
        try:
            time_nodes = policy_info.time_nodes
            if not time_nodes:
                return {}
            
            # 计算政策有效期
            future_dates = [t for t in time_nodes if t["is_future"]]
            if future_dates:
                validity_period = len(future_dates)
                relevance_score = min(validity_period * 10, 100)  # 简单评分
            else:
                relevance_score = 0
            
            return {
                "validity_period": validity_period if 'validity_period' in locals() else 0,
                "upcoming_deadlines": len(future_dates),
                "relevance_score": relevance_score,
                "has_future_dates": len(future_dates) > 0
            }
        except Exception as e:
            logger.error(f"时效性分析失败: {e}")
            return {}
    
    def _analyze_regional_matching(self, policy_info: PolicyInfo) -> Dict:
        """分析区域匹配度"""
        try:
            # 这里需要结合分析师关注的区域进行匹配
            # 目前返回基础信息
            return {
                "applicable_region": policy_info.applicable_region,
                "has_regional_scope": bool(policy_info.applicable_region),
                "matching_score": 50  # 默认中等匹配度
            }
        except Exception as e:
            logger.error(f"区域匹配度分析失败: {e}")
            return {}


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建处理器实例
    processor = PolicyDocumentProcessor()
    
    # 测试政策信息提取
    test_content = """
    关于支持人工智能产业发展的若干政策
    
    为贯彻落实国家关于发展人工智能的战略部署，支持我市人工智能产业发展，
    特制定本政策。
    
    一、总体目标
    到2025年，全市人工智能核心产业规模达到500亿元，培育100家以上人工智能企业。
    
    二、支持措施
    1. 资金支持：设立人工智能产业发展专项资金，每年安排不少于10亿元。
    2. 税收优惠：对高新技术企业减按15%税率征收企业所得税。
    3. 人才引进：对引进的高层次人才给予最高200万元安家补贴。
    4. 研发支持：对企业研发投入给予20%的资金资助。
    
    三、申报条件
    1. 在本市注册的人工智能企业；
    2. 具有独立法人资格；
    3. 上年度营业收入不低于1000万元。
    
    四、申报时间
    自2024年3月1日起至2024年6月30日止。
    
    五、实施期限
    本政策自发布之日起施行，有效期至2025年12月31日。
    
    发布机关：北京市人民政府
    发布日期：2024年1月15日
    """
    
    # 提取政策信息
    policy_info = processor._extract_policy_info(test_content)
    print("政策信息提取结果:")
    print(json.dumps(asdict(policy_info), ensure_ascii=False, indent=2))
    
    # 分析政策内容
    analysis_result = processor._analyze_policy_content(test_content, policy_info)
    print("\n政策分析结果:")
    print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
    
    print("\n✅ 政策文件处理模块测试通过！")