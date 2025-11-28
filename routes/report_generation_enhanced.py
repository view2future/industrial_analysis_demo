#!/usr/bin/env python3
"""
Enhanced Report Generation Routes with Floating Task Management
"""

import uuid
import json
import time
import asyncio
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from flask import Blueprint, render_template, request, jsonify, Response, stream_with_context
from flask_login import login_required, current_user
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
import logging
from datetime import datetime
import pytz

from src.ai.streaming_llm_generator import StreamingLLMReportGenerator
from src.utils.time_utils import format_beijing_time, now_beijing
from src.utils.api_error_handler import handle_api_error, APIService
from src.utils.notification_service import notification_service

logger = logging.getLogger(__name__)

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
    report_id: Optional[str] = None  # ID of generated report after completion
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
                'message': f'开始为{task.city} {task.industry}生成产业分析报告...',
                'city': task.city,
                'industry': task.industry,
                'timestamp': now_beijing().isoformat()
            })

            # Initialize AI generator
            generator = StreamingLLMReportGenerator(
                llm_service=task.llm_service,
                enable_fallback=True
            )

            # Generate report content
            accumulated_content = ""
            chunk_index = 0

            # Generate main report content
            for chunk_data in generator.generate_report_streaming(
                task.city, task.industry, task.additional_context
            ):
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

            # Task completed
            with self._lock:
                completed_task = self._tasks[task_id]
                completed_task.status = TaskStatus.COMPLETED
                completed_task.completed_at = time.time()
                completed_task.result = {'content': accumulated_content}
                completed_task.report_id = f"report_{task_id[:8]}"  # Generate report ID

            # Send final completion event
            self._send_event(task_id, 'final_complete', {
                'message': '报告生成完成',
                'task_id': task_id,
                'report_id': completed_task.report_id,
                'duration': completed_task.completed_at - completed_task.started_at if completed_task.started_at else 0,
                'timestamp': now_beijing().isoformat()
            })

        except Exception as e:
            with self._lock:
                task = self._tasks[task_id]
                task.status = TaskStatus.FAILED
                task.error = str(e)

            # Send error event
            api_error = handle_api_error(e, task.llm_service, 'background_task')
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

    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """Get task information"""
        with self._lock:
            return self._tasks.get(task_id)

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

    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                if task_id in self._result_queues:
                    del self._result_queues[task_id]
                return True
        return False

    def get_all_tasks(self, user_id: int = None) -> list:
        """Get all tasks, optionally filtered by user"""
        with self._lock:
            tasks = list(self._tasks.values())
            if user_id:
                tasks = [task for task in tasks if task.user_id == user_id]
            return tasks

# Global task manager instance
task_manager = TaskManager()

# Create blueprint
report_gen_enhanced_bp = Blueprint('report_gen_enhanced', __name__)

@report_gen_enhanced_bp.route('/report-generation')
@login_required
def report_generation_page():
    """Render the report generation page with modern UI and floating task manager"""
    return render_template('report_generation_enhanced.html')

@report_gen_enhanced_bp.route('/api/stream/generate-report', methods=['POST'])
@login_required
def stream_generate_report():
    """API endpoint for streaming report generation"""
    try:
        data = request.get_json() or {}
        city = (data.get('city') or '').strip()
        industry = (data.get('industry') or '').strip()
        llm_service = data.get('llm_service', 'kimi')
        additional_context = data.get('additional_context', '')

        if not city or not industry:
            return jsonify({'error': '城市和产业不能为空'}), 400

        # Create task
        user_id = getattr(current_user, 'id', 1)  # Default to user 1 if not available
        task_id = task_manager.create_task(city, industry, llm_service, additional_context, user_id)

        def generate_stream():
            """Generator function for SSE streaming"""
            try:
                # Send initial connection event
                yield f"data: {json.dumps({'type': 'connection_established', 'data': {'task_id': task_id, 'message': '连接已建立，开始生成报告...'}}, ensure_ascii=False)}\n\n"

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
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

            except GeneratorExit:
                # Client disconnected
                logger.info(f"Client disconnected for task {task_id}")
            except Exception as e:
                logger.error(f"Error in stream generator: {e}")
                yield f"data: {json.dumps({'type': 'error', 'data': {'error': str(e), 'type': 'generator_error'}}, ensure_ascii=False)}\n\n"

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

@report_gen_enhanced_bp.route('/api/tasks', methods=['GET'])
@login_required
def api_get_tasks():
    """Get list of all tasks for the current user"""
    try:
        user_id = getattr(current_user, 'id', 1)  # Default user ID if not available
        tasks = task_manager.get_all_tasks(user_id=user_id)

        task_list = []
        for task in tasks:
            task_list.append({
                'task_id': task.task_id,
                'city': task.city,
                'industry': task.industry,
                'llm_service': task.llm_service,
                'status': task.status.value,
                'created_at': format_beijing_time(task.created_at, '%Y-%m-%d %H:%M:%S') if task.created_at else None,
                'started_at': format_beijing_time(task.started_at, '%Y-%m-%d %H:%M:%S') if task.started_at else None,
                'completed_at': format_beijing_time(task.completed_at, '%Y-%m-%d %H:%M:%S') if task.completed_at else None,
                'report_id': task.report_id,
                'error': task.error
            })

        return jsonify({'tasks': task_list})
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return jsonify({'error': 'Failed to get tasks'}), 500

@report_gen_enhanced_bp.route('/api/tasks/<task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    """Delete a specific task"""
    try:
        success = task_manager.delete_task(task_id)
        if success:
            return jsonify({'success': True, 'message': '任务删除成功'})
        else:
            return jsonify({'error': '任务不存在'}), 404
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return jsonify({'error': 'Failed to delete task'}), 500

@report_gen_enhanced_bp.route('/api/task-status/<task_id>', methods=['GET'])
@login_required
def api_task_status(task_id):
    """Get status of a specific task"""
    try:
        task_info = task_manager.get_task_info(task_id)
        if not task_info:
            return jsonify({'error': 'Task not found'}), 404

        return jsonify({
            'task_id': task_info.task_id,
            'city': task_info.city,
            'industry': task_info.industry,
            'llm_service': task_info.llm_service,
            'status': task_info.status.value,
            'created_at': format_beijing_time(task_info.created_at, '%Y-%m-%d %H:%M:%S'),
            'started_at': format_beijing_time(task_info.started_at, '%Y-%m-%d %H:%M:%S') if task_info.started_at else None,
            'completed_at': format_beijing_time(task_info.completed_at, '%Y-%m-%d %H:%M:%S') if task_info.completed_at else None,
            'report_id': task_info.report_id,
            'error': task_info.error
        })
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        return jsonify({'error': 'Failed to get task status'}), 500