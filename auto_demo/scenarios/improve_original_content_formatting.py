#!/usr/bin/env python3
"""
Script to improve the original report content display in report_view_upload.html
"""

def improve_original_content_formatting():
    """Improve the original report content display formatting"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/report_view_upload.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the original content section and improve it
    old_original_content = """    <!-- Original Report Content （报告原文）-->
    {% if report and report.file_path %}
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">
                <i class="fas fa-file-alt mr-2 text-gray-600"></i>报告原文
            </h2>
            <div class="border border-gray-200 rounded-lg p-6 bg-white">
                <div class="markdown-content" style="word-break: break-word; overflow-wrap: anywhere;">
                    {% if report_data.full_content %}
                        {{ render_markdown(report_data.full_content) | safe }}
                    {% elif report.original_content %}
                        {% if is_json_content(report.original_content) %}
                            <div class="bg-gray-50 p-4 rounded">{{ format_json_content(report.original_content) | safe }}</div>
                        {% else %}
                            <div style="white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere;">
                                {{ report.original_content }}
                            </div>
                        {% endif %}
                    {% else %}
                        <p class="text-gray-500">原文内容不可用</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    {% endif %}"""
    
    new_original_content = """    <!-- Original Report Content （报告原文）-->
    {% if report and report.file_path %}
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">
                <i class="fas fa-file-alt mr-2 text-gray-600"></i>报告原文
            </h2>
            <div class="border border-gray-200 rounded-lg p-6 bg-white">
                <div class="markdown-content max-w-none">
                    {% if report_data.full_content %}
                        {{ render_markdown(report_data.full_content) | safe }}
                    {% elif report.original_content %}
                        {% if is_json_content(report.original_content) %}
                            <div class="bg-gray-50 p-4 rounded font-mono text-sm overflow-x-auto">{{ format_json_content(report.original_content) | safe }}</div>
                        {% else %}
                            <!-- Try to convert plain original content to markdown format for better readability -->
                            {% set original_md = report.original_content %}
                            {% if original_md %}
                                <!-- Replace double newlines with markdown paragraphs, but keep the content readable -->
                                <div class="original-content-readable">
                                    {% set paragraphs = original_md.split('\\n\\n') %}
                                    {% for para in paragraphs %}
                                        {% if para.strip() %}
                                            <p class="mb-4 text-gray-700 leading-relaxed">{{ para.strip() | replace('\\n', '<br>') | safe }}</p>
                                        {% endif %}
                                    {% endfor %}
                                </div>
                            {% else %}
                                <p class="text-gray-500">原文内容不可用</p>
                            {% endif %}
                        {% endif %}
                    {% else %}
                        <p class="text-gray-500">原文内容不可用</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    {% endif %}"""
    
    # Replace the original content section
    updated_content = content.replace(old_original_content, new_original_content)
    
    # Additional improvement: Add CSS for better readability
    if "</style>" in updated_content:
        # Find the extra_css block and add readability styles
        css_addition = """
    .original-content-readable {
        font-size: 16px;
        line-height: 1.8;
        color: #333;
    }
    .original-content-readable p {
        margin-bottom: 1.5rem;
        text-align: justify;
    }
    .original-content-readable pre {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
        margin: 1rem 0;
    }
    .original-content-readable code {
        background: #f1f3f5;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-family: monospace;
    }"""
        
        # Find the extra_css block end
        if "{% endblock %}" in updated_content and "extra_css" in updated_content:
            pos = updated_content.find("{% endblock %}", updated_content.find("{% block extra_css %}"))
            if pos != -1:
                updated_content = updated_content[:pos] + css_addition + updated_content[pos:]
    
    # Write back the updated content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Improved the original report content display in report_view_upload.html for better readability!")


if __name__ == "__main__":
    improve_original_content_formatting()