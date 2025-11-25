#!/usr/bin/env python3
"""
Ultra-stable subtitle test script
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_demo.demo_engine import DemoEngine

async def ultra_stable_subtitle_test():
    """Ultra-stable subtitle display test"""
    print("Running ultra-stable subtitle test...")
    
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
        
        print("Browser initialized, testing ultra-stable subtitle display...")
        
        # Test sequence - multiple subtitles to ensure stability
        test_subtitles = [
            "TEST 1: Ultra-stable subtitle - you should see this!",
            "TEST 2: If you see this, the fix is working!",
            "TEST 3: This should be visible on any page!",
            "SUCCESS: Subtitle system is now working reliably!"
        ]
        
        for i, subtitle_text in enumerate(test_subtitles):
            print(f"Displaying test {i+1}: {subtitle_text}")
            test_step = {
                'subtitle': subtitle_text,
                'description': f'Test subtitle {i+1}'
            }
            
            result = await engine._display_subtitle(test_step)
            print(f"Test {i+1} result: {result}")
            
            if result:
                print(f"WAIT 5 seconds - Look for: {subtitle_text}")
            else:
                print(f"ERROR: Test {i+1} failed!")
            
            # Wait to see the subtitle
            await asyncio.sleep(7)  # Wait longer than subtitle duration
        
        print("Ultra-stable subtitle test completed!")
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.cleanup()

if __name__ == '__main__':
    asyncio.run(ultra_stable_subtitle_test())