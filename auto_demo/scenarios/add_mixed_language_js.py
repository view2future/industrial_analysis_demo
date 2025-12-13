#!/usr/bin/env python3
"""
Script to add JavaScript for better mixed Chinese-English text handling
"""

def add_mixed_language_js():
    """Add JavaScript for better mixed Chinese-English text handling"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/report_view_upload.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the end of the template to add JavaScript
    if "{% endblock %}" in content and content.count("{% endblock %}") > 2:
        # Find the last endblock which should be the content block
        pos = content.rfind("{% endblock %}", 0, content.rfind("{% endblock %}"))
        js_content = """
<script>
// JavaScript to improve mixed Chinese-English text rendering
document.addEventListener('DOMContentLoaded', function() {
    // Apply special handling to content areas with mixed language text
    const contentElements = document.querySelectorAll('.content-item, .original-content-readable, .chinese-content, .mixed-content');
    
    contentElements.forEach(function(element) {
        // Ensure proper line breaking for mixed Chinese-English content
        element.style.wordBreak = 'break-word';
        element.style.overflowWrap = 'break-word';
        element.style.lineHeight = '1.7';
        
        // Check if element contains mixed language content
        const text = element.textContent || element.innerText;
        if (hasMixedLanguage(text)) {
            // Apply additional styles for better readability
            element.style.letterSpacing = '0.02em';
        }
    });
    
    // Function to detect mixed Chinese-English content
    function hasMixedLanguage(text) {
        // Check for both Chinese characters and English letters
        const hasChinese = /[\u4e00-\u9fff]/.test(text);
        const hasEnglish = /[a-zA-Z]/.test(text);
        return hasChinese && hasEnglish;
    }
    
    // For paragraphs, ensure proper line-height and spacing
    const paragraphs = document.querySelectorAll('p');
    paragraphs.forEach(function(p) {
        p.style.lineHeight = '1.8';
        p.style.textAlign = 'left';
        p.style.hyphens = 'auto';
    });
});
</script>"""
        
        updated_content = content[:pos] + js_content + content[pos:]
        
        # Write back the updated content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("Added JavaScript for better mixed Chinese-English text handling!")
    else:
        print("Could not find suitable location to add JavaScript.")


if __name__ == "__main__":
    add_mixed_language_js()