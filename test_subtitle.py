#!/usr/bin/env python3
"""
Test script to verify subtitle display functionality
"""

import asyncio
from auto_demo.demo_engine import DemoEngine

async def test_subtitle_display():
    """Test subtitle display functionality"""
    print("Testing subtitle display...")
    
    # Initialize demo engine
    engine = DemoEngine('auto_demo/scenarios/quick_demo.yaml', headless=False)
    
    try:
        # Load scenario
        if not await engine.load_scenario():
            print("Failed to load scenario")
            return False
        
        # Initialize browser
        if not await engine.initialize_browser():
            print("Failed to initialize browser")
            return False
        
        # Test different subtitle scenarios
        test_steps = [
            {'subtitle': '欢迎观看演示', 'description': '欢迎步骤'},
            {'subtitle': '这是测试字幕', 'description': '测试步骤'},
            {'subtitle': '字幕应该显示在页面底部', 'description': '位置测试'},
            {'subtitle': '黄色文字，黑色背景', 'description': '样式测试'}
        ]
        
        for i, step in enumerate(test_steps):
            print(f"Testing subtitle {i+1}: {step['subtitle']}")
            result = await engine._display_subtitle(step)
            print(f"  Result: {result}")
            await asyncio.sleep(3)  # Wait to see the subtitle
        
        print("Subtitle test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    finally:
        await engine.cleanup()

if __name__ == '__main__':
    asyncio.run(test_subtitle_display())