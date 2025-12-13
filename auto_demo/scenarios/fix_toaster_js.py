#!/usr/bin/env python3
"""
Script to fix the toaster.js file to allow clicking regardless of task count
"""

def fix_toaster_js():
    """Fix the click handler in toaster.js to not require tasks to be present"""
    toaster_js_path = "/Users/wangyu94/regional-industrial-dashboard/static/js/toaster.js"
    
    # Read the current content
    with open(toaster_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic section and fix it
    old_click_handler = """    bindEvents() {
        // Long press on toaster
        let pressTimer;
        this.toasterBody.addEventListener('mousedown', () => {
            pressTimer = setTimeout(() => this.openTaskPanel(), 8000); // 800ms long press
        });
        this.toasterBody.addEventListener('mouseup', () => clearTimeout(pressTimer));
        this.toasterBody.addEventListener('mouseleave', () => clearTimeout(pressTimer));
        
        // Click to toggle panel (short click)
        this.toasterBody.addEventListener('click', (e) => {
            if (e.detail === 1) { // Simple click
                if (this.tasks.length > 0) {
                    this.togglePanel();
                }
            }
        });
    }"""
    
    # Fixed version that allows clicking regardless of task count
    new_click_handler = """    bindEvents() {
        // Long press on toaster
        let pressTimer;
        this.toasterBody.addEventListener('mousedown', () => {
            pressTimer = setTimeout(() => this.openTaskPanel(), 8000); // 800ms long press
        });
        this.toasterBody.addEventListener('mouseup', () => clearTimeout(pressTimer));
        this.toasterBody.addEventListener('mouseleave', () => clearTimeout(pressTimer));
        
        // Click to toggle panel (short click)
        this.toasterBody.addEventListener('click', (e) => {
            if (e.detail === 1) { // Simple click
                // Always allow toggling the panel, regardless of task count
                this.togglePanel();
            }
        });
    }"""
    
    # Replace the old code with the new code
    updated_content = content.replace(old_click_handler, new_click_handler)
    
    # Write back the updated content
    with open(toaster_js_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Successfully updated toaster.js to allow clicking regardless of task count!")


if __name__ == "__main__":
    fix_toaster_js()