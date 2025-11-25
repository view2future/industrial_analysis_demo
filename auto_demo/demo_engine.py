#!/usr/bin/env python3
"""
Auto Demo Engine - Playwright-based browser automation
Based on YAML scenario configurations
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DemoEngine:
    """Main automation engine for running demo scenarios"""
    
    def __init__(self, scenario_path: str, headless: bool = True, record_video: bool = False, screen_size: Optional[str] = None):
        self.scenario_path = Path(scenario_path)
        self.headless = headless
        self.record_video = record_video
        self.scenario: Dict[str, Any] = {}
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.base_url = "http://localhost:5000"
        self.screen_size = screen_size
        self.viewport = {'width': 1280, 'height': 800}
        
    async def load_scenario(self) -> bool:
        """Load and parse YAML scenario file"""
        try:
            if not self.scenario_path.exists():
                logger.error(f"Scenario file not found: {self.scenario_path}")
                return False
            
            with open(self.scenario_path, 'r', encoding='utf-8') as f:
                self.scenario = yaml.safe_load(f)
            
            if not self.scenario:
                logger.error("Empty scenario file")
                return False
            
            # Extract configuration
            self.base_url = self.scenario.get('base_url', self.base_url)
            logger.info(f"Loaded scenario: {self.scenario.get('name', 'Unnamed')}")
            logger.info(f"Description: {self.scenario.get('description', 'No description')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load scenario: {e}")
            return False
    
    async def initialize_browser(self) -> bool:
        """Initialize Playwright browser"""
        try:
            playwright = await async_playwright().start()
            
            # Browser launch options
            launch_options = {
                'headless': self.headless,
                'slow_mo': self.scenario.get('config', {}).get('slow_motion', 50)
            }
            
            self.browser = await playwright.chromium.launch(**launch_options)
            
            # Resolve viewport
            self.viewport = self._resolve_viewport(self.screen_size)
            # Context options
            context_options = {
                'viewport': self.viewport,
                'locale': 'zh-CN',
                'timezone_id': 'Asia/Shanghai'
            }
            
            if self.record_video:
                recordings_dir = Path(__file__).parent / 'recordings'
                recordings_dir.mkdir(exist_ok=True)
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                context_options['record_video_dir'] = str(recordings_dir)
                context_options['record_video_size'] = self.viewport
                logger.info(f"Video recording enabled: {recordings_dir}/demo_{timestamp}.webm")
            
            self.context = await self.browser.new_context(**context_options)
            self.page = await self.context.new_page()
            
            # Set reasonable timeouts
            self.page.set_default_timeout(30000)  # 30 seconds
            self.page.set_default_navigation_timeout(30000)
            
            logger.info("Browser initialized successfully")
            await self._inject_control_panel()
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def run_scenario(self) -> bool:
        """Execute the demo scenario"""
        try:
            steps = self.scenario.get('steps', [])
            if not steps:
                logger.warning("No steps found in scenario")
                return False
            
            total_steps = len(steps)
            logger.info(f"Starting demo with {total_steps} steps")
            
            config = self.scenario.get('config', {})
            action_delay = config.get('action_delay', 1.5)
            
            for idx, step in enumerate(steps, 1):
                action = step.get('action')
                description = step.get('description', f'Step {idx}')
                
                logger.info(f"[{idx}/{total_steps}] {description}")
                await self._respect_pause()
                await self._inject_control_panel()
                success = await self.execute_action(step)
                
                if not success and not step.get('optional', False):
                    logger.error(f"Failed to execute required step: {description}")
                    return False
                
                # Delay between actions
                if idx < total_steps:
                    await self._respect_pause()
                    await asyncio.sleep(action_delay)
            
            logger.info("✅ Demo completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error running scenario: {e}")
            return False
    
    async def execute_action(self, step: Dict[str, Any]) -> bool:
        """Execute a single action step"""
        action = step.get('action')
        
        # Display subtitle before executing action
        await self._display_subtitle(step)
        
        try:
            if action == 'navigate':
                return await self._action_navigate(step)
            elif action == 'click':
                return await self._action_click(step)
            elif action == 'fill':
                return await self._action_fill(step)
            elif action == 'wait':
                return await self._action_wait(step)
            elif action == 'scroll_smooth':
                return await self._action_scroll_smooth(step)
            elif action == 'message':
                return await self._action_message(step)
            else:
                logger.warning(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return False
    
    async def _action_navigate(self, step: Dict[str, Any]) -> bool:
        """Navigate to a URL"""
        url = step.get('url', '/')
        full_url = url if url.startswith('http') else f"{self.base_url}{url}"
        
        try:
            await self.page.goto(full_url, wait_until='domcontentloaded')
            await asyncio.sleep(0.5)  # Extra time for JS to execute
            
            # Re-display subtitle after navigation
            await self._display_subtitle(step)
            await self._inject_control_panel()
            return True
        except Exception as e:
            logger.error(f"Navigation failed to {full_url}: {e}")
            return False
    
    async def _action_click(self, step: Dict[str, Any]) -> bool:
        """Click an element"""
        selector = step.get('selector')
        fallbacks = step.get('fallback', [])
        optional = step.get('optional', False)
        
        # Try primary selector
        try:
            await self.page.click(selector, timeout=5000)
            await asyncio.sleep(0.3)
            return True
        except Exception as e:
            logger.warning(f"Primary selector failed: {selector}")
        
        # Try fallback selectors
        for fb in fallbacks:
            fb_selector = fb.get('selector') if isinstance(fb, dict) else fb
            try:
                await self.page.click(fb_selector, timeout=5000)
                await asyncio.sleep(0.3)
                logger.info(f"Fallback selector succeeded: {fb_selector}")
                return True
            except Exception:
                continue
        
        if optional:
            logger.info("Optional click failed, continuing...")
            return True
        
        logger.error(f"All click attempts failed for: {selector}")
        return False
    
    async def _action_fill(self, step: Dict[str, Any]) -> bool:
        """Fill an input field"""
        selector = step.get('selector')
        value = step.get('value', '')
        
        try:
            # Clear existing value first
            await self.page.fill(selector, '')
            await asyncio.sleep(0.2)
            
            # Type with realistic speed
            await self.page.type(selector, value, delay=80)
            await asyncio.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"Fill failed for {selector}: {e}")
            return False
    
    async def _action_wait(self, step: Dict[str, Any]) -> bool:
        """Wait for a specified duration"""
        duration = step.get('duration', 1)
        total = 0.0
        interval = 0.1
        while total < duration:
            await self._respect_pause()
            await asyncio.sleep(interval)
            total += interval
        return True
    
    async def _action_scroll_smooth(self, step: Dict[str, Any]) -> bool:
        """Smooth scrolling animation"""
        direction = step.get('direction', 'down')
        duration = step.get('duration', 5)
        
        try:
            # Get page height
            page_height = await self.page.evaluate('document.documentElement.scrollHeight')
            viewport_height = await self.page.evaluate('window.innerHeight')
            
            if direction == 'down':
                start_pos = 0
                end_pos = page_height - viewport_height
            else:  # up
                start_pos = page_height - viewport_height
                end_pos = 0
            
            # Calculate steps for smooth animation
            steps = max(int(duration * 20), 20)  # 20 fps
            step_size = (end_pos - start_pos) / steps
            step_delay = duration / steps
            
            current_pos = start_pos
            for _ in range(steps):
                await self._respect_pause()
                current_pos += step_size
                await self.page.evaluate(f'window.scrollTo(0, {int(current_pos)})')
                await asyncio.sleep(step_delay)
            
            # Ensure we end at exact position
            await self.page.evaluate(f'window.scrollTo(0, {int(end_pos)})')
            return True
            
        except Exception as e:
            logger.error(f"Smooth scroll failed: {e}")
            return False
    
    async def _action_message(self, step: Dict[str, Any]) -> bool:
        """Display a message (console only)"""
        text = step.get('text', '')
        print(f"\n{'='*50}")
        print(f"  {text}")
        print(f"{'='*50}\n")
        return True
    
    async def _display_subtitle(self, step: Dict[str, Any]) -> bool:
        """Display subtitle on the page - STABLE VERSION BASED ON WORKING DEBUG SCRIPT"""
        try:
            # Get subtitle text from step
            subtitle = step.get('subtitle') or step.get('description', '')
            if not subtitle:
                return True
            
            logger.info(f"Displaying subtitle: {subtitle}")
            
            # Escape single quotes in subtitle text
            escaped_subtitle = subtitle.replace("'", "\\'").replace('"', '\\"')
            
            # USE THE EXACT SAME APPROACH THAT WORKED IN DEBUG SCRIPT
            script = """
            (function() {{
                try {{
                    // Remove any existing subtitle
                    const old = document.getElementById('automation-subtitle');
                    if (old) {{
                        old.remove();
                    }}
                    
                    // Create a VERY visible subtitle - SAME AS DEBUG SCRIPT
                    const container = document.createElement('div');
                    container.id = 'automation-subtitle';
                    container.textContent = '__SUB__';
                    
                    // SAME styles as debug script that worked
                    container.style.position = 'fixed';
                    container.style.bottom = '150px';  // Moved up further to ensure better visibility
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
                    
                    // Auto-remove after 5 seconds
                    setTimeout(() => {{
                        const element = document.getElementById('automation-subtitle');
                        if (element && element.parentNode) {{
                            element.remove();
                        }}
                    }}, 5000);
                    
                    return true;
                }} catch (error) {{
                    console.error('Error creating subtitle:', error);
                    return false;
                }}
            }})();
            """
            
            # Execute the script
            result = await self.page.evaluate(script.replace('__SUB__', escaped_subtitle))
            logger.info(f"Subtitle injection result: {result}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to display subtitle: {e}")
            return False
    
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    async def run(self) -> bool:
        """Main execution flow"""
        try:
            # Load scenario
            if not await self.load_scenario():
                return False
            
            # Initialize browser
            if not await self.initialize_browser():
                return False
            
            # Run the demo
            success = await self.run_scenario()
            
            # Give time to see final state
            if not self.headless:
                await asyncio.sleep(2)
            
            return success
            
        finally:
            await self.cleanup()

    def _resolve_viewport(self, size: Optional[str]) -> Dict[str, int]:
        if size == 'big':
            return {'width': 1920, 'height': 1080}
        if size == 'small':
            return {'width': 1280, 'height': 720}
        return {'width': 1280, 'height': 800}

    async def _is_paused(self) -> bool:
        try:
            val = await self.page.evaluate('localStorage.getItem("AUTO_DEMO_PAUSED") === "true"')
            return bool(val)
        except Exception:
            return False

    async def _respect_pause(self):
        while await self._is_paused():
            await asyncio.sleep(0.1)

    async def _inject_control_panel(self):
        try:
            script = """
            (function() {
                try {
                    if (!localStorage.getItem('AUTO_DEMO_PAUSED')) {
                        localStorage.setItem('AUTO_DEMO_PAUSED', 'false');
                    }

                    let overlay = document.getElementById('auto-demo-container');
                    if (!overlay) {
                        overlay = document.createElement('div');
                        overlay.id = 'auto-demo-container';
                        overlay.style.position = 'fixed';
                        overlay.style.top = '0';
                        overlay.style.right = '0';
                        overlay.style.width = '100vw';
                        overlay.style.height = '100vh';
                        overlay.style.zIndex = '9999999';
                        overlay.style.pointerEvents = 'none';
                        document.body.appendChild(overlay);
                    }

                    let btn = document.getElementById('auto-demo-toggle');
                    if (!btn) {
                        btn = document.createElement('button');
                        btn.id = 'auto-demo-toggle';
                        btn.style.position = 'absolute';
                        btn.style.top = '50%';
                        btn.style.right = '20px';
                        btn.style.transform = 'translateY(-50%)';
                        btn.style.width = '60px';
                        btn.style.height = '60px';
                        btn.style.borderRadius = '50%';
                        btn.style.border = 'none';
                        btn.style.outline = 'none';
                        btn.style.color = '#fff';
                        btn.style.boxShadow = '0 6px 10px rgba(0,0,0,0.2)';
                        btn.style.cursor = 'pointer';
                        btn.style.display = 'flex';
                        btn.style.flexDirection = 'column';
                        btn.style.alignItems = 'center';
                        btn.style.justifyContent = 'center';
                        btn.style.gap = '4px';
                        btn.style.fontSize = '18px';
                        btn.style.pointerEvents = 'auto';
                        btn.style.opacity = '0.5';
                        btn.style.transition = 'background-color 0.2s ease, transform 0.2s ease, opacity 0.2s ease, box-shadow 0.2s ease';
                        btn.setAttribute('role', 'button');
                        btn.setAttribute('tabindex', '0');

                        const iconEl = document.createElement('i');
                        iconEl.style.pointerEvents = 'none';
                        iconEl.style.fontSize = '18px';
                        const labelEl = document.createElement('span');
                        labelEl.id = 'auto-demo-toggle-label';
                        labelEl.style.fontSize = '12px';
                        labelEl.style.lineHeight = '1';
                        labelEl.style.fontWeight = '600';
                        labelEl.style.pointerEvents = 'none';

                        btn.appendChild(iconEl);
                        btn.appendChild(labelEl);
                        overlay.appendChild(btn);
                    }

                    const icon = btn.querySelector('i') || document.createElement('i');
                    const label = btn.querySelector('#auto-demo-toggle-label') || document.createElement('span');
                    if (!btn.contains(icon)) { btn.appendChild(icon); }
                    if (!btn.contains(label)) { label.id = 'auto-demo-toggle-label'; btn.appendChild(label); }

                    const applyVisualState = () => {
                        const paused = localStorage.getItem('AUTO_DEMO_PAUSED') === 'true';
                        icon.className = paused ? 'fas fa-play' : 'fas fa-pause';
                        label.textContent = paused ? 'Play' : 'Pause';
                        btn.setAttribute('aria-pressed', paused ? 'true' : 'false');
                        btn.setAttribute('aria-label', paused ? 'Play Auto Demo' : 'Pause Auto Demo');
                        btn.style.backgroundColor = paused ? 'rgba(255, 165, 0, 0.5)' : 'rgba(128, 0, 128, 0.5)';
                        btn.style.borderRadius = '50%';
                        btn.style.opacity = '0.5';
                    };

                    applyVisualState();

                    if (!document.getElementById('auto-demo-toggle-styles')) {
                        const style = document.createElement('style');
                        style.id = 'auto-demo-toggle-styles';
                        style.textContent = `
                            #auto-demo-toggle:focus { box-shadow: 0 0 0 3px rgba(98,0,238,0.6); outline: none; }
                            @media (max-width: 768px) {
                                #auto-demo-container { width: 100vw; height: 100vh; }
                                #auto-demo-toggle { right: 20px; top: 50%; transform: translateY(-50%); }
                            }
                            @media (min-width: 769px) {
                                #auto-demo-container { width: 100vw; height: 100vh; }
                                #auto-demo-toggle { right: 20px; top: 50%; transform: translateY(-50%); }
                            }
                        `;
                        document.head.appendChild(style);
                    }

                    if (!btn._bound) {
                        let clicking = false;
                        const toggle = () => {
                            if (clicking) return;
                            clicking = true;
                            const isPaused = localStorage.getItem('AUTO_DEMO_PAUSED') === 'true';
                            localStorage.setItem('AUTO_DEMO_PAUSED', !isPaused ? 'true' : 'false');
                            applyVisualState();
                            setTimeout(() => { clicking = false; }, 200);
                        };
                        btn.addEventListener('click', toggle);
                        btn.addEventListener('keydown', function(e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
                        btn._bound = true;
                    }
                    return true;
                } catch (e) {
                    return false;
                }
            })();
            """
            await self.page.evaluate(script)
        except Exception:
            pass


async def main():
    """Entry point for direct execution"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python demo_engine.py <scenario_file.yaml>")
        sys.exit(1)
    
    scenario_file = sys.argv[1]
    headless = '--headless' in sys.argv
    record = '--record' in sys.argv
    
    engine = DemoEngine(scenario_file, headless=headless, record_video=record)
    success = await engine.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
