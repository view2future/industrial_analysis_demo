#!/usr/bin/env python3
"""
Script to apply the highlight fix to demo_engine.py
This fixes the JavaScript syntax error that occurs when highlighting elements with quotes in selectors.
"""

import re
import os

def apply_highlight_fix():
    """Apply the fix to demo_engine.py"""
    demo_engine_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/demo_engine.py"
    
    # Read the current content
    with open(demo_engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The problematic line (around line 344) looks like:
    # script = f"(function(){{var el=document.querySelector('{selector}');...
    
    # Replace it with the fixed version that escapes single quotes
    old_line_pattern = r"script = f\"\\(function\\(\\)\\{\\{var el=document\\.querySelector\\('\{selector\}'\\);"
    new_line_replacement = r"escaped_selector = selector.replace(\"'\", \"\\\\'\"); script = f\"\\(function\\(\\)\\{\\{var el=document\\.querySelector\\('\{escaped_selector\}'\\);"
    
    # More specific pattern to match the exact function
    old_code_block = r"async def _action_highlight\(self, step: Dict\[str, Any\]\) -> bool:\n\s*selector = step\.get\('selector'\)\n\s*duration = float\(step\.get\('duration', 1\.5\)\)\n\s*try:\n\s*script = f\"\\(function\\(\\)\\{\\{var el=document\\.querySelector\\('\{selector\}'\\);.*?\\(duration\*1000\)\\);return true;\\}\\}\\)\\(\\);\""
    
    # The fixed version
    new_code_block = """async def _action_highlight(self, step: Dict[str, Any]) -> bool:
        selector = step.get('selector')
        duration = float(step.get('duration', 1.5))
        try:
            # Escape single quotes in the selector to prevent breaking the JavaScript string
            escaped_selector = selector.replace(\"'\", \"\\\\'\")
            script = f\"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();\"
            await self.page.evaluate(script)
            return True"""
    
    # Find and replace the function
    updated_content = re.sub(
        r'(async def _action_highlight\(self, step: Dict\[str, Any\]\) -> bool:\n\s*selector = step\.get\(\'selector\'\)\n\s*duration = float\(step\.get\(\'duration\', 1\.5\)\)\n\s*try:\n\s*script = f\")(.*?)(\'\{selector\}\'\);if\(!el\) return false;.*?return true;\}\}\)\(\);"\)',
        lambda m: f'{m.group(1)}escaped_selector = selector.replace(\"\\\'\", \"\\\\\\\\\\\'\")\n        script = f"{m.group(2)}{{escaped_selector}}\';if(!el) return false;{m.group(3)}',
        content,
        flags=re.DOTALL
    )
    
    # Alternative approach - simpler regex that just escapes the selector
    pattern = r"script = f\"(\(function\(\)\{\{var el=document\.querySelector\('\{)selector(}'\);.*?)\}\""
    replacement = r"escaped_selector = selector.replace(\"'\", \"\\'\")\n        script = f\"\1{escaped_selector}\3\""
    
    if not re.search(pattern, content):
        # Try the exact line match
        old_line = "script = f\"(function(){{var el=document.querySelector('{selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();\""
        new_line = "            # Escape single quotes in the selector to prevent breaking the JavaScript string\n            escaped_selector = selector.replace(\"'\", \"\\\\'\")\n            script = f\"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();\""
        
        updated_content = content.replace(old_line, new_line)
    
    # Write back the updated content
    with open(demo_engine_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Successfully updated demo_engine.py with the highlight fix!")
    print("The fix properly escapes single quotes in CSS selectors to prevent JavaScript syntax errors.")


if __name__ == "__main__":
    # Verify file exists first
    demo_engine_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/demo_engine.py"
    if os.path.exists(demo_engine_path):
        apply_highlight_fix()
    else:
        print(f"Error: {demo_engine_path} does not exist!")