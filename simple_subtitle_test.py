#!/usr/bin/env python3
"""
Simple test to verify subtitle display in browser console
"""

import asyncio
from playwright.async_api import async_playwright

async def test_subtitle_display():
    """Test subtitle display by checking browser console"""
    print("Testing subtitle display in browser...")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to a simple page
        await page.goto("http://localhost:5000")
        await page.wait_for_timeout(2000)
        
        # Test subtitle display
        subtitle_text = "测试字幕显示功能"
        escaped_text = subtitle_text.replace("'", "\\'").replace('"', '\\"')
        
        script = f"""
        (function() {{
            try {{
                console.log('Testing subtitle display: {escaped_text}');
                
                // Create subtitle container
                const container = document.createElement('div');
                container.id = 'test-subtitle';
                container.style.position = 'fixed';
                container.style.bottom = '20px';
                container.style.left = '50%';
                container.style.transform = 'translateX(-50%)';
                container.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                container.style.color = '#FFD700';
                container.style.padding = '15px 25px';
                container.style.borderRadius = '8px';
                container.style.fontFamily = 'Arial, sans-serif';
                container.style.fontSize = '18px';
                container.style.fontWeight = '500';
                container.style.textAlign = 'center';
                container.style.zIndex = '10000';
                container.style.maxWidth = '90%';
                container.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
                container.style.border = '1px solid #FFD700';
                
                // Set subtitle text
                container.textContent = '{escaped_text}';
                
                // Add to page
                document.body.appendChild(container);
                console.log('Test subtitle added to page');
                
                // Remove after 3 seconds
                setTimeout(() => {{
                    const element = document.getElementById('test-subtitle');
                    if (element && element.parentNode) {{
                        element.remove();
                        console.log('Test subtitle removed');
                    }}
                }}, 3000);
                
                return true;
            }} catch (error) {{
                console.error('Error in test:', error);
                return false;
            }}
        }})();
        """
        
        result = await page.evaluate(script)
        print(f"Subtitle test result: {result}")
        
        # Wait to see the subtitle
        await page.wait_for_timeout(5000)
        
        # Close browser
        await browser.close()
        
        print("Test completed!")

if __name__ == '__main__':
    asyncio.run(test_subtitle_display())