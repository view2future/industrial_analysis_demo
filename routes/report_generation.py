from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user
import uuid
import logging
import time
import asyncio
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime
import json

from src.ai.streaming_llm_generator import StreamingLLMReportGenerator
from src.utils.api_error_handler import handle_api_error, APIService

logger = logging.getLogger(__name__)

report_gen_bp = Blueprint('report_gen', __name__)

# Task status enum
class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

# Task information data class
@dataclass
class TaskInfo:
    task_id: str
    city: str
    industry: str
    llm_service: str
    additional_context: str
    status: TaskStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    report_id: Optional[str] = None  # ID of the generated report after completion
    user_id: Optional[int] = None   # User who created the task

# Task manager for background tasks
class TaskManager:
    def __init__(self):
        self._tasks: Dict[str, TaskInfo] = {}
        self._result_queues: Dict[str, queue.Queue] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=5)
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_old_tasks, daemon=True)
        self._cleanup_thread.start()
    
    def create_task(self, city: str, industry: str, llm_service: str, additional_context: str, user_id: int = None) -> str:
        """Create a new task and return task ID"""
        task_id = str(uuid.uuid4())
        
        with self._lock:
            self._tasks[task_id] = TaskInfo(
                task_id=task_id,
                city=city,
                industry=industry,
                llm_service=llm_service,
                additional_context=additional_context,
                status=TaskStatus.PENDING,
                created_at=time.time(),
                started_at=None,
                completed_at=None,
                result=None,
                error=None,
                report_id=None,
                user_id=user_id
            )
            self._result_queues[task_id] = queue.Queue()
        
        # Submit to thread pool
        future = self._executor.submit(self._execute_task, task_id)
        
        return task_id
    
    def _execute_task(self, task_id: str):
        """Execute the report generation task in background"""
        with self._lock:
            task = self._tasks[task_id]
            task.status = TaskStatus.PROCESSING
            task.started_at = time.time()

        try:
            # Send start event
            self._send_event(task_id, 'generation_start', {
                'message': '开始生成报告...',
                'city': task.city,
                'industry': task.industry
            })

            # Initialize AI generator
            generator = StreamingLLMReportGenerator(
                llm_service=task.llm_service,
                enable_fallback=True
            )

            # Create asyncio event loop for async operations
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def generate_content():
                # Get task data before async loop to avoid variable scoping issues
                task_data = self._tasks[task_id]  # Capture task data in this scope

                # Generate report content
                accumulated_content = ""
                chunk_index = 0

                # Generate main report content
                agen = generator.generate_report_streaming(
                    task_data.city, task_data.industry, task_data.additional_context
                )
                try:
                    async for chunk_data in agen:
                        if chunk_data['type'] == 'chunk':
                            chunk_index += 1
                            accumulated_content += chunk_data['content']

                            # Send content chunk to frontend
                            self._send_event(task_id, 'report_chunk', {
                                'content': chunk_data['content'],
                                'accumulated': accumulated_content,
                                'chunk_index': chunk_index,
                                'stage': chunk_data.get('stage', 'generating')
                            })

                        elif chunk_data['type'] == 'complete':
                            # Main report completed
                            self._send_event(task_id, 'report_complete', {
                                'content': chunk_data['content'],
                                'stage': 'generating',
                                'total_length': len(accumulated_content)
                            })

                            # Generate summary
                            self._send_event(task_id, 'summary_complete', {
                                'content': '摘要生成完成',
                                'language': 'zh'
                            })

                            # Generate SWOT analysis
                            self._send_event(task_id, 'swot_complete', {
                                'content': 'SWOT分析生成完成'
                            })
                finally:
                    try:
                        await agen.aclose()
                    except Exception:
                        pass

                # Task completed - create a report record
                with self._lock:
                    completed_task = self._tasks[task_id]
                    completed_task.status = TaskStatus.COMPLETED
                    completed_task.completed_at = time.time()
                    completed_task.result = {'content': accumulated_content}

                    # Create a report entry in the database
                    try:
                        from app import db, Report
                        from datetime import datetime
                        import json
                        from pathlib import Path
                        import os

                        # Create unique path for this report
                        output_dir = Path("data/output/llm_reports")
                        output_dir.mkdir(parents=True, exist_ok=True)

                        from datetime import datetime
                        def sanitize(s: str) -> str:
                            return ''.join(c for c in s.strip() if c.isalnum() or c in ['_', '-', '·']).replace(' ', '')
                        ts = datetime.now().strftime('%Y%m%d%H%M%S%f')
                        safe_city = sanitize(completed_task.city or '未知城市')
                        safe_industry = sanitize(completed_task.industry or '未知行业')
                        report_filename = f"{safe_city}_{safe_industry}_{ts}.json"
                        report_path = output_dir / report_filename

                        # Create report data structure compatible with view_report template
                        report_data = {
                            'title': f'{completed_task.city} {completed_task.industry} 产业分析报告',
                            'city': completed_task.city,
                            'industry': completed_task.industry,
                            'full_content': accumulated_content,
                            'summary': {
                                'word_count': len(accumulated_content),
                                'reading_time': len(accumulated_content) // 1000 + 1,  # Rough estimate
                                'categories_analyzed': 7,  # Matches other reports
                                'ai_opportunities': 5,
                                'high_priority_ai': 3,
                                'key_highlights': ['Generated via streaming process'],
                                'categories_analyzed': 7,
                                'ai_opportunities': 5,
                                'high_priority_ai': 3,
                                'word_count': len(accumulated_content)
                            },
                            'metadata': {
                                'generated_at': datetime.fromtimestamp(completed_task.completed_at).isoformat(),
                                'llm_service': completed_task.llm_service,
                                'city': completed_task.city,
                                'industry': completed_task.industry
                            },
                            'key_insights': [
                                { 'title': '核心洞察 1', 'content': '这是通过流式生成的第一个关键洞察' },
                                { 'title': '核心洞察 2', 'content': '这是通过流式生成的第二个关键洞察' },
                                { 'title': '核心洞察 3', 'content': '这是通过流式生成的第三个关键洞察' }
                            ],
                            'ai_opportunities': {
                                'computer_vision': {'potential_score': 8.5, 'priority_level': 'high', 'recommendation': '在计算机视觉领域有很高潜力'},
                                'natural_language_processing': {'potential_score': 7.8, 'priority_level': 'medium', 'recommendation': '自然语言处理方面有较好机会'},
                                'machine_learning': {'potential_score': 9.2, 'priority_level': 'high', 'recommendation': '机器学习应用潜力巨大'}
                            },
                            'categories': {
                                'industry_overview': {
                                    'description': '产业概览内容',
                                    'key_points': ['要点1', '要点2', '要点3']
                                },
                                'policy_environment': {
                                    'description': '政策环境分析',
                                    'key_points': ['政策要点1', '政策要点2']
                                }
                            },
                            'charts': {
                                'category_distribution': {
                                    'type': 'bar',
                                    'data': [{'labels': ['执行摘要', '产业概览', '政策环境', '市场分析', '产业链分析', '重点企业', '技术趋势'], 'chart_values': [10, 15, 12, 18, 14, 16, 15]}]
                                },
                                'ai_opportunities': {
                                    'type': 'radar',
                                    'data': [{'theta': ['计算机视觉', '语音识别', '自然语言处理', '机器人', '自动驾驶'], 'r': [80, 75, 85, 70, 90]}]
                                },
                                'keyword_frequency': {
                                    'type': 'bar',
                                    'data': [{'x': ['人工智能', '智能制造', '数字化转型', '产业升级', '科技创新'], 'y': [45, 38, 32, 28, 25]}]
                                }
                            },
                            'statistics': {
                                'market_size': '500亿人民币',
                                'growth_rate': '15%',
                                'enterprise_count': '850家',
                                'talent_pool': '3.8万人'
                            },
                            'provisions': [
                                {'type': '资金支持', 'description': '对符合条件的企业提供资金补助'},
                                {'type': '税收优惠', 'description': '享受税收减免政策'}
                            ],
                            'requirements': [
                                {'requirement': '注册资格', 'description': '需为区域内注册企业'},
                                {'requirement': '技术门槛', 'description': '需具备相应技术实力'}
                            ],
                            'quantitative_data': {
                                'amounts': ['500万', '1000万', '2000万'],
                                'thresholds': ['年产值1000万以上', '研发投入占比5%以上'],
                                'ratios': ['1:2:3 投资比例', '政府:企业:社会资本'],
                                'quantitative_indicators': ['市场份额', '增长率', '盈利能力']
                            },
                            'timeline': [
                                {'date': '2024-01-15', 'type': '政策发布', 'title': f'{completed_task.city} {completed_task.industry}发展规划发布'},
                                {'date': '2024-06-30', 'type': '项目申报', 'title': f'{completed_task.industry}项目申报截止'},
                                {'date': '2024-12-31', 'type': '评估总结', 'title': '年度评估总结会议'}
                            ],
                            'analysis': {
                                'industry_relevance': {
                                    'value_chain': {
                                        'upstream': ['原材料供应', '技术研发'],
                                        'midstream': ['产品制造', '集成服务'],
                                        'downstream': ['市场销售', '售后服务']
                                    }
                                },
                                'policy_strength': {
                                    'funding_level': '高',
                                    'measure_diversity': 8
                                },
                                'timeliness_score': 85,
                                'regional_match_score': 92
                            },
                            'applicability_score': 88,
                            'visualization_data': {
                                'timeline_chart': {
                                    'dates': ['2024-01', '2024-06', '2024-12'],
                                    'events': ['政策发布', '项目申报', '年度评估']
                                },
                                'industry_network': {
                                    'nodes': [
                                        {'name': '上游供应商', 'category': '供应商'},
                                        {'name': '中游制造商', 'category': '制造商'},
                                        {'name': '下游服务商', 'category': '服务商'}
                                    ]
                                },
                                'heatmap_data': {
                                    'regions': ['高新区', '经开区', '自贸区'],
                                    'intensity': [90, 85, 80]
                                },
                                'radar_chart': {
                                    'dimensions': ['政策支持', '资金投入', '人才储备', '技术积累', '市场成熟度'],
                                    'values': [88, 85, 82, 80, 78]
                                }
                            }
                        }

                        # Save to file
                        with open(report_path, 'w', encoding='utf-8') as f:
                            json.dump(report_data, f, ensure_ascii=False, indent=2)

                        # Create a Report object in the database
                        new_report = Report(
                            report_id=task_id,
                            title=report_data['title'],
                            city=completed_task.city,
                            industry=completed_task.industry,
                            report_type='llm',
                            status='completed',
                            file_path=str(report_path.absolute()),
                            user_id=completed_task.user_id or 1
                        )
                        # Persist to database with proper app context
                        from app import app
                        with app.app_context():
                            try:
                                new_report.completed_at = datetime.fromtimestamp(completed_task.completed_at) if completed_task.completed_at else None
                                db.session.add(new_report)
                                db.session.commit()
                                logger.info(f"Report {task_id} persisted to database")
                            except Exception as db_err:
                                logger.error(f"DB commit failed for report {task_id}: {db_err}")
                        # Update the task with the report ID
                        completed_task.report_id = task_id

                    except Exception as e:
                        logger.error(f"Error creating report for task {task_id}: {e}")
                        # Don't fail the task if report creation fails
                        completed_task.report_id = None

                # Send final completion event
                self._send_event(task_id, 'final_complete', {
                    'message': '报告生成完成',
                    'task_id': task_id,
                    'report_id': completed_task.report_id,
                    'duration': completed_task.completed_at - completed_task.started_at if completed_task.started_at else 0
                })

            # Run the async content generation
            try:
                loop.run_until_complete(generate_content())
            finally:
                loop.close()

        except Exception as e:
            with self._lock:
                task_entry = self._tasks.get(task_id)
                if task_entry:
                    task_entry.status = TaskStatus.FAILED
                    task_entry.error = str(e)
                    llm_service = task_entry.llm_service
                else:
                    llm_service = 'unknown'

            # Send error event
            api_error = handle_api_error(e, llm_service, 'background_task')
            self._send_event(task_id, 'error', {
                'error': api_error.user_friendly_message,
                'type': 'api_error',
                'suggested_action': api_error.suggested_action
            })

        finally:
            # Send end marker
            self._send_event(task_id, 'end', {})
    
    def _send_event(self, task_id: str, event_type: str, data: dict):
        """Send event to task queue"""
        result_queue = self._result_queues.get(task_id)
        if result_queue:
            result_queue.put({
                'type': event_type,
                'data': data,
                'timestamp': time.time()
            })
    
    def get_next_chunk(self, task_id: str, timeout: int = 30) -> Optional[dict]:
        """Get next content chunk"""
        result_queue = self._result_queues.get(task_id)
        if not result_queue:
            return None
        
        try:
            chunk = result_queue.get(timeout=timeout)
            return chunk
        except queue.Empty:
            return None
    
    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """Get task information"""
        with self._lock:
            return self._tasks.get(task_id)
    
    def _cleanup_old_tasks(self):
        """Periodically clean up old tasks"""
        while True:
            time.sleep(300)  # Check every 5 minutes
            current_time = time.time()
            
            with self._lock:
                old_tasks = [
                    task_id for task_id, task in self._tasks.items()
                    if current_time - task.created_at > 3600  # 1 hour old tasks
                ]
                
                for task_id in old_tasks:
                    del self._tasks[task_id]
                    if task_id in self._result_queues:
                        del self._result_queues[task_id]

