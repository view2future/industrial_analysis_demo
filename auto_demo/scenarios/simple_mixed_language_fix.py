#!/usr/bin/env python3
"""
Simple fix to handle mixed language content in detailed content section
"""

def simple_mixed_language_fix():
    """Simple fix for mixed language content readability"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/report_view_upload.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simplify the CSS - remove the complex mixed language CSS and revert to a cleaner approach
    # First remove the JavaScript
    if "<script>" in content and "</script>{% endblock %}" in content:
        # Remove the JavaScript block
        js_start = content.rfind("<script>")
        js_end = content.find("</script>{% endblock %}")
        if js_start != -1 and js_end != -1:
            js_end = js_end + len("</script>")
            content = content[:js_start] + content[js_end:]
    
    # Simplify content processing to be less aggressive
    # Revert to simpler content processing - just basic paragraph handling
    old_top_content = """                    {% if category_data.top_content %}
                    <div class="prose max-w-none mixed-content">
                        {% for content in category_data.top_content %}
                        <div class="mb-4 p-4 bg-white border-l-4 border-indigo-500 rounded-r-lg shadow-sm chinese-content">
                            {% if is_json_content(content) %}
                                <div class="json-container">{{ format_json_content(content) | safe }}</div>
                            {% else %}
                                <!-- Format plain content with proper paragraph structure for mixed language -->
                                {% set content_paragraphs = content.split('\\n\\n') %}
                                {% for para in content_paragraphs %}
                                    {% if para.strip() %}
                                        <p class="mb-3 text-gray-700 leading-relaxed content-item">{{ para.strip() | replace('\\n', '<br>') | safe }}</p>
                                    {% endif %}
                                {% endfor %}
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>"""
    
    # Simpler processing
    new_top_content = """                    {% if category_data.top_content %}
                    <div class="prose max-w-none">
                        {% for content in category_data.top_content %}
                        <div class="mb-4 p-4 bg-gray-50 rounded-lg border-l-4 border-indigo-500">
                            {% if is_json_content(content) %}
                                <div class="json-container">{{ format_json_content(content) | safe }}</div>
                            {% else %}
                                {{ content }}
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>"""
    
    # And for key_points
    old_key_points = """                    {% elif category_data.key_points %}
                    <div class="prose max-w-none mixed-content">
                        <ul class="space-y-3 chinese-content">
                            {% for point in category_data.key_points %}
                            <li class="p-3 bg-gradient-to-r from-white to-gray-50 rounded-lg border border-gray-100 list-item content-item">
                                {% if is_json_content(point) %}
                                    <div class="json-container">{{ format_json_content(point) | safe }}</div>
                                {% else %}
                                    <!-- Format plain points with proper paragraph structure for mixed language -->
                                    {% set point_paragraphs = point.split('\\n\\n') %}
                                    {% for para in point_paragraphs %}
                                        {% if para.strip() %}
                                            <p class="mb-2 text-gray-700 leading-relaxed">{{ para.strip() | replace('\\n', '<br>') | safe }}</p>
                                        {% endif %}
                                    {% endfor %}
                                {% endif %}
                            </li>
                            {% endfor %}
                        </ul>
                    </div>"""
    
    new_key_points = """                    {% elif category_data.key_points %}
                    <div class="prose max-w-none">
                        <ul class="space-y-3">
                            {% for point in category_data.key_points %}
                            <li class="p-3 bg-gray-50 rounded-lg border-l-4 border-indigo-500">
                                {% if is_json_content(point) %}
                                    <div class="json-container">{{ format_json_content(point) | safe }}</div>
                                {% else %}
                                    {{ point }}
                                {% endif %}
                            </li>
                            {% endfor %}
                        </ul>
                    </div>"""
    
    # Also revert the CSS to be simpler - remove the complex mixed language CSS
    # Keep only the basic readability CSS and remove the complex mixed language part
    if "/* Mixed-language text improvements */" in content:
        # Find the start of mixed language CSS and the end of the style block
        css_start = content.find("/* Mixed-language text improvements */")
        # Find the end of the style block
        style_end = content.find("</style>")
        if css_start != -1 and style_end != -1 and css_start < style_end:
            # Keep only the part before the mixed language CSS
            content = content[:css_start] + content[style_end:]
            # Add back a simpler word-break CSS
            content = content[:content.find("</style>")] + """
/* Basic word break for mixed content */
.bg-gray-50, .text-gray-800 {
    word-break: break-word;
    overflow-wrap: break-word;
}
""" + content[content.find("</style>"):]

    # Replace the sections with simpler versions
    content = content.replace(old_top_content, new_top_content)
    content = content.replace(old_key_points, new_key_points)
    
    # Write back the updated content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Reverted to simpler content processing for mixed language content!")


if __name__ == "__main__":
    simple_mixed_language_fix()