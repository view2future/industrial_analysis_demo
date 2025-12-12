#!/usr/bin/env python3
"""
Correct script to apply the highlight fix to demo_engine.py
This fixes the JavaScript syntax error that occurs when highlighting elements with quotes in selectors.
"""

def apply_highlight_fix():
    """Apply the fix to demo_engine.py using proper line handling"""
    demo_engine_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/demo_engine.py"
    
    # Read the current content
    with open(demo_engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The incorrectly updated line we need to fix (with the escape sequences in it)
    old_problematic_content = "# Escape single quotes in the selector to prevent breaking the JavaScript string\\n                        escaped_selector = selector.replace(\"'\", \"\\\\'\")\\n                        script = f\"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();\""
    
    # The correct content
    correct_content = """            # Escape single quotes in the selector to prevent breaking the JavaScript string
            escaped_selector = selector.replace("'", "\\\\'")
            script = f"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();\""""
    
    # Replace if the problematic content is found
    if old_problematic_content in content:
        updated_content = content.replace(old_problematic_content, correct_content)
        with open(demo_engine_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("Fixed the formatting in demo_engine.py!")
    else:
        # If the problematic content isn't found, let's use the original approach but with proper formatting
        print("Looking for original problematic line...")
        
        # Original problematic line
        original_line = "            script = f\"(function(){{var el=document.querySelector('{selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();\""
        
        # Fixed lines
        fixed_lines = """            # Escape single quotes in the selector to prevent breaking the JavaScript string
            escaped_selector = selector.replace("'", "\\\\'")
            script = f"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();\""""
        
        if original_line in content:
            updated_content = content.replace(original_line, fixed_lines)
            with open(demo_engine_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print("Applied original fix to demo_engine.py!")
        else:
            print("Could not find expected content to fix.")


if __name__ == "__main__":
    apply_highlight_fix()