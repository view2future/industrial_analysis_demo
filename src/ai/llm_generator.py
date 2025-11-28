#!/usr/bin/env python3
"""
LLM Report Generator using Kimi API (Moonshot AI)
Generates comprehensive regional industrial analysis reports.
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional, List
from openai import OpenAI
import google.generativeai as genai
from src.utils.api_error_handler import api_error_handler, handle_api_error, APIError, APIService

logger = logging.getLogger(__name__)


class LLMReportGenerator:
    """Generates industrial analysis reports using various LLM services with comprehensive error handling."""
    
    def __init__(self, config_path='config.json', llm_service: str = 'kimi', enable_fallback=True):
        """Initialize the LLM report generator.
        
        Args:
            config_path: Path to configuration file containing API keys
            llm_service: The LLM service to use ('kimi', 'gemini', or 'doubao')
        """
        logger.info("="*60)
        logger.info(f"初始化 {llm_service.upper()} LLM 报告生成器")
        logger.info("="*60)
        
        self.config = self._load_config(config_path)
        self.llm_service = llm_service
        self.enable_fallback = enable_fallback
        self.api_error_handler = api_error_handler
        self.available_services = self._detect_available_services()
        self.current_service = self._get_service_enum(llm_service)
        import threading
        self._client_lock = threading.Lock()
        self.usage_metrics = { 'kimi': 0, 'gemini': 0, 'doubao': 0 }
        
        if self.llm_service == 'kimi':
            api_keys_cfg = self.config.get('api_keys', {})
            self.api_key = (
                api_keys_cfg.get('kimi')
                or api_keys_cfg.get('kimi_api_key')
                or os.environ.get('KIMI_API_KEY')
                or os.environ.get('MOONSHOT_API_KEY')
            )
            if not self.api_key:
                logger.error("❌ Kimi API Key 未找到，请检查配置或环境变量")
                raise ValueError("Kimi API key not found")
            with self._client_lock:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.moonshot.cn/v1"
                )
            self.model_name = os.environ.get('KIMI_MODEL', "moonshot-v1-128k")
            self.temperature = float(os.environ.get('KIMI_TEMPERATURE', 0.7))
            self.max_tokens = int(os.environ.get('KIMI_MAX_TOKENS', 8000))
            logger.info("✓ Kimi API 配置成功")

        elif self.llm_service == 'gemini':
            api_keys_cfg = self.config.get('api_keys', {})
            self.api_key = (
                api_keys_cfg.get('google_gemini')
                or api_keys_cfg.get('google_gemini_api_key')
                or os.environ.get('GOOGLE_GEMINI_API_KEY')
            )
            if not self.api_key:
                logger.error("❌ Gemini API Key 未找到，请检查配置或环境变量")
                raise ValueError("Gemini API key not found")
            genai.configure(api_key=self.api_key)
            with self._client_lock:
                self.client = genai.GenerativeModel('gemini-1.5-pro-latest')
            self.model_name = "gemini-1.5-pro-latest"
            self.temperature = 0.7
            self.max_tokens = 8000
            logger.info("✓ Gemini API 配置成功")
            
        elif self.llm_service == 'doubao':
            self.api_key = self.config.get('api_keys', {}).get('doubao_api_key')
            if not self.api_key:
                logger.error("❌ Doubao API Key 未找到，请检查 config.json")
                raise ValueError("Doubao API key not found in config")
            
            logger.info(f"✓ Doubao API Key 已加载 (前10位): {self.api_key[:10]}...")
            # 豆包大模型集成逻辑将在这里实现
            self.client = None  # 占位符，实际实现时需要替换
            self.model_name = "doubao-pro"  # 占位符，实际实现时需要替换
            self.temperature = 0.7
            self.max_tokens = 8000
            logger.info("✓ Doubao API 配置成功")
        else:
            raise ValueError(f"Unsupported LLM service: {self.llm_service}")
        
        # 加载提示词模板
        logger.info("加载提示词模板...")
        self.prompt_template = self._load_prompt_template()
        if self.prompt_template:
            logger.info(f"✓ 提示词模板已加载 (长度: {len(self.prompt_template)} 字符)")
        else:
            logger.warning("⚠️ 提示词模板为空，将使用默认格式")
        
        logger.info("="*60)
        logger.info(f"✅ {self.llm_service.upper()} LLM 报告生成器初始化完成")
        logger.info("="*60)
    
    def _get_service_enum(self, service_name: str) -> APIService:
        """Convert service name to enum"""
        try:
            return APIService(service_name.lower())
        except ValueError:
            logger.warning(f"未知服务类型: {service_name}，默认使用 Kimi")
            return APIService.KIMI
    
    def _detect_available_services(self) -> List[APIService]:
        """Detect which services have valid API keys configured"""
        available = []
        
        api_keys_cfg = self.config.get('api_keys', {})
        # Check Kimi
        if api_keys_cfg.get('kimi') or api_keys_cfg.get('kimi_api_key') or os.environ.get('KIMI_API_KEY') or os.environ.get('MOONSHOT_API_KEY'):
            available.append(APIService.KIMI)
        
        # Check Gemini
        if api_keys_cfg.get('google_gemini') or api_keys_cfg.get('google_gemini_api_key') or os.environ.get('GOOGLE_GEMINI_API_KEY'):
            available.append(APIService.GEMINI)
        
        # Check Doubao
        if self.config.get('api_keys', {}).get('doubao_api_key'):
            available.append(APIService.DOUBAO)
        
        logger.info(f"✅ 检测到可用服务: {[s.value for s in available]}")
        return available
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _load_prompt_template(self) -> str:
        """Load the prompt template from file."""
        template_path = Path('industry_analysis_llm_prompt.md')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            return ""
    
    def generate_report(self, city: str, industry: str, 
                       additional_context: str = "", max_fallback_attempts: int = 2) -> Dict:
        """Generate a comprehensive industrial analysis report with intelligent error handling and fallback.
        
        Args:
            city: Target city name (e.g., "成都", "重庆")
            industry: Target industry name (e.g., "人工智能", "汽车产业")
            additional_context: Additional context or requirements
            max_fallback_attempts: Maximum number of fallback attempts to other services
        
        Returns:
            Dictionary containing the generated report and metadata, with error information if failed
        """
        try:
            # 准备提示词
            prompt = self._prepare_prompt(city, industry, additional_context)
            
            # 生成报告
            logger.info("="*60)
            logger.info(f"🚀 开始生成报告: {city} - {industry}")
            logger.info(f"🌐 首选服务: {self.llm_service.upper()}")
            logger.info(f"🔄 启用回退机制: {self.enable_fallback}")
            logger.info("="*60)
            logger.info(f"📝 提示词长度: {len(prompt)} 字符")
            
            # 尝试生成报告，支持服务回退
            return self._generate_report_with_fallback(
                city, industry, prompt, max_fallback_attempts
            )
            
        except Exception as e:
            logger.error("="*60)
            logger.error(f"❌ 报告生成失败")
            logger.error("="*60)
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误详情: {str(e)}")
            
            import traceback
            logger.error("完整堆栈跟踪:")
            logger.error(traceback.format_exc())
            
            # 使用错误处理器分析错误
            api_error = handle_api_error(e, self.llm_service, "报告生成")
            
            return {
                'success': False,
                'error': str(e),
                'api_error': {
                    'type': api_error.error_type.value,
                    'service': api_error.service.value,
                    'user_message': api_error.user_friendly_message,
                    'suggested_action': api_error.suggested_action,
                    'retry_after': api_error.retry_after
                },
                'city': city,
                'industry': industry,
                'failed_service': self.llm_service
            }
    
    def _call_kimi_api(self, prompt: str, start_time: float) -> Dict:
        """Call Kimi API"""
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位专业的产业分析师，擅长撰写深度的区域产业分析报告。请基于用户提供的框架和要求，生成详实、专业的分析报告。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        report_content = completion.choices[0].message.content
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        total_tokens = completion.usage.total_tokens
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Kimi API 调用成功！耗时: {elapsed:.2f} 秒")
        
        return {
            'success': True,
            'content': report_content,
            'tokens': {
                'prompt': prompt_tokens,
                'completion': completion_tokens,
                'total': total_tokens
            }
        }
    def _generate_report_with_fallback(self, city: str, industry: str, prompt: str, 
                                       max_fallback_attempts: int) -> Dict:
        """Generate report with intelligent fallback between services"""
        
        services_to_try = [self.current_service] + [
            s for s in self.available_services 
            if s != self.current_service
        ]
        
        last_error = None
        attempted_services = []
        
        for i, service in enumerate(services_to_try[:max_fallback_attempts + 1]):
            service_name = service.value
            attempted_services.append(service_name)
            
            logger.info(f"\n🔄 尝试服务 {i+1}/{len(services_to_try)}: {service_name.upper()}")
            
            try:
                # 临时切换到目标服务
                original_service = self.llm_service
                self.llm_service = service_name
                self.current_service = service
                
                # 重新初始化客户端
                self._reinitialize_client(service_name)
                
                # 生成报告
                result = self._call_api_with_retry(service_name, prompt)
                
                # 恢复原始服务
                self.llm_service = original_service
                self.current_service = self._get_service_enum(original_service)
                
                if result and result.get('success'):
                    logger.info(f"✅ 使用 {service_name.upper()} 成功生成报告！")
                    
                    # 使用返回的内容生成完整报告结构
                    report_content = result['content']
                    tokens = result['tokens']
                    
                    # 解析报告章节
                    logger.info("🔍 解析报告章节...")
                    sections = self._parse_report_sections(report_content)
                    logger.info(f"✓ 解析完成，共 {len(sections)} 个章节: {list(sections.keys())}")
                    
                    logger.info("="*60)
                    logger.info("✅ 报告生成成功！")
                    logger.info("="*60)
                    
                    return {
                        'success': True,
                        'city': city,
                        'industry': industry,
                        'full_content': report_content,
                        'sections': sections,
                        'metadata': {
                            'generated_at': None,
                            'model': self.model_name,
                            'provider': service_name,
                            'prompt_version': '1.0',
                            'tokens': tokens
                        },
                        'used_service': service_name,
                        'attempted_services': attempted_services
                    }
                
            except Exception as e:
                logger.warning(f"❌ {service_name.upper()} 服务失败: {str(e)}")
                last_error = e
                
                # 使用错误处理器分析错误
                api_error = handle_api_error(e, service_name, f"服务回退尝试 {i+1}")
                
                # 如果是配额超限，继续尝试下一个服务
                if api_error.error_type.value == 'quota_exceeded':
                    logger.info(f"➡️  继续尝试下一个服务...")
                    continue
                
                # 如果是连接问题，也可以尝试其他服务
                elif api_error_handler.is_connection_issue(service, e):
                    logger.info(f"➡️  连接问题，尝试下一个服务...")
                    continue
                
                # 恢复原始服务
                self.llm_service = original_service
                self.current_service = self._get_service_enum(original_service)
        
        # 所有服务都失败了
        logger.error(f"❌ 所有可用服务都失败，已尝试: {attempted_services}")
        if last_error:
            raise last_error
        else:
            raise Exception("所有 AI 服务都无法生成报告")
    
    def _reinitialize_client(self, service_name: str):
        """Reinitialize the API client for the specified service"""
        logger.info(f"🔧 重新初始化 {service_name.upper()} 客户端...")
        
        if service_name == 'kimi':
            api_keys_cfg = self.config.get('api_keys', {})
            self.api_key = (
                api_keys_cfg.get('kimi')
                or api_keys_cfg.get('kimi_api_key')
                or os.environ.get('KIMI_API_KEY')
                or os.environ.get('MOONSHOT_API_KEY')
            )
            if not self.api_key:
                raise ValueError("Kimi API key not found in config")

            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.moonshot.cn/v1"
            )
            self.model_name = "moonshot-v1-128k"

        elif service_name == 'gemini':
            api_keys_cfg = self.config.get('api_keys', {})
            self.api_key = (
                api_keys_cfg.get('google_gemini')
                or api_keys_cfg.get('google_gemini_api_key')
                or os.environ.get('GOOGLE_GEMINI_API_KEY')
            )
            if not self.api_key:
                raise ValueError("Gemini API key not found in config")

            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel('gemini-pro')
            self.model_name = "gemini-pro"

        elif service_name == 'doubao':
            self.api_key = self.config.get('api_keys', {}).get('doubao_api_key')
            if not self.api_key:
                raise ValueError("Doubao API key not found in config")

            # 豆包大模型客户端初始化逻辑
            self.client = None  # 占位符
            self.model_name = "doubao-pro"
    
    def _call_api_with_retry(self, service_name: str, prompt: str) -> Dict:
        """Call API with intelligent retry logic"""
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"📡 API 调用尝试 {attempt + 1}/{max_retries}...")
                start_time = time.time()
                
                # Key rotation check and reinit if necessary
                self._check_key_rotation_and_reinit(service_name)
                if service_name == 'kimi':
                    return self._call_kimi_api(prompt, start_time)
                elif service_name == 'gemini':
                    return self._call_gemini_api(prompt, start_time)
                elif service_name == 'doubao':
                    return self._call_doubao_api(prompt, start_time)
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"❌ API 调用失败 (尝试 {attempt + 1}/{max_retries}，耗时 {elapsed:.2f}秒)")
                
                # 使用错误处理器分析错误
                api_error = handle_api_error(e, service_name, f"API 调用尝试 {attempt + 1}")
                
                # 检查是否应该立即重试
                if not api_error_handler.should_retry_immediately(api_error):
                    logger.warning(f"⏹️  错误类型不建议重试: {api_error.error_type.value}")
                    raise e
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # 指数退避
                    retry_after = api_error.retry_after or delay
                    logger.warning(f"⏳ 等待 {retry_after} 秒后重试...")
                    time.sleep(retry_after)
                else:
                    logger.error("💥 所有重试均失败，放弃请求")
                    raise
    
    def _call_kimi_api(self, prompt: str, start_time: float) -> Dict:
        """Call Kimi API"""
        with self._client_lock:
            completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位专业的产业分析师，擅长撰写深度的区域产业分析报告。请基于用户提供的框架和要求，生成详实、专业的分析报告。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        report_content = completion.choices[0].message.content
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        total_tokens = completion.usage.total_tokens
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Kimi API 调用成功！耗时: {elapsed:.2f} 秒")
        self.usage_metrics['kimi'] += 1
        
        return {
            'success': True,
            'content': report_content,
            'tokens': {
                'prompt': prompt_tokens,
                'completion': completion_tokens,
                'total': total_tokens
            }
        }
    
    def _call_gemini_api(self, prompt: str, start_time: float) -> Dict:
        """Call Gemini API"""
        with self._client_lock:
            response = self.client.generate_content(
            prompt,
            generation_config={
                'temperature': self.temperature,
                'max_output_tokens': self.max_tokens
            }
        )
        
        report_content = response.text
        elapsed = time.time() - start_time
        logger.info(f"✅ Gemini API 调用成功！耗时: {elapsed:.2f} 秒")
        self.usage_metrics['gemini'] += 1
        
        return {
            'success': True,
            'content': report_content,
            'tokens': {
                'prompt': 0,  # Gemini doesn't provide detailed token usage
                'completion': 0,
                'total': 0
            }
        }
    
    def _call_doubao_api(self, prompt: str, start_time: float) -> Dict:
        """Call Doubao API (placeholder implementation)"""
        logger.warning("⚠️ 豆包大模型 API 调用尚未完全实现")
        
        # 模拟响应或抛出特定错误
        raise NotImplementedError("豆包大模型 API 集成尚未完成")
            
    def _parse_report_sections(self, content: str) -> Dict:
        """Parse the generated report into structured sections."""
        sections = {}
        
        section_markers = [
            ('executive_summary', ['1. 执行摘要', 'Executive Summary']),
            ('industry_overview', ['2. 产业概览', '产业概览与核心数据']),
            ('policy_landscape', ['3. 政策环境', 'Policy Landscape']),
            ('ecosystem', ['4. 产业生态', '产业生态与关键参与者']),
            ('value_chain', ['5. 产业链分析', 'Value Chain Analysis']),
            ('ai_integration', ['6. AI融合潜力', 'AI Integration Potential']),
            ('conclusion', ['7. 结论', 'Conclusion', '战略建议'])
        ]
        
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            found_section = False
            for section_key, markers in section_markers:
                if any(marker in line for marker in markers):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section_key
                    current_content = []
                    found_section = True
                    break
            
            if not found_section and current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        if not sections:
            sections['full_report'] = content
        
        return sections
            
    def _prepare_prompt(self, city: str, industry: str, 
                       additional_context: str) -> str:
        """Prepare the prompt by replacing placeholders."""
        prompt = self.prompt_template
        prompt = prompt.replace('[目标城市]', city)
        prompt = prompt.replace('[目标行业]', industry)
        
        if additional_context:
            prompt += f"\n\n补充信息和要求：\n{additional_context}"
        
        prompt += "\n\n请按照上述框架，生成一份详细、专业的产业分析报告。报告应包含具体的数据、案例和洞察。"
        
        return prompt
    
    def _prepare_prompt(self, city: str, industry: str, 
                       additional_context: str) -> str:
        """Prepare the prompt by replacing placeholders."""
        prompt = self.prompt_template
        prompt = prompt.replace('[目标城市]', city)
        prompt = prompt.replace('[目标行业]', industry)
        
        if additional_context:
            prompt += f"\n\n补充信息和要求：\n{additional_context}"
        
        prompt += "\n\n请按照上述框架，生成一份详细、专业的产业分析报告。报告应包含具体的数据、案例和洞察。"
        
        return prompt
    
    def _parse_report_sections(self, content: str) -> Dict:
        """Parse the generated report into structured sections."""
        sections = {}
        
        section_markers = [
            ('executive_summary', ['1. 执行摘要', 'Executive Summary']),
            ('industry_overview', ['2. 产业概览', '产业概览与核心数据']),
            ('policy_landscape', ['3. 政策环境', 'Policy Landscape']),
            ('ecosystem', ['4. 产业生态', '产业生态与关键参与者']),
            ('value_chain', ['5. 产业链分析', 'Value Chain Analysis']),
            ('ai_integration', ['6. AI融合潜力', 'AI Integration Potential']),
            ('conclusion', ['7. 结论', 'Conclusion', '战略建议'])
        ]
        
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            found_section = False
            for section_key, markers in section_markers:
                if any(marker in line for marker in markers):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section_key
                    current_content = []
                    found_section = True
                    break
            
            if not found_section and current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        if not sections:
            sections['full_report'] = content
        
        return sections
    
    def stream_report_content(self, city: str, industry: str, additional_context: str = ""):
        """Stream main report content chunks from the LLM service."""
        import time
        try:
            prompt = self._prepare_prompt(city, industry, additional_context)
            if self.llm_service == 'kimi':
                stream = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "你是一位专业的产业分析师。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=True
                )
                for chunk in stream:
                    delta = getattr(chunk.choices[0], 'delta', None)
                    if delta and getattr(delta, 'content', None):
                        yield delta.content
            elif self.llm_service == 'gemini':
                response = self.client.generate_content(prompt, stream=True)
                for chunk in response:
                    if hasattr(chunk, 'text') and chunk.text:
                        yield chunk.text
            else:
                # Fallback: no streaming support
                result = self.generate_report(city, industry, additional_context)
                yield result.get('full_content', '')
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"[流式生成出错] {e}"

    def generate_summary(self, full_report: str, language: str = 'zh') -> str:
        """Generate a concise summary of the full report."""
        logger.info(f"\n{'='*60}")
        logger.info(f"📝 生成{language.upper()}摘要...")
        logger.info(f"{'='*60}")
        
        try:
            if language == 'zh':
                summary_prompt = f"""请基于以下完整的产业分析报告，生成一份简洁的执行摘要（Executive Summary），
