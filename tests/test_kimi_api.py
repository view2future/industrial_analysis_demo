#!/usr/bin/env python3
"""
测试 Kimi API 集成
用于验证 API 配置是否正确
"""

import sys
import os
import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_api_connection():
    """测试 Kimi API 基础连接"""
    print("\n" + "="*80)
    print("🧪 测试 Kimi API 连接")
    print("="*80 + "\n")
    
    try:
        from openai import OpenAI
        print("✓ openai 库导入成功")
        
        # 加载配置
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        api_key = config['api_keys']['kimi_api_key']
        print(f"\n✓ API Key 已加载")
        print(f"  前10位: {api_key[:10]}...")
        print(f"  长度: {len(api_key)} 字符")
        
        # 配置客户端
        print(f"\n⏳ 初始化 Kimi 客户端...")
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
        print("✓ 客户端初始化成功")
        
        # 测试简单调用
        print(f"\n⏳ 测试 API 调用...")
        print(f"  模型: moonshot-v1-8k")
        print(f"  提示词: '你好，请说\"测试成功\"'")
        
        import time
        start_time = time.time()
        
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "user", "content": "你好，请说'测试成功'"}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        elapsed = time.time() - start_time
        
        response_text = completion.choices[0].message.content
        
        print(f"\n✅ API 调用成功！")
        print(f"  耗时: {elapsed:.2f} 秒")
        print(f"  响应内容: {response_text}")
        print(f"  Token 使用:")
        print(f"    - Prompt: {completion.usage.prompt_tokens}")
        print(f"    - Completion: {completion.usage.completion_tokens}")
        print(f"    - Total: {completion.usage.total_tokens}")
        
        print("\n" + "="*80)
        print("🎉 Kimi API 集成测试通过！")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败！")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        
        import traceback
        print(f"\n详细错误:")
        traceback.print_exc()
        
        return False


def test_llm_generator():
    """测试 LLM 报告生成器"""
    print("\n" + "="*80)
    print("🧪 测试 Kimi LLM 报告生成器")
    print("="*80 + "\n")
    
    try:
        from src.ai.llm_generator import LLMReportGenerator
        
        print("⏳ 初始化 LLM 报告生成器...")
        generator = LLMReportGenerator()
        
        print("\n⏳ 生成测试报告...")
        print("  城市: 成都")
        print("  行业: 人工智能")
        print("  要求: 简短测试报告，500字以内")
        
        result = generator.generate_report(
            city="成都",
            industry="人工智能",
            additional_context="这是一个API测试，请生成一份简短的测试报告，500字以内即可。"
        )
        
        if result.get('success'):
            print(f"\n✅ 报告生成成功！")
            print(f"  报告长度: {len(result['full_content'])} 字符")
            print(f"  章节数: {len(result['sections'])}")
            print(f"  章节列表: {list(result['sections'].keys())}")
            
            # Token 使用情况
            tokens = result['metadata'].get('tokens', {})
            if tokens:
                print(f"\n  Token 使用:")
                print(f"    - Prompt: {tokens.get('prompt', 0)}")
                print(f"    - Completion: {tokens.get('completion', 0)}")
                print(f"    - Total: {tokens.get('total', 0)}")
            
            print(f"\n  报告预览 (前300字):")
            print(f"  {result['full_content'][:300]}...")
            
            print("\n" + "="*80)
            print("🎉 Kimi LLM 报告生成器测试通过！")
            print("="*80 + "\n")
            return True
        else:
            print(f"\n❌ 报告生成失败！")
            print(f"  错误: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败！")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        
        import traceback
        print(f"\n详细错误:")
        traceback.print_exc()
        
        return False


if __name__ == '__main__':
    print("\n")
    print("█" * 80)
    print("  Kimi API 集成测试工具")
    print("█" * 80)
    
    # 测试 1: API 连接
    api_ok = test_api_connection()
    
    if api_ok:
        # 测试 2: LLM 报告生成器
        generator_ok = test_llm_generator()
        
        if generator_ok:
            print("\n✅ 所有测试通过！系统已就绪，可以开始使用。\n")
            print("💡 提示: Kimi API 无需代理，可直接访问\n")
            sys.exit(0)
        else:
            print("\n⚠️  API 连接正常，但报告生成器有问题。\n")
            sys.exit(1)
    else:
        print("\n❌ API 连接失败，请检查:")
        print("   1. API Key 是否正确")
        print("   2. 网络连接是否正常")
        print("   3. config.json 配置是否正确\n")
        sys.exit(1)
