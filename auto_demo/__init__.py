"""
Auto Demo System - Automated demonstration system for Regional Industrial Dashboard

This package provides browser automation capabilities using Playwright,
allowing for automated demonstration and testing of the dashboard features.

Usage:
    from auto_demo.demo_engine import DemoEngine
    
    engine = DemoEngine('scenarios/demo.yaml', headless=True, record_video=False)
    success = await engine.run()

For command-line usage:
    python start_demo.py --headed --record
"""

__version__ = '1.0.0'
__author__ = 'Regional Industrial Dashboard Team'

from .demo_engine import DemoEngine

__all__ = ['DemoEngine']
