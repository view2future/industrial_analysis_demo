#!/usr/bin/env python3
"""
Background tasks for report generation
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")

import json
import logging
from datetime import datetime
from pathlib import Path
from .celery_app import celery_app
from src.ai.llm_generator import LLMReportGenerator
from src.utils.api_error_handler import handle_api_error, api_error_handler
from src.utils.notification_service import notification_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='generate_llm_report', max_retries=3, default_retry_delay=60)
def generate_llm_report_task(self, city: str, industry: str, 
                             additional_context: str = "",
                             user_id: str = None,
                             initial_report_id: str = None,
                             llm_service: str = 'kimi',
                             **kwargs):
    """Background task to generate LLM report with comprehensive error handling and user notifications.
    
    Args:
        city: Target city name
        industry: Target industry name
        additional_context: Additional context or requirements
        user_id: User ID who requested the report
        initial_report_id: Initial report ID created in the web request
        llm_service: LLM service to use (kimi, gemini, etc.)
        **kwargs: Additional arguments (ignored)
    
    Returns:
        Dictionary with task result including report_id and status
    """
    try:
        logger.info("="*80)
        logger.info("🚀 后台任务开始: 生成 LLM 报告")
        logger.info("="*80)
        logger.info(f"📍 城市: {city}")
        logger.info(f"🏭 行业: {industry}")
        logger.info(f"👤 用户ID: {user_id}")
        logger.info(f"🆔 初始报告ID: {initial_report_id}")
        logger.info(f"📝 补充信息: {additional_context[:100] if additional_context else '无'}")
        
        # Update task state - INIT
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 10, 
                'total': 100, 
                'status': f'🔧 初始化 {llm_service.upper()} API...',
                'stage': 'init',
                'message': f'正在初始化 {llm_service.upper()} LLM 报告生成器'
            }
        )
        
        # Initialize LLM generator with fallback support
        logger.info(f"\n📦 正在初始化 {llm_service.upper()} LLM 报告生成器...")
        try:
            generator = LLMReportGenerator(llm_service=llm_service, enable_fallback=True)
            logger.info(f"✅ {llm_service.upper()} LLM 报告生成器初始化完成")
        except Exception as e:
            logger.error(f"❌ LLM 报告生成器初始化失败: {e}")
            api_error = handle_api_error(e, llm_service, "初始化阶段")
            
            # 通知用户
            notification_service.notify_api_connection_error(
                llm_service, str(e), user_id=user_id
            )
            
            raise Exception(f"LLM 报告生成器初始化失败: {api_error.user_friendly_message}")
        
        # Store model name for metadata
        self.model_name = getattr(generator, 'model_name', llm_service)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 20, 
                'total': 100, 
                'status': f'🌐 调用 {llm_service.upper()} API 生成 {city} {industry} 报告...',
                'stage': 'generating',
                'message': f'正在使用 {llm_service.upper()} API 生成 {city} {industry} 产业分析报告',
                'model': getattr(self, 'model_name', None),
                'service': llm_service
            }
        )
        logger.info('🌐 开始调用 %s API...', llm_service.upper())
        
        # Generate the main report with comprehensive error handling
        logger.info('🌐 开始调用 %s API...', llm_service.upper())
        
        try:
            report_result = generator.generate_report(city, industry, additional_context)
            
            if not report_result.get('success'):
                error_msg = report_result.get('error', '报告生成失败')
                logger.error(f"❌ 报告生成失败: {error_msg}")
                
                # 检查是否是 API 错误
                api_error_info = report_result.get('api_error')
                if api_error_info:
                    # 通知用户 API 错误
                    if api_error_info['type'] == 'quota_exceeded':
                        notification_service.notify_api_quota_exceeded(
                            api_error_info['service'], user_id, 
                            api_error_info.get('suggested_action', '')
                        )
                    else:
                        notification_service.notify_api_connection_error(
                            api_error_info['service'], 
                            api_error_info.get('user_message', error_msg), 
                            user_id
                        )
                
                raise Exception(f"报告生成失败: {error_msg}")
                
        except Exception as e:
            logger.error(f"❌ 报告生成过程异常: {e}")
            
            # 使用错误处理器分析错误
            api_error = handle_api_error(e, llm_service, "报告生成")
            
            # 通知用户
            if api_error.error_type.value == 'quota_exceeded':
                notification_service.notify_api_quota_exceeded(
                    llm_service, user_id, api_error.suggested_action
                )
            elif api_error_handler.is_connection_issue(api_error.service, e):
                notification_service.notify_api_connection_error(
                    llm_service, api_error.user_friendly_message, user_id
                )
            else:
                # 通用错误通知
                notification_service.notify_report_generation_result(
                    False, city, industry, llm_service, user_id, str(e)
                )
            
            # 如果启用了回退但仍然失败，提供更详细的错误信息
            if hasattr(generator, 'enable_fallback') and generator.enable_fallback:
                error_msg = f"报告生成失败（已尝试回退到所有可用服务）。{api_error.user_friendly_message}"
            else:
                error_msg = f"报告生成失败。{api_error.user_friendly_message}"
            
            raise Exception(error_msg)
        
        logger.info(f"✅ {llm_service.upper()} API 调用成功，报告主体已生成")
        
        # 记录实际使用的服务
        actual_service = report_result.get('used_service', llm_service)
        attempted_services = report_result.get('attempted_services', [llm_service])
        
        if actual_service != llm_service:
            logger.info(f"🔄 通过回退机制使用了 {actual_service.upper()} 服务")
            # 通知用户服务回退成功
            notification_service.notify_service_fallback(
                llm_service, actual_service, True, user_id
            )
        
        logger.info(f"📋 尝试过的服务: {[s.upper() for s in attempted_services]}")
        
        # Update progress - Report generated
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 60,
                'total': 100,
                'status': '✅ 报告主体生成完成',
                'stage': 'report_done',
                'message': f'报告主体已生成，共 {len(report_result["full_content"])} 字'
            }
        )
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 65, 
                'total': 100, 
                'status': '📝 生成中文摘要...',
                'stage': 'summary_zh',
                'message': '正在生成中文执行摘要'
            }
        )
        logger.info("\n📝 正在生成执行摘要...")
        
        # Generate summary in both languages
        summary_zh = generator.generate_summary(report_result['full_content'], 'zh')
        
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 73, 
                'total': 100, 
                'status': '📝 生成英文摘要...',
                'stage': 'summary_en',
                'message': '正在生成英文执行摘要'
            }
        )
        summary_en = generator.generate_summary(report_result['full_content'], 'en')
        logger.info("✅ 摘要生成完成（中英文）")
        
        # Update progress - Summaries done
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 80,
                'total': 100,
                'status': '✅ 摘要生成完成',
                'stage': 'summary_done',
                'message': '中英文摘要已生成'
            }
        )
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 85, 
                'total': 100, 
                'status': '📊 生成 SWOT 分析...',
                'stage': 'swot',
                'message': '正在生成优劣势分析'
            }
        )
        logger.info("\n📊 正在生成 SWOT 分析...")
        
        # Generate SWOT analysis
        swot = generator.generate_swot_analysis(report_result['full_content'])
        logger.info("✅ SWOT 分析生成完成")
        
        # Update progress - SWOT done
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 92,
                'total': 100,
                'status': '✅ SWOT 分析完成',
                'stage': 'swot_done',
                'message': 'SWOT 分析已生成'
            }
        )
        
        # Prepare final report data
        # Use initial_report_id if provided, otherwise generate new timestamp
        if initial_report_id:
            report_id = initial_report_id
            logger.info(f"📋 使用初始报告ID: {report_id}")
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_id = f"llm_report_{timestamp}"
            logger.info(f"📋 生成新报告ID: {report_id}")
        
        final_report = {
            'report_id': report_id,
            'city': city,
            'industry': industry,
            'generated_at': datetime.now().isoformat(),
            'full_content': report_result['full_content'],
            'sections': report_result['sections'],
            'summary': {
                'zh': summary_zh,
                'en': summary_en
            },
            'swot_analysis': swot,
            'metadata': {
                'model': self.model_name if hasattr(generator, 'model_name') else llm_service,
                'llm_service': llm_service,
                'user_id': user_id,
                'additional_context': additional_context
            }
        }
        
        # Save report to file
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 95,
                'total': 100,
                'status': '💾 保存报告文件...',
                'stage': 'saving',
                'message': f'正在保存报告到 {report_id}.json'
            }
        )
        
        logger.info(f"\n💾 保存报告到文件...")
        
        # Get app_root_path from kwargs if provided
        app_root_path = kwargs.get('app_root_path')
        
        if app_root_path:
            output_dir = Path(app_root_path) / 'data' / 'output' / 'llm_reports'
        else:
            output_dir = Path('data/output/llm_reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{report_id}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 报告已保存: {output_path}")
        logger.info(f"📏 文件大小: {output_path.stat().st_size / 1024:.2f} KB")
        
        # Update progress - Saving done
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 98,
                'total': 100,
                'status': '✅ 报告已保存',
                'stage': 'saving_done',
                'message': f'报告文件已保存: {output_path.stat().st_size / 1024:.2f} KB'
            }
        )
        
        logger.info("="*80)
        logger.info("🎉 LLM 报告生成任务完成！")
        logger.info("="*80)
        
        # 通知用户报告生成成功
        notification_service.notify_report_generation_result(
            True, city, industry, actual_service, user_id
        )
        
        # Update progress to complete with all information
        self.update_state(
            state='SUCCESS',
            meta={
                'current': 100, 
                'total': 100, 
                'status': '✅ 报告生成完成！',
                'stage': 'completed',
                'message': '所有处理已完成，正在跳转到报告页面...',
                'report_id': report_id,
                'file_path': str(output_path),
                'file_size': f"{output_path.stat().st_size / 1024:.2f} KB",
                'city': city,
                'industry': industry,
                'generated_at': final_report['generated_at'],
                'model': self.model_name,
                'service': llm_service
            }
        )
        
        return {
            'success': True,
            'report_id': report_id,
            'file_path': str(output_path),
            'city': city,
            'industry': industry,
            'generated_at': final_report['generated_at'],
            'service_used': actual_service,
            'attempted_services': attempted_services
        }
    
    except Exception as e:
        logger.error("="*80)
        logger.error("❌ LLM 报告生成任务失败")
        logger.error("="*80)
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        
        import traceback
        logger.error("完整堆栈跟踪:")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),
                'traceback': traceback.format_exc(),
                'status': f'任务失败: {str(e)}'
            })
        return {
            'success': False,
            'error': str(e)
        }