长度控制在300-500字，包含：
1. 核心发现（2-3点）
2. 关键数据指标（2-3个）
3. 主要建议（2-3条）

报告内容：
{full_report[:3000]}

请直接输出摘要内容，不需要额外的格式说明。"""
            else:
                summary_prompt = f"""Based on the following industrial analysis report, 
generate a concise Executive Summary in English (200-300 words) including:
1. Key findings (2-3 points)
2. Critical metrics (2-3 items)
3. Main recommendations (2-3 items)

Report content:
{full_report[:3000]}

Please output the summary directly without additional formatting instructions."""
            
            logger.info("🌐 调用 API 生成摘要...")
            start_time = time.time()
            
            if self.llm_service == 'kimi':
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": summary_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=1000
                )
                summary_content = completion.choices[0].message.content
            elif self.llm_service == 'gemini':
                response = self.client.generate_content(summary_prompt)
                summary_content = response.text
            elif self.llm_service == 'doubao':
                # 调用豆包大模型 API 生成摘要 (占位符实现)
                logger.warning("⚠️ 豆包大模型摘要生成功能尚未完全实现")
                summary_content = ""  # 占位符，实际实现时需要替换

            elapsed = time.time() - start_time
            logger.info(f"✅ 摘要生成成功！耗时: {elapsed:.2f} 秒")
            logger.info(f"📊 摘要长度: {len(summary_content)} 字符")
            return summary_content
        
        except Exception as e:
            logger.error(f"❌ 摘要生成失败: {type(e).__name__} - {str(e)}")
            return "摘要生成失败" if language == 'zh' else "Summary generation failed"
    
    def generate_swot_analysis(self, full_report: str) -> Dict:
        """Generate SWOT analysis from the full report."""
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 生成 SWOT 分析...")
        logger.info(f"{'='*60}")
        
        try:
            swot_prompt = f"""请基于以下产业分析报告，生成详细的SWOT战略分析。

