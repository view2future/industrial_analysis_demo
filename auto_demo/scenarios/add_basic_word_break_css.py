#!/usr/bin/env python3
"""
Simple fix: Add proper word break CSS for mixed language text
"""

def add_basic_word_break_css():
    """Add the most basic CSS fix for mixed language content"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/report_view_upload.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the style section and add basic word break support
    # Add this to the existing CSS for original content
    basic_word_break_css = """
/* Basic word break support for mixed Chinese-English content */
.original-content-readable,
.json-container,
.bg-gray-50,
.content-item {
    word-break: break-word;
    overflow-wrap: break-word;
    line-break: loose;
    -webkit-hyphens: auto;
    -moz-hyphens: auto;
    hyphens: auto;
    line-height: 1.7;
}
"""
    
    # Find the end of the existing CSS styles in the <style> tag and add the word break CSS
    if ".text-content {" in content and "</style>" in content:
        # Find the last closing brace before </style>
        style_end = content.find("</style>")
        # Insert the CSS before </style>
        updated_content = content[:style_end] + basic_word_break_css + content[style_end:]
        
        # Write back the updated content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("Added basic word break CSS for mixed language content!")
    else:
        print("Could not find style block to add CSS.")


if __name__ == "__main__":
    add_basic_word_break_css()