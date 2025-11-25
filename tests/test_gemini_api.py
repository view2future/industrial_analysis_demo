#!/usr/bin/env python3
"""
测试 Google Gemini API 集成
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
    """测试 API 基础连接"""
    print("\n" + "="*80)
    print("🧪 测试 Google Gemini API 连接")
    print("="*80 + "\n")
    
    try:
        import google.generativeai as genai
        print("✓ google.generativeai 库导入成功")
        print(f"  版本: {genai.__version__}")
        
        # 加载配置
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        api_key = config['api_keys']['google_gemini_api_key']
        print(f"\n✓ API Key 已加载")
        print(f"  前10位: {api_key[:10]}...")
        print(f"  长度: {len(api_key)} 字符")
        
        # 配置 API
        print(f"\n⏳ 配置 Gemini API...")
        genai.configure(api_key=api_key)
        print("✓ API 配置成功")
        
        # 初始化模型
        print(f"\n⏳ 初始化 gemini-1.5-pro-latest 模型...")
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        print(f"✓ 模型初始化成功: {model.model_name}")
        
        # 测试简单调用
        print(f"\n⏳ 测试 API 调用...")
        print(f"  提示词: '你好，请说\"测试成功\"'")
        
        import time
        start_time = time.time()
        
        response = model.generate_content(
            "你好，请说\"测试成功\"",
            generation_config={'max_output_tokens': 50}
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ API 调用成功！")
        print(f"  耗时: {elapsed:.2f} 秒")
        print(f"  响应长度: {len(response.text)} 字符")
        print(f"  响应内容: {response.text}")
        
        print("\n" + "="*80)
        print("🎉 Google Gemini API 集成测试通过！")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败！")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        
        if 'UNAVAILABLE' in str(e) or 'timeout' in str(e).lower():
            print(f"\n⚠️  这是网络连接问题:")
            print(f"  1. 检查能否访问 generativelanguage.googleapis.com")
            print(f"  2. 如在中国大陆，需要配置网络代理")
            print(f"  3. 参考 NETWORK_SETUP.md 配置代理")
        
        import traceback
        print(f"\n详细错误:")
        traceback.print_exc()
        
        return False


def test_llm_generator():
    """测试 LLM 报告生成器"""
    print("\n" + "="*80)
    print("🧪 测试 LLM 报告生成器")
    print("="*80 + "\n")
    
    try:
        from src.ai.llm_generator import LLMReportGenerator
        
        print("⏳ 初始化 LLM 报告生成器...")
        generator = LLMReportGenerator()
        
        print("\n⏳ 生成测试报告...")
        print("  城市: 测试市")
        print("  行业: 测试行业")
        
        result = generator.generate_report(
            city="成都",
            industry="人工智能",
            additional_context="请生成一份简短的测试报告，200字以内"
        )
        
        if result.get('success'):
            print(f"\n✅ 报告生成成功！")
            print(f"  报告长度: {len(result['full_content'])} 字符")
            print(f"  章节数: {len(result['sections'])}")
            print(f"  章节列表: {list(result['sections'].keys())}")
            print(f"\n  报告预览 (前200字):")
            print(f"  {result['full_content'][:200]}...")
            
            print("\n" + "="*80)
            print("🎉 LLM 报告生成器测试通过！")
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
    print("  Google Gemini API 集成测试工具")
    print("█" * 80)
    
    # 测试 1: API 连接
    api_ok = test_api_connection()
    
    if api_ok:
        # 测试 2: LLM 报告生成器
        generator_ok = test_llm_generator()
        
        if generator_ok:
            print("\n✅ 所有测试通过！系统已就绪，可以开始使用。\n")
            sys.exit(0)
        else:
            print("\n⚠️  API 连接正常，但报告生成器有问题。\n")
            sys.exit(1)
    else:
        print("\n❌ API 连接失败，请先解决网络问题。")
        print("   参考 NETWORK_SETUP.md 配置网络代理。\n")
        sys.exit(1)
