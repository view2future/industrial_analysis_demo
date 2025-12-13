#!/usr/bin/env python3
"""
Script to add CSS for better handling of mixed Chinese-English text in report_view_upload.html
"""

def add_mixed_language_css():
    """Add CSS for better mixed Chinese-English text handling"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/report_view_upload.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add CSS for better mixed-language text handling
    mixed_language_css = """
/* Mixed-language text improvements */
.text-content,
.original-content-readable,
.prose,
.json-container {
    word-wrap: break-word;
    word-break: break-word;
    overflow-wrap: break-word;
    line-break: strict;
    -webkit-hyphens: auto;
    -moz-hyphens: auto;
    -ms-hyphens: auto;
    hyphens: auto;
}

/* Specific handling for mixed Chinese-English text */
.mixed-content {
    white-space: pre-wrap;
    word-break: break-all;
    overflow-wrap: break-word;
}

/* Improve readability for key points and content */
.content-item {
    line-height: 1.7;
    text-align: left;
    -webkit-text-size-adjust: 100%;
}

/* Better handling for lists in mixed language content */
ul.space-y-3 li {
    line-height: 1.6;
    word-break: break-word;
}

/* For Chinese text specifically */
.chinese-content {
    line-height: 1.8;
    letter-spacing: 0.01em;
    word-break: break-word;
}
"""
    
    # Find the style tag and append mixed language styling
    if ".original-content-readable" in content and "</style>" in content:
        # Find the closing </style> tag and insert the mixed language CSS before it
        pos = content.rfind("</style>")
        updated_content = content[:pos] + mixed_language_css + content[pos:]
        
        # Write back the updated content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("Added CSS for better mixed Chinese-English text handling!")
    else:
        print("Could not find the style block to add mixed language CSS.")


if __name__ == "__main__":
    add_mixed_language_css()