#!/usr/bin/env python3
"""
Fix the end of the highlight function to include proper error logging
"""

def fix_function_end():
    """Fix the end of the _action_highlight function"""
    demo_engine_path = "/Users/wangyu94/regional-industrial-dashboard/auto_demo/demo_engine.py"
    
    # Read the current content
    with open(demo_engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The function should end with proper error logging
    old_ending = """        except Exception as e:
            return False
    
    async def _display_subtitle"""
    
    new_ending = """        except Exception as e:
            logger.error(f"Highlight failed for {selector}: {e}")
            return False
    
    async def _display_subtitle"""
    
    # Replace the ending
    updated_content = content.replace(old_ending, new_ending)
    
    # Write back the corrected content
    with open(demo_engine_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Fixed the ending of the _action_highlight function with proper error logging!")


if __name__ == "__main__":
    fix_function_end()