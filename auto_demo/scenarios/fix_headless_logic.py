#!/usr/bin/env python3
"""
Script to fix the headless/headed mode logic in start_demo.py
"""

def fix_headless_logic():
    """Fix the headless/headed mode logic in start_demo.py"""
    start_demo_path = "/Users/wangyu94/regional-industrial-dashboard/start_demo.py"
    
    # Read the current content
    with open(start_demo_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the problematic logic
    old_logic = """    # Determine headless mode
    headless = not args.headed if args.headed else True"""
    
    new_logic = """    # Determine headless mode
    if args.headed:
        headless = False
    elif args.headless:
        headless = True
    else:
        headless = True  # Default to headless if neither flag is specified"""
    
    # Replace the old logic with the new logic
    updated_content = content.replace(old_logic, new_logic)
    
    # Write back the updated content
    with open(start_demo_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Successfully updated the headless/headed logic in start_demo.py!")


if __name__ == "__main__":
    fix_headless_logic()