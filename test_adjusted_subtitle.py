#!/usr/bin/env python3
"""
Test script to verify adjusted subtitle position
"""

import asyncio
from playwright.async_api import async_playwright

async def test_adjusted_subtitle():
    """Test that subtitle appears in adjusted position"""
    print("Testing adjusted subtitle position...")
    
    async with async_playwright() as p:
        # Launch browser in headed mode to see the subtitle
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to a simple page
        await page.goto("https://example.com")
        await page.wait_for_timeout(2000)
        
        # Test the adjusted subtitle display
        result = await page.evaluate("""
            (function() {
                try {
                    // Remove any existing subtitle
                    const old = document.getElementById('automation-subtitle');
                    if (old) {
                        old.remove();
                    }
                    
                    // Create subtitle with adjusted position
                    const container = document.createElement('div');
                    container.id = 'automation-subtitle';
                    container.textContent = '测试字幕 - 应该在屏幕可见区域内';
                    
                    // Apply styles with adjusted position
                    container.style.position = 'fixed';
                    container.style.bottom = '150px';  // Further adjusted from 100px for better visibility
                    container.style.left = '50%';
                    container.style.transform = 'translateX(-50%)';
                    container.style.backgroundColor = 'black';
                    container.style.color = 'yellow';
                    container.style.padding = '15px 30px';
                    container.style.borderRadius = '8px';
                    container.style.fontFamily = 'Arial, sans-serif';
                    container.style.fontSize = '20px';
                    container.style.fontWeight = 'bold';
                    container.style.textAlign = 'center';
                    container.style.zIndex = '9999999';
                    container.style.maxWidth = '90%';
                    container.style.boxSizing = 'border-box';
                    container.style.border = '3px solid yellow';
                    container.style.boxShadow = '0 0 15px rgba(255, 255, 0, 0.7)';
                    
                    // Add to page
                    document.body.appendChild(container);
                    
                    console.log('Adjusted subtitle added to page');
                    return true;
                } catch (error) {
                    console.error('Error creating subtitle:', error);
                    return false;
                }
            })();
        """)
        
        print(f"Subtitle display result: {result}")
        print("Check if the yellow subtitle is visible on screen...")
        print("Waiting 8 seconds to observe the subtitle...")
        await page.wait_for_timeout(8000)
        
        # Clean up
        await page.evaluate("""
            () => {
                const el = document.getElementById('automation-subtitle');
                if (el) el.remove();
            }
        """)
        
        await browser.close()
        print("Test completed!")

if __name__ == '__main__':
    asyncio.run(test_adjusted_subtitle())