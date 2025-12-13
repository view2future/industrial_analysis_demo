#!/usr/bin/env python3
"""
Script to add CSS styling for JSON content to make it more readable
"""

def add_json_css_styling():
    """Add CSS styling for JSON content readability"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/report_view_upload.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add JSON-specific styling to the existing CSS
    json_css = """
.json-container {
    font-family: 'Courier New', Consolas, Monaco, monospace;
    font-size: 14px;
    line-height: 1.5;
    background: #f8fafc;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #e2e8f0;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.json-row {
    margin: 0.25rem 0;
    display: block;
}

.json-key {
    color: #b16286;
    font-weight: bold;
    font-style: italic;
}

.json-value {
    color: #458588;
    margin-left: 0.5rem;
}

.json-index {
    color: #d79921;
    font-weight: bold;
}

.json-nested {
    border-left: 2px solid #cbd5e0;
    margin-left: 0.5rem;
    padding-left: 1rem;
}

.text-content {
    line-height: 1.8;
    color: #333;
}
"""
    
    # Find the style tag we just added and append JSON styling
    if ".original-content-readable" in content and "</style>" in content:
        # Find the closing </style> tag and insert the JSON CSS before it
        pos = content.rfind("</style>")
        updated_content = content[:pos] + json_css + content[pos:]
        
        # Write back the updated content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("Added CSS styling for JSON content readability!")
    else:
        print("Could not find the style block to add JSON CSS.")


if __name__ == "__main__":
    add_json_css_styling()