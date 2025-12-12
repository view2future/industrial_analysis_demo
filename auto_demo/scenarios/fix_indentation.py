#!/usr/bin/env python3
"""
Correct script to fix the indentation in the highlight function
"""

def fix_indentation():
    """Fix the indentation in demo_engine.py"""
    demo_engine_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/demo_engine.py"
    
    # Read the current content
    with open(demo_engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the function with incorrect indentation
    old_content = """        try:
                        # Escape single quotes in the selector to prevent breaking the JavaScript string
            escaped_selector = selector.replace("'", "\\'")
            script = f"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();"
            await self.page.evaluate(script)"""
    
    new_content = """        try:
            # Escape single quotes in the selector to prevent breaking the JavaScript string
            escaped_selector = selector.replace("'", "\\'")
            script = f"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();"
            await self.page.evaluate(script)"""
    
    # Replace the indented content with correct indentation
    updated_content = content.replace(old_content, new_content)
    
    # Write back the updated content
    with open(demo_engine_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Fixed indentation in demo_engine.py!")


if __name__ == "__main__":
    fix_indentation()