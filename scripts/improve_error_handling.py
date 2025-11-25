#!/usr/bin/env python3
"""
Improve error handling in the celery task to prevent missing files
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.tasks.report_tasks import generate_llm_report_task
from datetime import datetime
import json

def create_improved_task():
    """Create an improved version of the celery task with better error handling"""
    
    improved_code = '''#!/usr/bin/env python3
"""
Background tasks for report generation - IMPROVED VERSION with better error handling
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from .celery_app import celery_app
from src.ai.llm_generator import LLMReportGenerator

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='generate_llm_report_improved')
def generate_llm_report_task_improved(self, city: str, industry: str, 
                             additional_context: str = "",
                             user_id: str = None,
                             initial_report_id: str = None,
                             llm_service: str = 'kimi',
                             **kwargs):
    """Background task to generate LLM report with improved error handling.
    
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
        logger.info("🚀 后台任务开始: 生成 LLM 报告 (改进版)")
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
        
        # Initialize LLM generator
        logger.info(f"\\n📦 正在初始化 {llm_service.upper()} LLM 报告生成器...")
        generator = LLMReportGenerator(llm_service=llm_service)
        logger.info(f"✅ {llm_service.upper()} LLM 报告生成器初始化完成")
        
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
                'message': f'正在使用 {llm_service.upper()} API 生成 {city} {industry} 产业分析报告'
            }
        )
        logger.info('🌐 开始调用 %s API...', llm_service.upper())
        
        # Generate the main report
        report_result = generator.generate_report(city, industry, additional_context)
        
        if not report_result.get('success'):
            error_msg = report_result.get('error', '报告生成失败')
            logger.error(f"❌ 报告生成失败: {error_msg}")
            raise Exception(error_msg)
        
        logger.info("✅ Kimi API 调用成功，报告主体已生成")
        
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
        logger.info("\\n📝 正在生成执行摘要...")
        
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
        logger.info("\\n📊 正在生成 SWOT 分析...")
        
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
        
        # Save report to file - WITH IMPROVED ERROR HANDLING
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
        
        logger.info(f"\\n💾 保存报告到文件...")
        
        # Get app_root_path from kwargs if provided
        app_root_path = kwargs.get('app_root_path')
        
        if app_root_path:
            output_dir = Path(app_root_path) / 'data' / 'output' / 'llm_reports'
        else:
            output_dir = Path('data/output/llm_reports')
        
        # IMPROVED ERROR HANDLING FOR DIRECTORY CREATION
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ 输出目录已确认: {output_dir}")
        except Exception as e:
            logger.error(f"❌ 无法创建输出目录 {output_dir}: {e}")
            raise Exception(f"无法创建输出目录: {e}")
        
        output_path = output_dir / f"{report_id}.json"
        
        # IMPROVED FILE WRITING WITH VERIFICATION
        try:
            # Write the file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 报告已保存: {output_path}")
            
            # VERIFY THE FILE WAS ACTUALLY WRITTEN
            if not output_path.exists():
                raise Exception(f"文件写入后不存在: {output_path}")
            
            file_size = output_path.stat().st_size
            if file_size == 0:
                raise Exception(f"文件大小为0，可能写入失败: {output_path}")
            
            logger.info(f"📏 文件大小: {file_size / 1024:.2f} KB")
            
            # VERIFY FILE CAN BE READ
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                logger.info(f"✅ 文件验证成功，包含 {len(test_data)} 个顶级键")
            except Exception as e:
                raise Exception(f"文件验证失败，无法读取JSON: {e}")
            
        except Exception as e:
            logger.error(f"❌ 文件保存失败: {e}")
            raise Exception(f"报告文件保存失败: {e}")
        
        # Update progress - Saving done
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 98,
                'total': 100,
                'status': '✅ 报告已保存',
                'stage': 'saving_done',
                'message': f'报告文件已保存: {file_size / 1024:.2f} KB'
            }
        )
        
        logger.info("="*80)
        logger.info("🎉 LLM 报告生成任务完成！")
        logger.info("="*80)
        
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
                'file_size': f"{file_size / 1024:.2f} KB",
                'city': city,
                'industry': industry,
                'generated_at': final_report['generated_at']
            }
        )
        
        return {
            'success': True,
            'report_id': report_id,
            'file_path': str(output_path),
            'city': city,
            'industry': industry,
            'generated_at': final_report['generated_at']
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

'''

    print("✅ Improved celery task code generated!")
    print("\n📋 Key improvements:")
    print("1. ✅ Added directory creation error handling")
    print("2. ✅ Added file existence verification after writing")
    print("3. ✅ Added file size validation (prevents 0-byte files)")
    print("4. ✅ Added JSON readability verification")
    print("5. ✅ Better error messages for debugging")
    print("\n💡 To use this improved version:")
    print("1. Replace the current task in src/tasks/report_tasks.py")
    print("2. Update the task name in app_enhanced.py from 'generate_llm_report' to 'generate_llm_report_improved'")
    print("3. Restart the celery worker")

if __name__ == '__main__':
    create_improved_task()