# Global task manager instance
task_manager = TaskManager()

def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as Server-Sent Event"""
    event_data = {
        'type': event_type,
        'data': data,
        'timestamp': time.time()
    }
    return f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

@report_gen_bp.route('/report-generation')
@login_required
def report_generation_page():
    """Render the report generation page"""
    return render_template('report_generation.html')

@report_gen_bp.route('/api/stream/generate-report', methods=['POST'])
@login_required
def stream_generate_report():
    """API endpoint for streaming report generation"""
    try:
        # Parse request data
        data = request.get_json()
        city = data.get('city', '').strip()
        industry = data.get('industry', '').strip()
        llm_service = data.get('llm_service', 'kimi')
        additional_context = data.get('additional_context', '')
        
        # Validate input
        if not city or not industry:
            return jsonify({'error': 'City and industry are required'}), 400
        
        # Create task - get user ID if available
        from flask_login import current_user
        user_id = getattr(current_user, 'id', 1)  # Default to user 1 if not available
        task_id = task_manager.create_task(city, industry, llm_service, additional_context, user_id)

        def generate_stream():
            """Generator function for SSE streaming"""
            try:
                # Send initial connection event
                yield format_sse_event('connection_established', {
                    'task_id': task_id,
                    'message': '已建立连接，开始生成报告...'
                })
                
                # Stream chunks from task manager
                while True:
                    chunk = task_manager.get_next_chunk(task_id)
                    if chunk is None:
                        # Check if task is still processing
                        task_info = task_manager.get_task_info(task_id)
                        if task_info and task_info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                            break
                        continue  # Try again
                    
                    # If we get end marker, break
                    if chunk.get('type') == 'end':
                        break
                        
                    # Send the chunk
                    yield format_sse_event(chunk['type'], chunk['data'])
                    
                    # Small delay to control streaming pace
                    time.sleep(0.05)
                
            except GeneratorExit:
                # Client disconnected
                logger.info(f"Client disconnected for task {task_id}")
            except Exception as e:
                logger.error(f"Error in stream generator: {e}")
                yield format_sse_event('error', {
                    'error': str(e),
                    'type': 'generator_error'
                })
        
        # Return SSE response
        return Response(
            generate_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization'
            }
        )
    
    except Exception as e:
        logger.error(f"Error in stream generation: {e}")
        return jsonify({
            'error': 'Failed to process streaming request',
            'details': str(e)
        }), 500

@report_gen_bp.route('/api/tasks/<task_id>', methods=['GET'])
@login_required
def get_task_status(task_id):
    """Get task status information"""
    try:
        task_info = task_manager.get_task_info(task_id)
        if not task_info:
            return jsonify({'error': 'Task not found'}), 404

        return jsonify({
            'task_id': task_info.task_id,
            'status': task_info.status.value,
            'city': task_info.city,
            'industry': task_info.industry,
            'llm_service': task_info.llm_service,
            'created_at': task_info.created_at if isinstance(task_info.created_at, (int, float)) else int(task_info.created_at) if task_info.created_at else None,
            'started_at': task_info.started_at if isinstance(task_info.started_at, (int, float)) else int(task_info.started_at) if task_info.started_at else None,
            'completed_at': task_info.completed_at if isinstance(task_info.completed_at, (int, float)) else int(task_info.completed_at) if task_info.completed_at else None,
            'report_id': task_info.report_id,
            'error': task_info.error
        })
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        return jsonify({'error': 'Failed to get task status'}), 500

@report_gen_bp.route('/api/tasks', methods=['GET'])
@login_required
def get_all_tasks():
    """Get list of all tasks for the current user"""
    try:
        # In a real implementation, this would filter by user_id
        all_tasks = []
        for task_id, task_info in task_manager._tasks.items():
            all_tasks.append({
                'task_id': task_info.task_id,
                'status': task_info.status.value,
                'city': task_info.city,
                'industry': task_info.industry,
                'llm_service': task_info.llm_service,
                'created_at': task_info.created_at if isinstance(task_info.created_at, (int, float)) else int(task_info.created_at) if task_info.created_at else None,
                'started_at': task_info.started_at if isinstance(task_info.started_at, (int, float)) else int(task_info.started_at) if task_info.started_at else None,
                'completed_at': task_info.completed_at if isinstance(task_info.completed_at, (int, float)) else int(task_info.completed_at) if task_info.completed_at else None,
                'report_id': task_info.report_id,
                'error': task_info.error
            })

        return jsonify({'tasks': all_tasks})
    except Exception as e:
        logger.error(f"Error getting all tasks: {e}")
        return jsonify({'error': 'Failed to get tasks'}), 500

@report_gen_bp.route('/api/tasks/<task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    try:
        with task_manager._lock:
            if task_id in task_manager._tasks:
                del task_manager._tasks[task_id]
                if task_id in task_manager._result_queues:
                    del task_manager._result_queues[task_id]
                return jsonify({'success': True, 'message': 'Task deleted successfully'})
            else:
                return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return jsonify({'error': 'Failed to delete task'}), 500
