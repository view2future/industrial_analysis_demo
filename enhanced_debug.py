#!/usr/bin/env python3
"""
Enhanced debug script to test subtitle display with more visual feedback
"""

import asyncio
from playwright.async_api import async_playwright

async def enhanced_debug_subtitle():
    """Enhanced debug subtitle display"""
    print("Enhanced debugging subtitle display...")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to a simple page
        await page.goto("http://localhost:5000")
        await page.wait_for_timeout(3000)
        
        print("Page loaded, now testing subtitle display...")
        
        # Test with maximum visibility
        print("Creating highly visible subtitle...")
        result = await page.evaluate("""
            (function() {
                try {
                    console.log('Starting subtitle creation...');
                    
                    // Remove any existing subtitle
                    const old = document.getElementById('super-visible-subtitle');
                    if (old) {
                        console.log('Removing old subtitle');
                        old.remove();
                    }
                    
                    // Create a VERY visible subtitle
                    const container = document.createElement('div');
                    container.id = 'super-visible-subtitle';
                    container.textContent = '🔥 YOU SHOULD SEE THIS SUPER VISIBLE SUBTITLE 🔥';
                    
                    // MAXIMUM visibility styles
                    container.style.position = 'fixed';
                    container.style.bottom = '50px';
                    container.style.left = '50%';
                    container.style.transform = 'translateX(-50%)';
                    container.style.backgroundColor = 'red';
                    container.style.color = 'white';
                    container.style.padding = '20px 40px';
                    container.style.borderRadius = '10px';
                    container.style.fontFamily = 'Arial, sans-serif';
                    container.style.fontSize = '24px';
                    container.style.fontWeight = 'bold';
                    container.style.textAlign = 'center';
                    container.style.zIndex = '9999999';
                    container.style.maxWidth = '95%';
                    container.style.boxSizing = 'border-box';
                    container.style.border = '5px solid yellow';
                    container.style.boxShadow = '0 0 20px rgba(255, 255, 0, 0.8)';
                    container.style.textShadow = '2px 2px 4px rgba(0, 0, 0, 0.5)';
                    
                    // Add to page
                    document.body.appendChild(container);
                    console.log('Super visible subtitle added to page');
                    
                    // Verify it exists
                    const check = document.getElementById('super-visible-subtitle');
                    if (check) {
                        console.log('SUCCESS: Subtitle element found in DOM!');
                    } else {
                        console.error('ERROR: Subtitle element NOT found in DOM!');
                    }
                    
                    // Flash effect to make it more noticeable
                    let flashCount = 0;
                    const flashInterval = setInterval(() => {
                        if (flashCount >= 10) {
                            clearInterval(flashInterval);
                            return;
                        }
                        container.style.backgroundColor = flashCount % 2 === 0 ? 'red' : 'orange';
                        flashCount++;
                    }, 300);
                    
                    // Auto-remove after 15 seconds
                    setTimeout(() => {
                        const element = document.getElementById('super-visible-subtitle');
                        if (element && element.parentNode) {
                            element.remove();
                            console.log('Super visible subtitle removed');
                        }
                        clearInterval(flashInterval);
                    }, 15000);
                    
                    return check !== null;
                } catch (error) {
                    console.error('Error creating subtitle:', error);
                    return false;
                }
            })();
        """)
        print(f"Subtitle creation result: {result}")
        print("Waiting 15 seconds - you should see a RED subtitle with YELLOW border at the bottom of the page!")
        await page.wait_for_timeout(15000)
        
        # Close browser
        await browser.close()
        
        print("Enhanced debug test completed!")

if __name__ == '__main__':
    asyncio.run(enhanced_debug_subtitle())