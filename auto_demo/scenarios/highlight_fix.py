"""
Fix for the highlight function in demo_engine.py

The issue is that single quotes in CSS selectors break the JavaScript string.
This file contains the corrected version of the _action_highlight method.
"""

async def _action_highlight_fixed(self, step: dict) -> bool:
    """
    Fixed version of the highlight action that properly escapes the selector
    """
    selector = step.get('selector')
    duration = float(step.get('duration', 1.5))
    try:
        # Properly escape single quotes in the selector to prevent breaking the JavaScript string
        escaped_selector = selector.replace("'", "\\'")
        script = f"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();"
        await self.page.evaluate(script)
        return True
    except Exception as e:
        logger.error(f"Highlight failed for {selector}: {e}")
        return False

# Alternative implementation using JSON.stringify to properly escape the selector
async def _action_highlight_json_escaped(self, step: dict) -> bool:
    """
    Alternative implementation using JSON.stringify for proper escaping
    """
    selector = step.get('selector')
    duration = float(step.get('duration', 1.5))
    try:
        import json
        selector_json = json.dumps(selector)  # This will properly escape the string
        script = f"(function(){{var el=document.querySelector({selector_json});if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();"
        await self.page.evaluate(script)
        return True
    except Exception as e:
        logger.error(f"Highlight failed for {selector}: {e}")
        return False