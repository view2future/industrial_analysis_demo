#!/usr/bin/env python3
"""
Streaming routes for real-time content generation
Provides Server-Sent Events (SSE) endpoints for streaming LLM responses
"""

import json
import logging
import time
import asyncio
import threading
from queue import Queue, Empty
from flask import Blueprint, Response, request, jsonify, stream_with_context
from flask_login import login_required, current_user
from src.ai.streaming_llm_generator import StreamingLLMReportGenerator
from src.utils.api_error_handler import handle_api_error, APIError

logger = logging.getLogger(__name__)

streaming_bp = Blueprint('streaming', __name__)


def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as Server-Sent Event"""
    event_data = {
        'type': event_type,
        'data': data,
        'timestamp': time.time()
    }
    return f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"


@streaming_bp.route('/api/stream/generate-report', methods=['POST'])
def stream_generate_report():
    """
    Stream report generation using Server-Sent Events
    Provides real-time content streaming to frontend
    """
    try:
        # Log request details
        logger.info(f"🎯 收到流式报告生成请求: {request.method} {request.url}")
        logger.info(f"Content-Type: {request.headers.get('Content-Type', 'Not set')}")
        
        # Log authentication status
        from flask_login import current_user
        logger.info(f"User authentication status: authenticated={getattr(current_user, 'is_authenticated', False)}, user_id={getattr(current_user, 'id', 'N/A')}")
        
        data = request.get_json()
        logger.info(f"Request data received: {data}")
        
        # Log available services
        try:
            from src.ai.streaming_llm_generator import StreamingLLMReportGenerator
            from pathlib import Path
            app_root = Path(__file__).parent.parent.parent
            cfg_path = str(app_root / 'config.json')
            temp_generator = StreamingLLMReportGenerator(config_path=cfg_path, llm_service='kimi')
            logger.info(f"Available services: {[s.value for s in temp_generator.available_services]}")
            logger.info(f"Current service: {temp_generator.current_service.value}")
        except Exception as e:
            logger.error(f"Error checking available services: {e}")
        
        if not data:
            logger.warning("No JSON data provided in streaming request")
            return jsonify({'error': 'No JSON data provided'}), 400
        
        city = data.get('city', '').strip()
        industry = data.get('industry', '').strip()
        additional_context = data.get('additional_context', '')
        llm_service = data.get('llm_service', 'kimi')
        
        logger.info(f"请求参数 - city: '{city}', industry: '{industry}', llm_service: '{llm_service}', additional_context: '{additional_context[:50]}...'")
        
        # Validate input
        if not city or not industry:
            logger.warning(f"Missing required parameters: city={city}, industry={industry}")
            return jsonify({'error': 'City and industry are required'}), 400
        
        logger.info(f"🚀 开始流式报告生成: {city} - {industry} (服务: {llm_service})")
        
        def generate_stream():
            """Generator function for SSE streaming with true async support"""
            try:
                # Create a queue for communication between async and sync
                chunk_queue = Queue()
                
                async def async_generate():
                    """Async generator function"""
                    try:
                        # Send start event ASAP to avoid frontend waiting forever
                        start_event = format_sse_event('generation_start', {
                            'message': '开始生成报告...',
                            'city': city,
                            'industry': industry,
                            'service': llm_service
                        })
                        chunk_queue.put(start_event.encode('utf-8'))
                        
                        # Initialize streaming generator (use absolute config path if available)
                        from pathlib import Path
                        app_root = Path(__file__).parent.parent.parent
                        cfg_path = str(app_root / 'config.json')
                        logger.info(f"Initializing StreamingLLMReportGenerator with config path: {cfg_path}")

                        # Initialize generator with timeout protection
                        try:
                            generator = StreamingLLMReportGenerator(
                                config_path=cfg_path,
                                llm_service=llm_service,
                                enable_fallback=True
                            )
                            logger.info(f"Generator initialized successfully. Available services: {[s.value for s in generator.available_services]}")
                        except Exception as init_error:
                            logger.error(f"Generator initialization failed: {init_error}")
                            # Check if it's an API key or connection issue
                            from src.utils.api_error_handler import handle_api_error, APIService
                            api_error = handle_api_error(init_error, llm_service, context='generator_initialization')

                            error_data = {
                                'error': api_error.user_friendly_message,
                                'type': 'api_error',
                                'raw': str(init_error),
                                'suggested_action': api_error.suggested_action,
                                'retry_after': api_error.retry_after,
                                'service': api_error.service.value,
                                'error_type': api_error.error_type.value
                            }
                            err_event = format_sse_event('error', error_data)
                            chunk_queue.put(err_event.encode('utf-8'))
                            chunk_queue.put(None)
                            return

                        # If requested service not available, emit clear error and stop
                        from src.utils.api_error_handler import APIService
                        requested_service_enum = APIService(llm_service.lower()) if llm_service.lower() in [s.value for s in APIService] else APIService.KIMI
                        if requested_service_enum not in generator.available_services:
                            service_name = requested_service_enum.value
                            err_event = format_sse_event('error', {
                                f'error': f'{service_name.capitalize()} 密钥未配置或无效，无法初始化客户端',
                                'type': 'authentication_error',
                                'service': service_name
                            })
                            chunk_queue.put(err_event.encode('utf-8'))
                            chunk_queue.put(None)
                            return
                        
                        # Stream the generation process
                        async for chunk in generator.generate_report_streaming(
                            city, industry, additional_context
                        ):
                            sse_event = format_sse_event('report_chunk', chunk)
                            chunk_queue.put(sse_event.encode('utf-8'))
                            
                            # Control streaming pace
                            await asyncio.sleep(0.05)
                        
                        # Send completion event
                        final_event = format_sse_event('report_complete', {
                            'message': '报告生成完成',
                            'city': city,
                            'industry': industry,
                            'service': llm_service
                        })
                        chunk_queue.put(final_event.encode('utf-8'))
                        
                    except Exception as e:
                        logger.error(f"❌ 异步生成失败: {e}")
                        try:
                            from src.utils.api_error_handler import handle_api_error
                            api_err = handle_api_error(e, llm_service, context='stream_generate_report')
                            error_data = {
                                'error': api_err.user_friendly_message,
                                'type': 'api_error',
                                'raw': str(e),
                                'suggested_action': api_err.suggested_action,
                                'retry_after': api_err.retry_after,
                                'service': api_err.service.value,
                                'error_type': api_err.error_type.value
                            }
                        except Exception:
                            error_data = {
                                'error': str(e),
                                'type': 'generation_error'
                            }
                        error_event = format_sse_event('error', error_data)
                        chunk_queue.put(error_event.encode('utf-8'))
                    finally:
                        chunk_queue.put(None)  # Sentinel to indicate completion
                
                # Run async function in a separate thread
                def run_async():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(async_generate())
                    finally:
                        loop.close()
                
                thread = threading.Thread(target=run_async)
                thread.start()
                
                # Yield chunks as they become available
                while True:
                    try:
                        chunk = chunk_queue.get(timeout=30)  # 30 second timeout
                        if chunk is None:  # Sentinel value
                            break
                        yield chunk
                    except Empty:
                        logger.warning("⏰ 流式生成超时")
                        break
                
                thread.join(timeout=10)  # Wait for thread to complete
                
            except Exception as e:
                logger.error(f"❌ 流式生成失败: {e}")
                try:
                    from src.utils.api_error_handler import handle_api_error
                    api_err = handle_api_error(e, llm_service, context='stream_outer')
                    error_data = {
                        'error': api_err.user_friendly_message,
                        'type': 'api_error',
                        'raw': str(e),
                        'suggested_action': api_err.suggested_action,
                        'retry_after': api_err.retry_after,
                        'service': api_err.service.value,
                        'error_type': api_err.error_type.value
                    }
                except Exception:
                    error_data = {
                        'error': str(e),
                        'type': 'streaming_error'
                    }
                error_event = format_sse_event('error', error_data)
                yield error_event.encode('utf-8')
        
        # Return SSE response
        return Response(
            stream_with_context(generate_stream()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',  # Disable Nginx buffering
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization'
            }
        )
        
    except Exception as e:
        logger.error(f"❌ 流式请求处理失败: {e}")
        return jsonify({
            'error': 'Failed to process streaming request',
            'details': str(e)
        }), 500


@streaming_bp.route('/api/stream/test', methods=['GET'])
def test_stream():
    """Test endpoint for streaming functionality"""
    def test_events():
        for i in range(5):
            data = {
                'message': f'Test message {i + 1}',
                'timestamp': time.time()
            }
            yield format_sse_event('test', data).encode('utf-8')
            time.sleep(1)
    
    return Response(
        test_events(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@streaming_bp.route('/api/stream/health', methods=['GET'])
def stream_health():
    """Health check for streaming service"""
    return jsonify({
        'status': 'healthy',
        'streaming_enabled': True,
        'timestamp': time.time()
    })