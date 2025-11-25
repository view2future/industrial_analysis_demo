#!/usr/bin/env python3
"""Test Kimi API SWOT generation"""
from openai import OpenAI
import json
import re

config = json.load(open('config.json'))
api_key = config['api_keys']['kimi_api_key']

client = OpenAI(
    api_key=api_key,
    base_url='https://api.moonshot.cn/v1'
)

test_prompt = '''请对成都汽车产业进行SWOT分析，严格按以下JSON格式输出：
{
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["劣势1", "劣势2"],
    "opportunities": ["机遇1", "机遇2"],
    "threats": ["威胁1", "威胁2"]
}

只输出JSON，不要其他文字。'''

print('正在调用Kimi API...')
response = client.chat.completions.create(
    model='moonshot-v1-128k',
    messages=[
        {'role': 'system', 'content': '你是专业分析师，只输出JSON格式结果，不要markdown标记。'},
        {'role': 'user', 'content': test_prompt}
    ],
    temperature=0.7,
    max_tokens=2000
)

result = response.choices[0].message.content
print('原始响应:')
print(result)
print('\n解析测试:')
cleaned = re.sub(r'^```json\s*', '', result)
cleaned = re.sub(r'^```\s*', '', cleaned)
cleaned = re.sub(r'\s*```$', '', cleaned)
cleaned = cleaned.strip()
print('清理后:')
print(cleaned[:500])
try:
    parsed = json.loads(cleaned)
    print('✓ JSON解析成功')
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
except Exception as e:
    print(f'✗ 解析失败: {e}')
