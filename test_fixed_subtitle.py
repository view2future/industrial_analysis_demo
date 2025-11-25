#!/usr/bin/env python3
"""
Test script to verify the fixed subtitle display
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_demo.demo_engine import DemoEngine

async def test_fixed_subtitle():
    """Test the fixed subtitle display functionality"""
    print("Testing FIXED subtitle display...")
    
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
        
        print("Browser initialized, testing subtitle display...")
        
        # Test the fixed subtitle display with a very visible example
        test_step = {
            'subtitle': '🔥 FIXED SUBTITLE - YOU SHOULD SEE THIS! 🔥',
            'description': 'Testing fixed subtitle display'
        }
        
        print("Displaying test subtitle...")
        result = await engine._display_subtitle(test_step)
        print(f"Subtitle display result: {result}")
        
        if result:
            print("SUCCESS: Subtitle display function returned True")
            print("WAIT 6 seconds - you should see a VERY VISIBLE subtitle at the bottom of the page!")
            print("Look for: 🔥 FIXED SUBTITLE - YOU SHOULD SEE THIS! 🔥")
        else:
            print("ERROR: Subtitle display function returned False")
        
        # Wait to see the subtitle
        await asyncio.sleep(8)
        
        # Test another subtitle
        test_step2 = {
            'subtitle': '✅ SECOND TEST - STILL VISIBLE? ✅',
            'description': 'Second subtitle test'
        }
        
        print("Displaying second test subtitle...")
        result2 = await engine._display_subtitle(test_step2)
        print(f"Second subtitle display result: {result2}")
        
        # Wait to see the second subtitle
        await asyncio.sleep(8)
        
        print("Fixed subtitle test completed!")
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.cleanup()

if __name__ == '__main__':
    asyncio.run(test_fixed_subtitle())