要求：
1. 每个维度（优势、劣势、机遇、威胁）至少列出4-6个要点
2. 要点要具体、可操作、有洞察力
3. 结合报告中的具体数据和案例
4. 严格按照JSON格式输出

输出格式：
{{
    "strengths": ["优势1：具体描述...", "优势2：具体描述...", "优势3：具体描述...", "优势4：具体描述..."],
    "weaknesses": ["劣势1：具体描述...", "劣势2：具体描述...", "劣势3：具体描述...", "劣势4：具体描述..."],
    "opportunities": ["机遇1：具体描述...", "机遇2：具体描述...", "机遇3：具体描述...", "机遇4：具体描述..."],
    "threats": ["威胁1：具体描述...", "威胁2：具体描述...", "威胁3：具体描述...", "威胁4：具体描述..."]
}}

报告内容：
{full_report[:4000]}

请只输出JSON格式的内容，不要包含markdown代码块标记或其他说明文字。"""
            
            logger.info("🌐 调用 API 生成 SWOT...")
            start_time = time.time()
            
            if self.llm_service == 'kimi':
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一位专业的战略分析师，擅长进行SWOT分析。请严格按照JSON格式输出结果，不要添加任何markdown标记或额外说明。"
                        },
                        {
                            "role": "user",
                            "content": swot_prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                response_text = completion.choices[0].message.content.strip()
            elif self.llm_service == 'gemini':
                response = self.client.generate_content(swot_prompt)
                response_text = response.text.strip()
            elif self.llm_service == 'doubao':
                # 调用豆包大模型 API 生成 SWOT 分析 (占位符实现)
                logger.warning("⚠️ 豆包大模型 SWOT 分析功能尚未完全实现")
                response_text = "{}"  # 占位符，实际实现时需要替换

            elapsed = time.time() - start_time
            logger.info(f"✅ SWOT 生成成功！耗时: {elapsed:.2f} 秒")
            
            logger.info(f"📄 原始响应长度: {len(response_text)} 字符")
            logger.info(f"📄 响应预览: {response_text[:200]}...")
            
            import re
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'^```\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            response_text = response_text.strip()
            
            try:
                swot_data = json.loads(response_text)
                logger.info(f"✓ SWOT JSON 解析成功")
                logger.info(f"  - 优势: {len(swot_data.get('strengths', []))} 项")
                logger.info(f"  - 劣势: {len(swot_data.get('weaknesses', []))} 项")
                logger.info(f"  - 机遇: {len(swot_data.get('opportunities', []))} 项")
                logger.info(f"  - 威胁: {len(swot_data.get('threats', []))} 项")
                
                if not any([swot_data.get('strengths'), swot_data.get('weaknesses'), 
                           swot_data.get('opportunities'), swot_data.get('threats')]):
                    logger.warning("⚠️ SWOT 所有字段为空，使用文本解析")
                    return self._parse_swot_from_text(response_text)
                
                return swot_data
            except json.JSONDecodeError as je:
                logger.warning(f"⚠️ SWOT 响应不是有效 JSON: {str(je)}")
                logger.info(f"尝试解析的文本: {response_text[:500]}")
                return self._parse_swot_from_text(response_text)
        
        except Exception as e:
            logger.error(f"❌ SWOT 生成失败: {type(e).__name__} - {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            logger.warning("⚠️ API调用失败，使用文本解析作为备选方案")
            try:
                return self._extract_swot_from_full_report(full_report)
            except:
                return {
                    'strengths': [],
                    'weaknesses': [],
                    'opportunities': [],
                    'threats': []
                }
    
    def _parse_swot_from_text(self, text: str) -> Dict:
        """Parse SWOT analysis from plain text response."""
        logger.info("📝 解析 SWOT 文本内容...")
        logger.info(f"原始响应 (前500字符): {text[:500]}")
        
        swot = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }
        
        import re
        
        text_cleaned = re.sub(r'```json\s*', '', text)
        text_cleaned = re.sub(r'```\s*', '', text_cleaned)
        
        try:
            swot_data = json.loads(text_cleaned.strip())
            logger.info("✓ 清理后的文本成功解析为 JSON")
            return swot_data
        except json.JSONDecodeError:
            logger.info("✗ JSON 解析失败，使用文本模式")
        
        lines = text.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
                
            if '优势' in line or 'Strength' in line.lower() or '"strengths"' in line:
                current_category = 'strengths'
                logger.info(f"  🔍 找到优势部分")
            elif '劣势' in line or '弱点' in line or 'Weakness' in line.lower() or '"weaknesses"' in line:
                current_category = 'weaknesses'
                logger.info(f"  🔍 找到劣势部分")
            elif '机遇' in line or '机会' in line or 'Opportunit' in line or '"opportunities"' in line:
                current_category = 'opportunities'
                logger.info(f"  🔍 找到机遇部分")
            elif '威胁' in line or 'Threat' in line.lower() or '"threats"' in line:
                current_category = 'threats'
                logger.info(f"  🔍 找到威胁部分")
            elif current_category:
                if line.startswith('-') or line.startswith('•') or line.startswith('*') or re.match(r'^\d+[\.\)、]', line):
                    item = re.sub(r'^[-•*\d+\.\)、\s]+', '', line).strip()
                    item = item.strip('"\'、,，')
                    if item and len(item) > 2:
                        swot[current_category].append(item)
                        logger.info(f"    ✓ 添加项目: {item[:50]}...")
        
        logger.info(f"📊 解析结果统计:")
        logger.info(f"  - 优势: {len(swot['strengths'])} 项")
        logger.info(f"  - 劣势: {len(swot['weaknesses'])} 项")
        logger.info(f"  - 机遇: {len(swot['opportunities'])} 项")
        logger.info(f"  - 威胁: {len(swot['threats'])} 项")
        
        return swot
    
    def _extract_swot_from_full_report(self, full_report: str) -> Dict:
        """从完整报告中提取SWOT信息作为备选方案"""
        logger.info("📝 从报告内容中提取SWOT...")
        
        swot = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }
        
        # 简单的关键词提取
        lines = full_report.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(word in line for word in ['优势', '强项', '竞争力']):
                if len(line.strip()) > 10 and not line.startswith('#'):
                    swot['strengths'].append(line.strip())
            elif any(word in line for word in ['劣势', '不足', '短板', '弱点']):
                if len(line.strip()) > 10 and not line.startswith('#'):
                    swot['weaknesses'].append(line.strip())
            elif any(word in line for word in ['机遇', '机会', '潜力']):
                if len(line.strip()) > 10 and not line.startswith('#'):
                    swot['opportunities'].append(line.strip())
            elif any(word in line for word in ['威胁', '风险', '挑战']):
                if len(line.strip()) > 10 and not line.startswith('#'):
                    swot['threats'].append(line.strip())
        
        # 限制每个维度最多5条
        for key in swot:
            swot[key] = swot[key][:5]
        
        logger.info(f"✓ 从报告提取SWOT: 优势{len(swot['strengths'])}, 劣势{len(swot['weaknesses'])}, 机遇{len(swot['opportunities'])}, 威胁{len(swot['threats'])}")
        return swot
    
    def answer_question(self, report_content: str, question: str) -> str:
        """Answer a specific question about the report."""
        try:
            qa_prompt = f"""基于以下产业分析报告，回答用户的问题。
