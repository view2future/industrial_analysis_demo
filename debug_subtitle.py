#!/usr/bin/env python3
"""
Debug script to test subtitle display step by step
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_subtitle_display():
    """Debug subtitle display step by step"""
    print("Debugging subtitle display...")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to a simple page
        await page.goto("http://localhost:5000")
        await page.wait_for_timeout(3000)
        
        print("Page loaded, now testing subtitle display...")
        
        # Test 1: Simple element creation
        print("Test 1: Creating simple element")
        result1 = await page.evaluate("""
            () => {
                const div = document.createElement('div');
                div.id = 'debug-subtitle-1';
                div.textContent = 'DEBUG: Simple Test';
                div.style.position = 'fixed';
                div.style.bottom = '50px';
                div.style.left = '50%';
                div.style.transform = 'translateX(-50%)';
                div.style.backgroundColor = 'black';
                div.style.color = 'yellow';
                div.style.padding = '10px 20px';
                div.style.zIndex = '999999';
                div.style.fontSize = '20px';
                div.style.fontWeight = 'bold';
                document.body.appendChild(div);
                console.log('Element created and added');
                return document.getElementById('debug-subtitle-1') !== null;
            }
        """)
        print(f"Test 1 result: {result1}")
        await page.wait_for_timeout(3000)
        
        # Remove first test element
        await page.evaluate("""
            () => {
                const el = document.getElementById('debug-subtitle-1');
                if (el) el.remove();
            }
        """)
        
        # Test 2: Function-based approach
        print("Test 2: Function-based approach")
        result2 = await page.evaluate("""
            (function() {
                try {
                    const container = document.createElement('div');
                    container.id = 'debug-subtitle-2';
                    container.textContent = 'DEBUG: Function Test';
                    container.style.cssText = 'position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%); background: black; color: yellow; padding: 10px 20px; z-index: 999999; font-size: 20px; font-weight: bold;';
                    document.body.appendChild(container);
                    console.log('Function test element added');
                    return true;
                } catch (error) {
                    console.error('Function test error:', error);
                    return false;
                }
            })()
        """)
        print(f"Test 2 result: {result2}")
        await page.wait_for_timeout(3000)
        
        # Remove second test element
        await page.evaluate("""
            () => {
                const el = document.getElementById('debug-subtitle-2');
                if (el) el.remove();
            }
        """)
        
        # Test 3: Exact approach from our code
        print("Test 3: Exact approach from our code")
        result3 = await page.evaluate("""
            (function() {
                try {
                    // Remove existing subtitle if present
                    const existing = document.getElementById('automation-subtitle');
                    if (existing) {
                        existing.remove();
                    }
                    
                    // Create subtitle container
                    const container = document.createElement('div');
                    container.id = 'automation-subtitle';
                    container.textContent = 'DEBUG: Final Test - You should see this!';
                    
                    // Apply basic styles
                    container.style.position = 'fixed';
                    container.style.bottom = '20px';
                    container.style.left = '50%';
                    container.style.transform = 'translateX(-50%)';
                    container.style.backgroundColor = 'black';
                    container.style.color = 'yellow';
                    container.style.padding = '15px 25px';
                    container.style.borderRadius = '8px';
                    container.style.fontFamily = 'Arial, sans-serif';
                    container.style.fontSize = '18px';
                    container.style.fontWeight = 'bold';
                    container.style.textAlign = 'center';
                    container.style.zIndex = '999999';
                    container.style.maxWidth = '90%';
                    container.style.boxSizing = 'border-box';
                    container.style.border = '2px solid yellow';
                    
                    // Add to page
                    document.body.appendChild(container);
                    console.log('Final test subtitle added to page');
                    
                    // Auto-remove after 8 seconds
                    setTimeout(() => {
                        const element = document.getElementById('automation-subtitle');
                        if (element && element.parentNode) {
                            element.remove();
                            console.log('Final test subtitle removed');
                        }
                    }, 8000);
                    
                    return true;
                } catch (error) {
                    console.error('Error displaying subtitle:', error);
                    return false;
                }
            })();
        """)
        print(f"Test 3 result: {result3}")
        print("Waiting 10 seconds to see if subtitle appears...")
        await page.wait_for_timeout(10000)
        
        # Close browser
        await browser.close()
        
        print("Debug test completed!")

if __name__ == '__main__':
    asyncio.run(debug_subtitle_display())