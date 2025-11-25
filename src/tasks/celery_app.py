#!/usr/bin/env python3
"""
Celery application for background task processing
Handles async report generation and other long-running tasks
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")

import os
from celery import Celery

# Configure Celery
celery_app = Celery(
    'industrial_analysis',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['src.tasks'])
