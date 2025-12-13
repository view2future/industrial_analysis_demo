#!/usr/bin/env python3
"""
Script to add CSS styling for better readability of original content in report_view_upload.html
"""

def improve_original_content_css():
    """Add CSS styling for better readability of original content"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/report_view_upload.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the extra_head block and add CSS
    if "{% block extra_head %}" in content and "{% endblock %}" in content:
        # Find the extra_head block
        head_start = content.find("{% block extra_head %}")
        head_end = content.find("{% endblock %}", head_start)
        
        # Extract the content inside extra_head
        head_content_start = head_start + len("{% block extra_head %}")
        head_content = content[head_content_start:head_end].strip()
        
        # Add CSS for better readability if it's not already there
        css_to_add = """
<style>
.original-content-readable {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #333;
    max-width: 100%;
    overflow-x: auto;
}
.original-content-readable p {
    margin-bottom: 1.5rem;
    text-align: justify;
    hyphens: auto;
}
.original-content-readable h1, 
.original-content-readable h2, 
.original-content-readable h3,
.original-content-readable h4,
.original-content-readable h5,
.original-content-readable h6 {
    margin-top: 2rem;
    margin-bottom: 1rem;
    color: #2d3748;
    font-weight: 600;
}
.original-content-readable h1 {
    font-size: 1.8rem;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.3rem;
}
.original-content-readable h2 {
    font-size: 1.6rem;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.3rem;
}
.original-content-readable h3 {
    font-size: 1.4rem;
}
.original-content-readable h4 {
    font-size: 1.2rem;
}
.original-content-readable h5 {
    font-size: 1.1rem;
}
.original-content-readable h6 {
    font-size: 1.0rem;
    color: #4a5568;
}
.original-content-readable pre {
    background: #f7fafc;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin: 1rem 0;
    border: 1px solid #e2e8f0;
}
.original-content-readable code {
    background: #edf2f7;
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}
.original-content-readable blockquote {
    border-left: 4px solid #cbd5e0;
    padding-left: 1rem;
    margin: 1rem 0;
    color: #4a5568;
    font-style: italic;
}
.original-content-readable ul, .original-content-readable ol {
    margin: 1rem 0;
    padding-left: 2rem;
}
.original-content-readable li {
    margin-bottom: 0.5rem;
    line-height: 1.6;
}
.original-content-readable table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    overflow-x: auto;
}
.original-content-readable table, 
.original-content-readable th, 
.original-content-readable td {
    border: 1px solid #cbd5e0;
}
.original-content-readable th, .original-content-readable td {
    padding: 0.5rem 1rem;
    text-align: left;
}
.original-content-readable th {
    background-color: #f7fafc;
    font-weight: 600;
}
.original-content-readable a {
    color: #4299e1;
    text-decoration: underline;
}
.original-content-readable a:hover {
    color: #2b6cb0;
}
.original-content-readable strong {
    font-weight: 600;
}
.original-content-readable em {
    font-style: italic;
}
.original-content-readable hr {
    border: 0;
    height: 1px;
    background: #e2e8f0;
    margin: 2rem 0;
}
</style>"""
        
        # Check if the CSS is already in the head
        if "original-content-readable" not in head_content:
            # Add the CSS to the head content
            new_head_content = head_content + css_to_add
            # Replace the head block with the updated content
            updated_content = content[:head_start] + "{% block extra_head %}\n" + new_head_content + "\n{% endblock %}" + content[head_end + len("{% endblock %}"):]
            
            # Write back the updated content
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("Added CSS styling for better readability of original content!")
        else:
            print("CSS styling for original content already exists.")
    else:
        print("Could not find extra_head block to add CSS.")


if __name__ == "__main__":
    improve_original_content_css()