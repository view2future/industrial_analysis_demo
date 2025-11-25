#!/usr/bin/env python3
"""
Working version subtitle test - based on the version that actually worked
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_demo.demo_engine import DemoEngine

async def working_version_test():
    """Test the working version of subtitle display"""
    print("Testing the WORKING version of subtitle display...")
    
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
        
        print("Browser initialized, testing WORKING subtitle display...")
        
        # Test the exact same approach that worked in debug script
        test_subtitles = [
            "✅ WORKING VERSION - You should definitely see this!",
            "✅ If you see this, the approach is correct!",
            "✅ This uses the same method as the debug script!",
            "🎉 SUCCESS: Stable subtitle display achieved!"
        ]
        
        for i, subtitle_text in enumerate(test_subtitles):
            print(f"Displaying working test {i+1}: {subtitle_text}")
            test_step = {
                'subtitle': subtitle_text,
                'description': f'Working test {i+1}'
            }
            
            result = await engine._display_subtitle(test_step)
            print(f"Working test {i+1} result: {result}")
            
            if result:
                print(f"WAIT 5 seconds - Look for: {subtitle_text}")
            else:
                print(f"ERROR: Working test {i+1} failed!")
            
            # Wait to see the subtitle (same duration as debug script)
            await asyncio.sleep(7)
        
        print("Working version subtitle test completed!")
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.cleanup()

if __name__ == '__main__':
    asyncio.run(working_version_test())