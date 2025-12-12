#!/usr/bin/env python3
"""
Simple script to apply the highlight fix to demo_engine.py
This fixes the JavaScript syntax error that occurs when highlighting elements with quotes in selectors.
"""

import os

def apply_highlight_fix():
    """Apply the fix to demo_engine.py using simple string replacement"""
    demo_engine_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/demo_engine.py"
    
    # Read the current content
    with open(demo_engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the specific line that needs to be fixed
    # The problematic line looks like:
    old_line = "            script = f\"(function(){{var el=document.querySelector('{selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();\""
    
    # The fixed line that escapes single quotes in the selector
    new_lines = [
        "            # Escape single quotes in the selector to prevent breaking the JavaScript string",
        "            escaped_selector = selector.replace(\"'\", \"\\\\'\")",
        "            script = f\"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();\""
    ]
    new_content = "\\n            ".join(new_lines)
    
    # Replace the old line with the new content
    if old_line in content:
        updated_content = content.replace(old_line, new_content)
        
        # Write back the updated content
        with open(demo_engine_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("Successfully updated demo_engine.py with the highlight fix!")
        print("The fix properly escapes single quotes in CSS selectors to prevent JavaScript syntax errors.")
    else:
        print("Could not find the exact line to replace. Looking for similar patterns...")
        
        # Alternative: Replace using a less exact match
        if "document.querySelector('{selector}')" in content:
            # Find the complete line containing the problematic code
            lines = content.split('\\n')
            modified_lines = []
            replaced = False
            
            for line in lines:
                if "document.querySelector('{selector}')" in line and "f\"(" in line:
                    # This is the line we need to replace
                    if not replaced:
                        modified_lines.extend([
                            "            # Escape single quotes in the selector to prevent breaking the JavaScript string",
                            "            escaped_selector = selector.replace(\"'\", \"\\\\'\")",
                            "            script = f\"(function(){{var el=document.querySelector('{escaped_selector}');if(!el) return false;var old=el.style.boxShadow;var old2=el.style.outline;el.style.outline='3px solid #f59e0b';el.style.boxShadow='0 0 18px rgba(245,158,11,0.8)';setTimeout(function(){{el.style.boxShadow=old;el.style.outline=old2;}}, {int(duration*1000)});return true;}})();\""
                        ])
                        replaced = True
                    else:
                        modified_lines.append(line)
                else:
                    modified_lines.append(line)
            
            if replaced:
                updated_content = '\\n'.join(modified_lines)
                with open(demo_engine_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print("Successfully updated demo_engine.py with the highlight fix!")
                print("The fix properly escapes single quotes in CSS selectors to prevent JavaScript syntax errors.")
            else:
                print("Could not find the expected pattern in the file.")
        else:
            print("Could not locate the problematic code in demo_engine.py")


if __name__ == "__main__":
    # Verify file exists first
    demo_engine_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/demo_engine.py"
    if os.path.exists(demo_engine_path):
        apply_highlight_fix()
    else:
        print(f"Error: {demo_engine_path} does not exist!")