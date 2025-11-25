#!/usr/bin/env python3
"""
Streaming LLM Report Generator with real-time content streaming support
Provides streaming capabilities for Google Gemini and Kimi APIs
"""

import os
import json
import logging
import time
import asyncio
from typing import Dict, Optional, AsyncIterator, Iterator
from pathlib import Path
from openai import OpenAI
import google.generativeai as genai
from src.utils.api_error_handler import api_error_handler, handle_api_error, APIError, APIService

logger = logging.getLogger(__name__)


class StreamingLLMReportGenerator:
    """Streaming LLM Report Generator with real-time content streaming support"""
    
    def __init__(self, config_path='config.json', llm_service: str = 'kimi', enable_fallback=True):
        """Initialize the streaming LLM report generator
        
        Args:
            config_path: Path to configuration file containing API keys
            llm_service: The LLM service to use ('kimi', 'gemini', or 'doubao')
            enable_fallback: Whether to enable service fallback on failures
        """
        logger.info("="*60)
        logger.info(f"初始化 {llm_service.upper()} 流式 LLM 报告生成器")
        logger.info("="*60)
        
        self.config = self._load_config(config_path)
        self.llm_service = llm_service
        self.enable_fallback = enable_fallback
        self.api_error_handler = api_error_handler
        self.available_services = self._detect_available_services()
        self.current_service = self._get_service_enum(llm_service)
        
        # Streaming configuration
        self.chunk_size = 1024  # Stream chunk size in characters
        self.streaming_timeout = 30  # Timeout for streaming in seconds
        # Simple rate limiter state
        self._last_call_ts = {}
        self._min_interval_sec = {
            APIService.KIMI: float(os.environ.get('KIMI_MIN_INTERVAL', 0.5)),
            APIService.GEMINI: float(os.environ.get('GEMINI_MIN_INTERVAL', 0.5)),
        }
        
        # Initialize clients
        logger.info(f"Initializing clients for service: {self.llm_service}")
        self._initialize_clients()
        
        logger.info(f"✅ {self.llm_service.upper()} 流式 LLM 报告生成器初始化完成")
        logger.info(f"Available services: {[s.value for s in self.available_services]}")
        logger.info(f"Current service: {self.current_service.value}")
    
    def _get_service_enum(self, service_name: str) -> APIService:
        """Convert service name to enum"""
        try:
            return APIService(service_name.lower())
        except ValueError:
            logger.warning(f"未知服务类型: {service_name}，默认使用 Kimi")
            return APIService.KIMI
    
    def _detect_available_services(self) -> list:
        """Detect which services have valid API keys configured"""
        available = []
        
        api_keys_cfg = self.config.get('api_keys', {})
        if api_keys_cfg.get('kimi') or api_keys_cfg.get('kimi_api_key') or os.environ.get('KIMI_API_KEY') or os.environ.get('MOONSHOT_API_KEY'):
            available.append(APIService.KIMI)
        
        if api_keys_cfg.get('google_gemini') or api_keys_cfg.get('google_gemini_api_key') or os.environ.get('GOOGLE_GEMINI_API_KEY'):
            available.append(APIService.GEMINI)
        
        if api_keys_cfg.get('doubao_api_key'):
            available.append(APIService.DOUBAO)
        
        logger.info(f"✅ 检测到可用服务: {[s.value for s in available]}")
        return available
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _initialize_clients(self):
        """Initialize API clients for all available services"""
        self.clients = {}
        
        # Initialize Kimi client
        if APIService.KIMI in self.available_services:
            try:
                api_keys_cfg = self.config.get('api_keys', {})
                logger.info(f"API keys config: {api_keys_cfg}")
                api_key = (
                    api_keys_cfg.get('kimi')
                    or api_keys_cfg.get('kimi_api_key')
                    or os.environ.get('KIMI_API_KEY')
                    or os.environ.get('MOONSHOT_API_KEY')
                )
                logger.info(f"Selected Kimi API key (first 10 chars): {api_key[:10] if api_key else 'None'}")
                if api_key:
                    self.clients[APIService.KIMI] = OpenAI(
                        api_key=api_key,
                        base_url="https://api.moonshot.cn/v1"
                    )
                    logger.info("✅ Kimi 客户端初始化成功")
            except Exception as e:
                logger.error(f"❌ Kimi 客户端初始化失败: {e}")
        else:
            logger.warning("未检测到Kimi密钥，Kimi不可用")
        
        # Initialize Gemini client
        if APIService.GEMINI in self.available_services:
            try:
                api_keys_cfg = self.config.get('api_keys', {})
                api_key = (
                    api_keys_cfg.get('google_gemini')
                    or api_keys_cfg.get('google_gemini_api_key')
                    or os.environ.get('GOOGLE_GEMINI_API_KEY')
                )
                if api_key:
                    genai.configure(api_key=api_key)
                    self.clients[APIService.GEMINI] = genai.GenerativeModel('gemini-1.5-flash-latest')
                    logger.info("✅ Gemini 客户端(gemini-1.5-flash-latest)初始化成功")
            except Exception as e:
                logger.error(f"❌ Gemini 客户端初始化失败: {e}")
        else:
            logger.info("Gemini未配置或不可用")
        
        # Initialize Doubao client (placeholder)
        if APIService.DOUBAO in self.available_services:
            self.clients[APIService.DOUBAO] = None
            logger.info("⚠️ 豆包大模型客户端为占位符")
    
    async def generate_report_streaming(self, city: str, industry: str, 
                                       additional_context: str = "") -> AsyncIterator[Dict]:
        """Generate report with streaming support, yielding content chunks in real-time
        
        Args:
            city: Target city name
            industry: Target industry name
            additional_context: Additional context or requirements
            
        Yields:
            Dictionary containing streaming data:
            - type: 'start', 'chunk', 'complete', 'error'
            - content: Text content (for chunks)
            - stage: Current processing stage
            - metadata: Additional information
        """
        try:
            logger.info("="*60)
            logger.info(f"🚀 开始流式生成报告: {city} - {industry}")
            logger.info("="*60)
            
            # Prepare prompt
            prompt = self._prepare_prompt(city, industry, additional_context)
            
            # Yield start signal
            yield {
                'type': 'start',
                'stage': 'generating',
                'message': '开始生成报告主体...',
                'metadata': {
                    'city': city,
                    'industry': industry,
                    'service': self.llm_service
                }
            }
            
            # Try to generate with current service
            async for chunk in self._generate_with_service_streaming(
                self.current_service, city, industry, prompt
            ):
                yield chunk
                
                # If we got a complete report, also generate summary and SWOT
                if chunk['type'] == 'complete':
                    full_content = chunk['content']
                    
                    # Generate summaries
                    async for summary_chunk in self._generate_summaries_streaming(full_content, city, industry):
                        yield summary_chunk
                    
                    # Generate SWOT analysis
                    async for swot_chunk in self._generate_swot_streaming(full_content, city, industry):
                        yield swot_chunk
                    
                    break
            
            logger.info("✅ 流式报告生成完成")
            
        except Exception as e:
            logger.error(f"❌ 流式报告生成失败: {e}")
            api_error = handle_api_error(e, self.llm_service, "流式报告生成")
            
            yield {
                'type': 'error',
                'error': str(e),
                'api_error': {
                    'type': api_error.error_type.value,
                    'user_message': api_error.user_friendly_message,
                    'suggested_action': api_error.suggested_action
                }
            }
    
    async def _generate_with_service_streaming(self, service: APIService, city: str, industry: str, 
                                             prompt: str) -> AsyncIterator[Dict]:
        """Generate content using the specified service with streaming"""
        
        service_name = service.value
        logger.info(f"🌐 开始流式调用 {service_name.upper()} API...")
        
        try:
            if service == APIService.KIMI:
                async for chunk in self._stream_kimi(prompt):
                    yield chunk
            elif service == APIService.GEMINI:
                async for chunk in self._stream_gemini(prompt):
                    yield chunk
            elif service == APIService.DOUBAO:
                async for chunk in self._stream_doubao(prompt):
                    yield chunk
            else:
                raise ValueError(f"不支持的流式服务: {service_name}")
                
        except Exception as e:
            logger.error(f"❌ {service_name.upper()} 流式调用失败: {e}")
            
            # If fallback is enabled, try other services
            if self.enable_fallback:
                fallback_service = self.api_error_handler.get_fallback_service(service, self.available_services)
                if fallback_service:
                    logger.info(f"🔄 回退到 {fallback_service.value.upper()} 服务...")
                    
                    yield {
                        'type': 'service_fallback',
                        'original_service': service_name,
                        'fallback_service': fallback_service.value,
                        'message': f'正在切换到 {fallback_service.value.upper()} 服务...'
                    }
                    
                    async for chunk in self._generate_with_service_streaming(fallback_service, city, industry, prompt):
                        yield chunk
                else:
                    raise Exception("没有可用的回退服务")
            else:
                raise e
    
    async def _stream_kimi(self, prompt: str) -> AsyncIterator[Dict]:
        """Stream content from Kimi API using OpenAI-compatible streaming"""
        logger.info("🌙 开始流式调用 Kimi API (OpenAI-compatible streaming)...")
        
        client = self.clients.get(APIService.KIMI)
        if not client:
            raise ValueError("Kimi 客户端未初始化")
        
        try:
            # Basic rate limiting: ensure minimal interval between calls
            now = time.time()
            last = self._last_call_ts.get(APIService.KIMI, 0)
            min_interval = self._min_interval_sec.get(APIService.KIMI, 0.5)
            if now - last < min_interval:
                await asyncio.sleep(min_interval - (now - last))
            self._last_call_ts[APIService.KIMI] = time.time()
            # Start streaming with OpenAI-compatible API
            attempts = 0
            err = None
            stream = None
            kimi_model = os.environ.get('KIMI_MODEL', 'moonshot-v1-128k')
            kimi_temp = float(os.environ.get('KIMI_TEMPERATURE', 0.7))
            kimi_max = int(os.environ.get('KIMI_MAX_TOKENS', 8000))
            while attempts < 2:
                attempts += 1
                try:
                    stream = client.chat.completions.create(
                        model=kimi_model,
                        messages=[
                            {
                                "role": "system",
                                "content": "你是一位专业的产业分析师，擅长撰写深度的区域产业分析报告。请基于用户提供的框架和要求，生成详实、专业的分析报告，文字长度在5000字以上。"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=kimi_temp,
                        max_tokens=kimi_max,
                        stream=True,
                        stream_options={
                            "include_usage": True
                        }
                    )
                    err = None
                    break
                except Exception as e:
                    err = e
                    await asyncio.sleep(1.0)
            if err and stream is None:
                raise err
            
            accumulated_content = ""
            chunk_count = 0
            
            # Process streaming response
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        content = delta.content
                        accumulated_content += content
                        chunk_count += 1
                        
                        # Add small delay to simulate natural streaming pace
                        await asyncio.sleep(0.03)
                        
                        # Yield streaming chunk
                        yield {
                            'type': 'chunk',
                            'content': content,
                            'accumulated': accumulated_content,
                            'chunk_index': chunk_count,
                            'stage': 'generating',
                            'timestamp': time.time()
                        }
            
            # Yield completion
            yield {
                'type': 'complete',
                'content': accumulated_content,
                'stage': 'generating',
                'metadata': {
                    'chunks': chunk_count,
                    'service': 'kimi',
                    'total_length': len(accumulated_content)
                }
            }
            
            logger.info(f"✅ Kimi 流式调用完成，共 {chunk_count} 个分块，总长度: {len(accumulated_content)}")
            
        except Exception as e:
            logger.error(f"❌ Kimi 流式调用失败: {e}")
            raise e
    
    async def _stream_gemini(self, prompt: str) -> AsyncIterator[Dict]:
        """Stream content from Google Gemini API using streamGenerateContent"""
        logger.info("🎯 开始流式调用 Google Gemini API (streamGenerateContent)...")
        
        client = self.clients.get(APIService.GEMINI)
        if not client:
            raise ValueError("Gemini 客户端未初始化")
        
        try:
            # Configure generation
            generation_config = {
                'temperature': 0.7,
                'max_output_tokens': 8000,
                'top_p': 0.8,
                'top_k': 40
            }
            
            # Start streaming generation - using the correct streamGenerateContent method
            response = client.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True  # This enables streamGenerateContent
            )
            
            accumulated_content = ""
            chunk_count = 0
            
            # Process streaming response
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    content = chunk.text
                    accumulated_content += content
                    chunk_count += 1
                    
                    # Add small delay to simulate natural streaming pace
                    await asyncio.sleep(0.05)
                    
                    # Yield streaming chunk
                    yield {
                        'type': 'chunk',
                        'content': content,
                        'accumulated': accumulated_content,
                        'chunk_index': chunk_count,
                        'stage': 'generating',
                        'timestamp': time.time()
                    }
            
            # Yield completion
            yield {
                'type': 'complete',
                'content': accumulated_content,
                'stage': 'generating',
                'metadata': {
                    'chunks': chunk_count,
                    'service': 'gemini',
                    'total_length': len(accumulated_content)
                }
            }
            
            logger.info(f"✅ Gemini 流式调用完成，共 {chunk_count} 个分块，总长度: {len(accumulated_content)}")
            
        except Exception as e:
            logger.error(f"❌ Gemini 流式调用失败: {e}")
            raise e
    
    async def _stream_doubao(self, prompt: str) -> AsyncIterator[Dict]:
        """Stream content from Doubao API (placeholder)"""
        logger.warning("⚠️ 豆包大模型流式 API 调用尚未完全实现")
        
        # For now, simulate streaming with delays
        test_content = "【豆包大模型流式内容占位符】\n\n"
        test_content += "这是一个模拟的流式响应，用于测试系统功能。\n\n"
        test_content += "实际实现时，这里将包含豆包大模型生成的真实内容。\n\n"
        
        accumulated_content = ""
        
        # Simulate streaming chunks
        for i, char in enumerate(test_content):
            accumulated_content += char
            
            yield {
                'type': 'chunk',
                'content': char,
                'accumulated': accumulated_content,
                'chunk_index': i + 1,
                'stage': 'generating'
            }
            
            # Small delay to simulate streaming
            await asyncio.sleep(0.01)
        
        # Yield completion
        yield {
            'type': 'complete',
            'content': accumulated_content,
            'stage': 'generating',
            'metadata': {
                'chunks': len(test_content),
                'service': 'doubao'
            }
        }
    
    async def _generate_summaries_streaming(self, full_content: str, city: str, industry: str) -> AsyncIterator[Dict]:
        """Generate summaries with streaming support"""
        
        # Chinese summary
        yield {
            'type': 'start',
            'stage': 'summary_zh',
            'message': '正在生成中文执行摘要...'
        }
        
        summary_prompt_zh = f"""请基于以下完整的产业分析报告，生成一份简洁的执行摘要（Executive Summary），
长度控制在300-500字，包含：
1. 核心发现（2-3点）
2. 关键数据指标（2-3个）
3. 主要建议（2-3条）

报告内容：
{full_content[:3000]}

请直接输出摘要内容，不需要额外的格式说明。"""
        
        accumulated_summary_zh = ""
        
        if self.current_service == APIService.KIMI:
            async for chunk in self._stream_kimi(summary_prompt_zh):
                if chunk['type'] == 'chunk':
                    accumulated_summary_zh += chunk['content']
                    yield {
                        'type': 'summary_chunk',
                        'content': chunk['content'],
                        'language': 'zh',
                        'accumulated': accumulated_summary_zh
                    }
        elif self.current_service == APIService.GEMINI:
            async for chunk in self._stream_gemini(summary_prompt_zh):
                if chunk['type'] == 'chunk':
                    accumulated_summary_zh += chunk['content']
                    yield {
                        'type': 'summary_chunk',
                        'content': chunk['content'],
                        'language': 'zh',
                        'accumulated': accumulated_summary_zh
                    }
        
        yield {
            'type': 'summary_complete',
            'content': accumulated_summary_zh,
            'language': 'zh'
        }
        
        # English summary
        yield {
            'type': 'start',
            'stage': 'summary_en',
            'message': '正在生成英文执行摘要...'
        }
        
        summary_prompt_en = f"""Based on the following industrial analysis report, 
generate a concise Executive Summary in English (200-300 words) including:
1. Key findings (2-3 points)
2. Critical metrics (2-3 items)
3. Main recommendations (2-3 items)

Report content:
{full_content[:3000]}

Please output the summary directly without additional formatting instructions."""
        
        accumulated_summary_en = ""
        
        if self.current_service == APIService.KIMI:
            async for chunk in self._stream_kimi(summary_prompt_en):
                if chunk['type'] == 'chunk':
                    accumulated_summary_en += chunk['content']
                    yield {
                        'type': 'summary_chunk',
                        'content': chunk['content'],
                        'language': 'en',
                        'accumulated': accumulated_summary_en
                    }
        elif self.current_service == APIService.GEMINI:
            async for chunk in self._stream_gemini(summary_prompt_en):
                if chunk['type'] == 'chunk':
                    accumulated_summary_en += chunk['content']
                    yield {
                        'type': 'summary_chunk',
                        'content': chunk['content'],
                        'language': 'en',
                        'accumulated': accumulated_summary_en
                    }
        
        yield {
            'type': 'summary_complete',
            'content': accumulated_summary_en,
            'language': 'en'
        }
    
    async def _generate_swot_streaming(self, full_content: str, city: str, industry: str) -> AsyncIterator[Dict]:
        """Generate SWOT analysis with streaming support"""
        
        yield {
            'type': 'start',
            'stage': 'swot',
            'message': '正在生成 SWOT 分析...'
        }
        
        swot_prompt = f"""请基于以下产业分析报告，生成详细的SWOT战略分析。

要求：
1. 每个维度（优势、劣势、机遇、威胁）至少列出4-6个要点
2. 要点要具体、可操作、有洞察力
3. 结合报告中的具体数据和案例
4. 严格按照JSON格式输出

输出格式：
{{
    "strengths": ["优势1：具体描述...", "优势2：具体描述..."],
    "weaknesses": ["劣势1：具体描述...", "劣势2：具体描述..."],
    "opportunities": ["机遇1：具体描述...", "机遇2：具体描述..."],
    "threats": ["威胁1：具体描述...", "威胁2：具体描述..."]
}}

报告内容：
{full_content[:4000]}

请只输出JSON格式的内容，不要包含markdown代码块标记或其他说明文字。"""
        
        accumulated_swot = ""
        
        if self.current_service == APIService.KIMI:
            async for chunk in self._stream_kimi(swot_prompt):
                if chunk['type'] == 'chunk':
                    accumulated_swot += chunk['content']
                    yield {
                        'type': 'swot_chunk',
                        'content': chunk['content'],
                        'accumulated': accumulated_swot
                    }
        elif self.current_service == APIService.GEMINI:
            async for chunk in self._stream_gemini(swot_prompt):
                if chunk['type'] == 'chunk':
                    accumulated_swot += chunk['content']
                    yield {
                        'type': 'swot_chunk',
                        'content': chunk['content'],
                        'accumulated': accumulated_swot
                    }
        
        yield {
            'type': 'swot_complete',
            'content': accumulated_swot
        }
    
    def _prepare_prompt(self, city: str, industry: str, additional_context: str) -> str:
        """Prepare the prompt by replacing placeholders"""
        template_path = Path('industry_analysis_llm_prompt.md')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            prompt_template = self._get_default_prompt_template()
        
        prompt = prompt_template
        prompt = prompt.replace('[目标城市]', city)
        prompt = prompt.replace('[目标行业]', industry)
        
        if additional_context:
            prompt += f"\n\n补充信息和要求：\n{additional_context}"
        
        prompt += "\n\n请按照上述框架，生成一份详细、专业的产业分析报告。报告应包含具体的数据、案例和洞察。"
        
        return prompt
    
    def _get_default_prompt_template(self) -> str:
        """Get default prompt template if file is not available"""
        return """请生成一份关于[目标城市] [目标行业]的产业分析报告，包含以下章节：

1. 执行摘要
2. 产业概览与核心数据
3. 政策环境分析
4. 产业生态与关键参与者
5. 产业链分析
6. AI融合潜力分析
7. 结论与建议

请提供详细、专业的分析内容。"""
    
    def _parse_report_sections(self, content: str) -> Dict:
        """Parse the generated report into structured sections"""
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


# Import asyncio for async functionality
import asyncio


# Convenience function for synchronous streaming
def generate_report_streaming_sync(city: str, industry: str, 
                                 additional_context: str = "",
                                 llm_service: str = 'kimi',
                                 enable_fallback: bool = True) -> Iterator[Dict]:
    """Synchronous wrapper for streaming report generation"""
    
    async def _async_generator():
        generator = StreamingLLMReportGenerator(
            llm_service=llm_service,
            enable_fallback=enable_fallback
        )
        async for chunk in generator.generate_report_streaming(city, industry, additional_context):
            yield chunk
    
    # Run async generator in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        async_gen = _async_generator()
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
    finally:
        loop.close()


# Global streaming generator instance
streaming_generator = StreamingLLMReportGenerator()