请提供准确、简洁的答案，并在可能的情况下引用报告中的具体内容。

报告内容：
{report_content[:4000]}

用户问题：{question}

请直接回答问题，不需要额外的格式说明。"""
            
            if self.llm_service == 'kimi':
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": qa_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=1000
                )
                return completion.choices[0].message.content
            elif self.llm_service == 'gemini':
                response = self.client.generate_content(qa_prompt)
                return response.text
        
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return f"抱歉，回答问题时出现错误：{str(e)}"
    def _check_key_rotation_and_reinit(self, service_name: str):
        api_keys_cfg = self.config.get('api_keys', {})
        current = None
        if service_name == 'kimi':
            current = (
                api_keys_cfg.get('kimi')
                or api_keys_cfg.get('kimi_api_key')
                or os.environ.get('KIMI_API_KEY')
                or os.environ.get('MOONSHOT_API_KEY')
            )
        elif service_name == 'gemini':
            current = (
                api_keys_cfg.get('google_gemini')
                or api_keys_cfg.get('google_gemini_api_key')
                or os.environ.get('GOOGLE_GEMINI_API_KEY')
            )
        if current and current != getattr(self, 'api_key', None):
            logger.info(f"检测到 {service_name.upper()} API Key 发生变更，正在重新初始化客户端...")
            if service_name == 'kimi':
                with self._client_lock:
                    self.client = OpenAI(api_key=current, base_url="https://api.moonshot.cn/v1")
                self.api_key = current
            elif service_name == 'gemini':
                genai.configure(api_key=current)
                with self._client_lock:
                    self.client = genai.GenerativeModel('gemini-1.5-pro-latest')
                self.api_key = current
