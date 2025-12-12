#!/usr/bin/env python3
"""
Clean script to rewrite the highlight function correctly
"""

def rewrite_highlight_function():
    """Rewrite the _action_highlight function correctly"""
    demo_engine_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/demo_engine.py"
    
    # Read the current content
    with open(demo_engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the start and end of the function to replace
    # We'll look for the function definition and rewrite it completely
    start_marker = "async def _action_highlight(self, step: Dict[str, Any]) -> bool:"
    end_marker = "            logger.error(f\"Highlight failed for {selector}: {e}\")"
    
    # Find the start position
    start_pos = content.find(start_marker)
    if start_pos == -1:
        print("Could not find the start of the function")
        return
    
    # Find the end position (find the line after the end marker)
    end_pos = content.find(end_marker)
    if end_pos == -1:
        print("Could not find the end marker")
        return
    
    # Find the end of the logger.error line
    end_pos = content.find('\n', end_pos + len(end_marker))
    if end_pos == -1:
        end_pos = len(content)
    else:
        # Go to end of that line
        end_pos = content.find('\n', end_pos)
        if end_pos == -1:
            end_pos = len(content)
    
    # Extract the parts before and after the function
    before_function = content[:start_pos]
    after_function = content[end_pos:]
    
    # Define the corrected function with proper indentation (4 spaces per level)
    corrected_function = """async def _action_highlight(self, step: Dict[str, Any]) -> bool:
        selector = step.get('selector')
        duration = float(step.get('duration', 1.5))
        try:
            # Escape single quotes in the selector to prevent breaking the JavaScript string
            escaped_selector = selector.replace("'", "\\\\'")
            script = f"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();"
            await self.page.evaluate(script)
            return True
        except Exception as e:"""
    
    # Combine everything
    new_content = before_function + corrected_function + after_function
    
    # Write back the corrected content
    with open(demo_engine_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Successfully rewrote the _action_highlight function with correct indentation!")


if __name__ == "__main__":
    rewrite_highlight_function()