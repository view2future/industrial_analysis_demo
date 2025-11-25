#!/usr/bin/env python3
"""
Kimi Policy Parser - Uses Moonshot AI (Kimi) for policy document analysis
"""

import logging
import json
import time
from typing import Dict, Any, List
from openai import OpenAI
import os

logger = logging.getLogger(__name__)


class KimiPolicyParser:
    """Policy parser using Kimi (Moonshot AI) for advanced analysis"""
    
    def __init__(self, config_path: str = 'config.json'):
        """Initialize the Kimi policy parser with API configuration."""
        self.config = self._load_config(config_path)
        
        # Get Kimi API key from config
        api_keys = self.config.get('api_keys', {})
        self.api_key = (
            api_keys.get('kimi')
            or api_keys.get('kimi_api_key')
            or os.environ.get('KIMI_API_KEY')
            or os.environ.get('MOONSHOT_API_KEY')
        )
        
        if not self.api_key:
            raise ValueError("Kimi API key not found in config or environment variables")
        
        # Initialize the OpenAI client with Kimi endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.moonshot.cn/v1"
        )
        
        # Use a high-context model for better policy understanding
        self.model = "moonshot-v1-128k"
        self.temperature = 0.3  # Lower temperature for more consistent analysis
        self.max_tokens = 4000  # Sufficient for detailed policy analysis
        
        logger.info("✅ Kimi Policy Parser initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def parse_policy_document(self, document_text: str) -> Dict[str, Any]:
        """
        Parse a policy document using Kimi AI for comprehensive analysis.
        
        Args:
            document_text: The full text of the policy document
            
        Returns:
            Dict containing structured policy analysis results
        """
        try:
            logger.info("🚀 Starting Kimi policy analysis...")
            start_time = time.time()
            
            # Prepare the prompt for policy analysis
            prompt = self._create_policy_analysis_prompt(document_text)
            
            # Call Kimi API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert policy analyst. Analyze the given policy document and extract key information in JSON format. Be precise, comprehensive, and structure the information logically. Focus on identifying specific amounts, dates, eligibility criteria, and requirements."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}  # Request JSON output
            )
            
            response_text = completion.choices[0].message.content
            logger.info(f"✅ Kimi API call completed in {time.time() - start_time:.2f}s")
            
            # Parse the JSON response
            try:
                result = json.loads(response_text)
                logger.info("✅ Policy analysis completed successfully")
                return self._validate_and_format_result(result, document_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response_text[:500]}...")
                # Fallback: return basic structure
                return self._create_fallback_result(document_text)
                
        except Exception as e:
            logger.error(f"❌ Kimi policy analysis failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._create_fallback_result(document_text, error=str(e))
    
    def _create_policy_analysis_prompt(self, document_text: str) -> str:
        """Create the prompt for policy analysis using the local prompt file."""
        # Read the local prompt template
        try:
            with open('policy_analysis_prompt.md', 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            # Try different possible filenames
            try:
                with open('policy_analysis_prompt.txt', 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
            except FileNotFoundError:
                logger.warning("Policy analysis prompt file not found, using fallback prompt")
                # Fallback prompt if no file is available
                prompt_template = """# 政策文件深度分析报告

## 1. 政策摘要 (Policy Summary)

* **核心内容提炼**：请从以下政策文档中精炼出核心政策内容，包括政策目标、主要措施、适用对象、实施期限等关键信息。
* **关键要点概述**：用2-3句话概括政策的核心要点和影响。

## 2. 政策要点分类 (Policy Key Points)

请将政策内容按以下类别进行分门别类地罗列：

### 资金支持类
* 详细列出政策中提及的资金补贴、奖励、专项资金等量化指标
* 包括金额范围、申请条件、支持比例等具体数据

### 税收优惠类
* 明确列出各项税收减免、优惠政策
* 注明适用税率、减免幅度、执行期限等

### 人才支持类
* 人才引进、培训、激励等相关政策条款
* 包括补贴金额、优惠政策、服务保障等内容

### 土地政策类
* 土地使用、租金减免、产业园区等相关政策
* 注明面积、价格、期限等具体量化指标

### 金融支持类
* 贷款、融资、担保等金融支持政策
* 包括利率、额度、期限、贴息比例等数据

### 其他支持类
* 其他形式的政策支持措施
* 如审批绿色通道、简化流程等

### 年度目标与量化指标
* 政策中明确的各项目标和量化指标
* 包括时间节点、完成标准、预期效果等

## 3. 产业链分析 (Industry Chain Analysis)

请根据政策文件内容，识别并分析相关产业的上中下游结构：

### 上游产业 (Upstream Industries)
* 政策涉及的原材料、基础设备、核心零部件等相关产业
* 政策对上游产业的影响和支持措施

### 中游产业 (Midstream Industries)
* 政策涉及的核心生产、制造、集成等相关产业
* 政策对中游产业的主要扶持措施

### 下游产业 (Downstream Industries)
* 政策涉及的应用市场、服务、销售渠道等相关产业
* 政策对下游产业的推动作用

### 产业链协同
* 上中下游产业链协同发展的政策措施
* 产业链补链强链的具体举措

## 4. 注意事项

* **准确提取**：严格按照政策原文内容进行分析，不得编造或推测
* **量化指标优先**：优先提取和展示政策中的具体数据、金额、比例等量化指标
* **时间节点明确**：明确标注政策实施、申报、截止等相关时间节点
* **结构清晰**：按照上述分类清晰有序地展示政策内容
* **去除适用性评分**：不包含任何关于适用性评分的内容

现在请开始分析以下政策文档："""

        # Limit document length to prevent exceeding token limits
        max_length = 20000  # Keep prompt under reasonable length
        truncated_text = document_text[:max_length] if len(document_text) > max_length else document_text

        # Replace the placeholder in the prompt
        return prompt_template.replace("现在请开始分析提供的政策文档。",
                                      f"现在请开始分析以下政策文档：\n\n{truncated_text}")
    
    def _validate_and_format_result(self, result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Validate and format the result to ensure complete structure."""
        # Ensure required top-level keys exist
        required_keys = [
            'metadata', 'document_structure', 'entities', 'provisions', 
            'requirements', 'quantitative_data', 'timeline', 
            'relationships', 'key_points', 'analysis', 'full_text'
        ]
        
        for key in required_keys:
            if key not in result:
                if key == 'metadata':
                    result[key] = {
                        'title': '政策标题',
                        'issuing_authority': '发布机构',
                        'publication_date': '',
                        'applicable_regions': [],
                        'key_industries': []
                    }
                elif key == 'document_structure':
                    result[key] = []
                elif key == 'entities':
                    result[key] = {
                        'organizations': [],
                        'key_personnel': [],
                        'geographical_entities': []
                    }
                elif key == 'provisions':
                    result[key] = []
                elif key == 'requirements':
                    result[key] = []
                elif key == 'quantitative_data':
                    result[key] = {
                        'amounts': [], 'thresholds': [], 
                        'ratios': [], 'time_periods': []
                    }
                elif key == 'timeline':
                    result[key] = []
                elif key == 'relationships':
                    result[key] = []
                elif key == 'key_points':
                    result[key] = ['政策要点']
                elif key == 'analysis':
                    result[key] = {
                        'industry_relevance': {
                            'value_chain': {
                                'upstream': [], 'midstream': [], 'downstream': []
                            },
                            'related_industries': []
                        },
                        'policy_strength': {
                            'funding_level': 'Medium',
                            'measure_diversity': 0,
                            'support_comprehensiveness': 'Partial'
                        },
                        'timeliness_score': 70,
                        'regional_match_score': 75
                    }
                elif key == 'full_text':
                    result[key] = original_text
        
        # Set the original text as full_text if not provided or empty
        if not result.get('full_text'):
            result['full_text'] = original_text
            
        return result
    
    def _create_fallback_result(self, document_text: str, error: str = "") -> Dict[str, Any]:
        """Create a fallback result when Kimi analysis fails."""
        logger.warning(f"Falling back to basic analysis due to error: {error}")
        
        return {
            'metadata': {
                'title': 'Kimi解析失败 - 使用本地解析',
                'issuing_authority': '未知',
                'publication_date': '',
                'applicable_regions': [],
                'key_industries': []
            },
            'document_structure': [{'section': '全文', 'content': 'Kimi解析失败，内容显示'}],
            'entities': {
                'organizations': [],
                'key_personnel': [],
                'geographical_entities': []
            },
            'provisions': [],
            'requirements': [],
            'quantitative_data': {
                'amounts': [], 'thresholds': [], 
                'ratios': [], 'time_periods': []
            },
            'timeline': [],
            'relationships': [],
            'key_points': [document_text[:500] + '...' if len(document_text) > 500 else document_text],
            'analysis': {
                'industry_relevance': {
                    'value_chain': {
                        'upstream': [], 'midstream': [], 'downstream': []
                    },
                    'related_industries': []
                },
                'policy_strength': {
                    'funding_level': 'Unknown',
                    'measure_diversity': 0,
                    'support_comprehensiveness': 'Unknown'
                },
                'timeliness_score': 0,
                'regional_match_score': 0
            },
            'full_text': document_text
        }


if __name__ == "__main__":
    # Test the Kimi policy parser
    logging.basicConfig(level=logging.INFO)
    
    try:
        parser = KimiPolicyParser()
        test_document = """
        关于支持人工智能产业发展的若干政策
        
        为贯彻落实国家关于发展人工智能的战略部署，支持我市人工智能产业发展，
        特制定本政策。
        
        一、总体目标
        到2025年，全市人工智能核心产业规模达到500亿元，培育100家以上人工智能企业。
        
        二、支持措施
        1. 资金支持：设立人工智能产业发展专项资金，每年安排不少于10亿元。
        2. 税收优惠：对高新技术企业减按15%税率征收企业所得税。
        3. 人才引进：对引进的高层次人才给予最高200万元安家补贴。
        
        三、申报时间
        自2024年3月1日起至2024年6月30日止。
        """
        
        result = parser.parse_policy_document(test_document)
        print(f"✅ Kimi policy parsing completed!")
        print(f"Title: {result['metadata']['title']}")
        print(f"Key industries: {result['metadata']['key_industries']}")
        print(f"Quantitative data amounts: {len(result['quantitative_data']['amounts'])}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()