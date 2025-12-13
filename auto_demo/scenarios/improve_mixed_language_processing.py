#!/usr/bin/env python3
"""
Script to improve content processing for mixed Chinese-English text in report_view_upload.html
"""

def improve_mixed_language_content_processing():
    """Improve content processing for mixed Chinese-English text"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/report_view_upload.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the detailed content section and improve the content handling
    # The issue is likely with how content is split and processed
    # Looking at the current implementation, I need to improve the paragraph handling
    
    # Update the content processing for top_content
    old_top_content = """                    {% if category_data.top_content %}
                    <div class="prose max-w-none">
                        {% for content in category_data.top_content %}
                        <div class="mb-4 p-4 bg-white border-l-4 border-indigo-500 rounded-r-lg shadow-sm">
                            {% if is_json_content(content) %}
                                <div class="json-container">{{ format_json_content(content) | safe }}</div>
                            {% else %}
                                <!-- Format plain content with proper paragraph structure -->
                                {% set content_paragraphs = content.split('\\n\\n') %}
                                {% for para in content_paragraphs %}
                                    {% if para.strip() %}
                                        <p class="mb-3 text-gray-700 leading-relaxed">{{ para.strip() | replace('\\n', '<br>') | safe }}</p>
                                    {% endif %}
                                {% endfor %}
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>"""
    
    new_top_content = """                    {% if category_data.top_content %}
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
    
    # Update the content processing for key_points
    old_key_points = """                    {% elif category_data.key_points %}
                    <div class="prose max-w-none">
                        <ul class="space-y-3">
                            {% for point in category_data.key_points %}
                            <li class="p-3 bg-gradient-to-r from-white to-gray-50 rounded-lg border border-gray-100 list-item">
                                {% if is_json_content(point) %}
                                    <div class="json-container">{{ format_json_content(point) | safe }}</div>
                                {% else %}
                                    <!-- Format plain points with proper paragraph structure -->
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
    
    # Replace both sections
    updated_content = content.replace(old_top_content, new_top_content)
    updated_content = updated_content.replace(old_key_points, new_key_points)
    
    # Write back the updated content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Improved content processing for mixed Chinese-English text in report_view_upload.html!")


if __name__ == "__main__":
    improve_mixed_language_content_processing()