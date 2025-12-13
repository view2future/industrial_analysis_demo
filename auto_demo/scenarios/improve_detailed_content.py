#!/usr/bin/env python3
"""
Script to improve readability of the detailed content sections in report_view_upload.html
"""

def improve_detailed_content_formatting():
    """Improve readability of the detailed content sections"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/report_view_upload.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the detailed content section and improve it
    old_detailed_content = """        <!-- Categories Content （详细内容）-->
        {% if report_data.categories %}
        <div class="bg-white rounded-xl shadow-lg p-6">
            <h3 class="text-2xl font-bold text-gray-800 mb-6">
                <i class="fas fa-folder-open mr-2 text-indigo-600"></i>详细内容
            </h3>
            <div class="space-y-6">
                {% for category_name, category_data in report_data.categories.items() %}
                <div class="border-b pb-6 last:border-b-0">
                    <h4 class="text-xl font-semibold text-gray-800 mb-3">
                        {{ category_name }}
                        <span class="text-sm text-gray-500 ml-2">(相关度: {{ category_data.relevance_score }})</span>
                    </h4>
                    {% if category_data.top_content %}
                    <div class="bg-gray-50 p-4 rounded-lg space-y-3">
                        {% for content in category_data.top_content %}
                        <div class="text-gray-800 leading-relaxed pb-3 border-b last:border-b-0" style="word-break: break-word; overflow-wrap: anywhere;">
                            {% if is_json_content(content) %}
                                <div class="bg-white p-3 rounded border-l-4 border-blue-500">{{ format_json_content(content) | safe }}</div>
                            {% else %}
                                {{ content }}
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    {% elif category_data.key_points %}
                    <div class="bg-gray-50 p-4 rounded-lg space-y-3">
                        {% for point in category_data.key_points %}
                        <div class="text-gray-800 leading-relaxed pb-3 border-b last:border-b-0" style="word-break: break-word; overflow-wrap: anywhere;">
                            {% if is_json_content(point) %}
                                <div class="bg-white p-3 rounded border-l-4 border-blue-500">{{ format_json_content(point) | safe }}</div>
                            {% else %}
                                {{ point }}
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}"""
    
    new_detailed_content = """        <!-- Categories Content （详细内容）-->
        {% if report_data.categories %}
        <div class="bg-white rounded-xl shadow-lg p-6">
            <h3 class="text-2xl font-bold text-gray-800 mb-6">
                <i class="fas fa-folder-open mr-2 text-indigo-600"></i>详细内容
            </h3>
            <div class="space-y-8">
                {% for category_name, category_data in report_data.categories.items() %}
                <div class="border border-gray-200 rounded-xl p-6 last:border-b-0 transition-all hover:shadow-md">
                    <div class="flex items-center justify-between mb-4">
                        <h4 class="text-xl font-semibold text-gray-800">
                            {{ category_name }}
                        </h4>
                        <span class="text-sm bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full">
                            相关度: {{ category_data.relevance_score }}
                        </span>
                    </div>
                    {% if category_data.top_content %}
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
                    </div>
                    {% elif category_data.key_points %}
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
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}"""
    
    # Replace the detailed content section
    updated_content = content.replace(old_detailed_content, new_detailed_content)
    
    # Write back the updated content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Improved readability of detailed content sections in report_view_upload.html!")


if __name__ == "__main__":
    improve_detailed_content_formatting()