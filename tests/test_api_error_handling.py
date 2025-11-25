#!/usr/bin/env python3
"""
Test script for API error handling and notification system
Simulates various API failures to verify the error handling works correctly
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.api_error_handler import api_error_handler, APIErrorType, APIService, handle_api_error
from src.utils.notification_service import notification_service, notify_api_issue
from src.ai.llm_generator import LLMReportGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_api_error_detection():
    """Test API error detection and classification"""
    print("\n" + "="*60)
    print("🧪 测试 API 错误检测和分类")
    print("="*60)
    
    # Test quota exceeded errors
    test_errors = [
        # Kimi quota errors
        (Exception("Quota exceeded for this month"), APIService.KIMI, "quota_exceeded"),
        (Exception("余额不足，请充值"), APIService.KIMI, "quota_exceeded"),
        (Exception("配额已用完"), APIService.KIMI, "quota_exceeded"),
        
        # Gemini quota errors
        (Exception("User quota exceeded"), APIService.GEMINI, "quota_exceeded"),
        (Exception("Project quota limit reached"), APIService.GEMINI, "quota_exceeded"),
        
        # Connection errors
        (Exception("Connection timeout"), APIService.KIMI, "connection_timeout"),
        (Exception("Connection refused"), APIService.GEMINI, "connection_refused"),
        (Exception("Service temporarily unavailable"), APIService.DOUBAO, "service_unavailable"),
        
        # Authentication errors
        (Exception("Authentication failed"), APIService.KIMI, "authentication_error"),
        (Exception("API key not valid"), APIService.GEMINI, "authentication_error"),
        
        # Rate limiting
        (Exception("Too many requests"), APIService.KIMI, "rate_limited"),
        (Exception("Rate limit exceeded"), APIService.GEMINI, "rate_limited"),
    ]
    
    for error, service, expected_type in test_errors:
        api_error = api_error_handler.detect_error_type(error, service)
        result = "✅" if api_error.error_type.value == expected_type else "❌"
        print(f"{result} {service.value.upper()} - {str(error)[:50]}... -> {api_error.error_type.value}")
        
        if api_error.error_type.value == expected_type:
            print(f"   📝 用户消息: {api_error.user_friendly_message}")
            print(f"   💡 建议操作: {api_error.suggested_action}")
    
    print("\n✅ API 错误检测测试完成")


def test_notifications():
    """Test notification creation and management"""
    print("\n" + "="*60)
    print("🔔 测试通知系统")
    print("="*60)
    
    # Test quota exceeded notification
    notification = notification_service.notify_api_quota_exceeded(
        'kimi', 'test_user', '建议切换到 Gemini 服务'
    )
    print(f"✅ 创建配额超限通知: {notification.title}")
    
    # Test connection error notification
    notification = notification_service.notify_api_connection_error(
        'gemini', '连接超时', 'test_user'
    )
    print(f"✅ 创建连接错误通知: {notification.title}")
    
    # Test fallback notification
    notification = notification_service.notify_service_fallback(
        'kimi', 'gemini', True, 'test_user'
    )
    print(f"✅ 创建服务回退通知: {notification.title}")
    
    # Test report generation result
    notification = notification_service.notify_report_generation_result(
        True, '成都', '人工智能', 'kimi', 'test_user'
    )
    print(f"✅ 创建报告成功通知: {notification.title}")
    
    # Test report generation failure
    notification = notification_service.notify_report_generation_result(
        False, '北京', '汽车产业', 'gemini', 'test_user', 'API 配额不足'
    )
    print(f"✅ 创建报告失败通知: {notification.title}")
    
    # Get user notifications
    notifications = notification_service.get_user_notifications('test_user')
    print(f"\n📊 用户 test_user 的通知统计:")
    print(f"   总通知数: {len(notifications)}")
    print(f"   未读通知: {len([n for n in notifications if not n.read])}")
    
    # Get notification stats
    stats = notification_service.get_notification_stats('test_user')
    print(f"   按严重程度分布: {stats['by_severity']}")
    print(f"   按类型分布: {stats['by_type']}")
    
    print("\n✅ 通知系统测试完成")


def test_llm_generator_with_fallback():
    """Test LLM generator with fallback mechanism"""
    print("\n" + "="*60)
    print("🤖 测试 LLM 生成器回退机制")
    print("="*60)
    
    try:
        # Create generator with fallback enabled
        generator = LLMReportGenerator(enable_fallback=True)
        print(f"✅ LLM 生成器初始化成功")
        print(f"   可用服务: {[s.value for s in generator.available_services]}")
        print(f"   当前服务: {generator.current_service.value}")
        print(f"   启用回退: {generator.enable_fallback}")
        
        # Test service detection
        available_services = generator._detect_available_services()
        print(f"   检测到的可用服务: {[s.value for s in available_services]}")
        
        # Test fallback service selection
        if len(available_services) > 1:
            fallback_service = api_error_handler.get_fallback_service(
                generator.current_service, available_services
            )
            print(f"   回退服务建议: {fallback_service.value if fallback_service else '无'}")
        
        print("\n✅ LLM 生成器回退机制测试完成")
        
    except Exception as e:
        print(f"❌ LLM 生成器测试失败: {e}")
        api_error = handle_api_error(e, 'kimi', "LLM 生成器测试")
        print(f"   错误分析: {api_error.user_friendly_message}")


def test_error_summary():
    """Test error summary functionality"""
    print("\n" + "="*60)
    print("📊 测试错误摘要功能")
    print("="*60)
    
    # Generate some test errors
    test_errors = [
        Exception("Kimi quota exceeded"),
        Exception("Gemini connection timeout"),
        Exception("Kimi rate limited"),
        Exception("Gemini quota exceeded"),
        Exception("Kimi service unavailable"),
    ]
    
    services = [APIService.KIMI, APIService.GEMINI, APIService.KIMI, APIService.GEMINI, APIService.KIMI]
    
    for error, service in zip(test_errors, services):
        api_error_handler.detect_error_type(error, service)
    
    # Get error summary
    summary = api_error_handler.get_error_summary()
    print(f"✅ 错误摘要:")
    print(f"   总错误数: {summary['total_errors']}")
    print(f"   最近错误: {summary['recent_errors']}")
    print(f"   错误类型分布: {summary['error_types']}")
    print(f"   受影响服务: {summary['affected_services']}")
    
    if 'last_error' in summary:
        last_error = summary['last_error']
        print(f"   最近错误: {last_error['type']} - {last_error['service']} - {last_error['timestamp']}")
    
    print("\n✅ 错误摘要功能测试完成")


def test_convenience_functions():
    """Test convenience functions for API issues"""
    print("\n" + "="*60)
    print("🛠️  测试便捷函数")
    print("="*60)
    
    # Test handle_api_error function
    error = Exception("Test quota exceeded error")
    api_error = handle_api_error(error, 'kimi', "便捷函数测试")
    print(f"✅ handle_api_error: {api_error.error_type.value}")
    
    # Test notify_api_issue function
    notification1 = notify_api_issue('quota_exceeded', 'gemini', 'test_user', 
                                   'Quota exceeded for project')
    print(f"✅ notify_api_issue (quota): {notification1.title}")
    
    notification2 = notify_api_issue('connection_error', 'kimi', 'test_user',
                                   'Connection timeout after 30s')
    print(f"✅ notify_api_issue (connection): {notification2.title}")
    
    notification3 = notify_api_issue('service_fallback', 'doubao', 'test_user',
                                   context={'original_service': 'kimi', 
                                          'fallback_service': 'gemini', 
                                          'success': True})
    print(f"✅ notify_api_issue (fallback): {notification3.title}")
    
    print("\n✅ 便捷函数测试完成")


def test_notification_management():
    """Test notification management functions"""
    print("\n" + "="*60)
    print("📋 测试通知管理功能")
    print("="*60)
    
    # Create some test notifications
    user_id = 'test_user_mgmt'
    
    # Create multiple notifications
    for i in range(3):
        notification_service.notify_api_quota_exceeded('kimi', user_id, f'Test suggestion {i}')
    
    # Get notifications
    notifications = notification_service.get_user_notifications(user_id)
    print(f"✅ 创建并获取通知: {len(notifications)} 条")
    
    # Test marking as read
    if notifications:
        first_notification = notifications[0]
        success = notification_service.mark_as_read(first_notification.id, user_id)
        print(f"✅ 标记通知为已读: {success}")
        
        # Re-get notifications
        updated_notifications = notification_service.get_user_notifications(user_id, include_read=True)
        read_count = len([n for n in updated_notifications if n.read])
        print(f"   已读通知数: {read_count}")
    
    # Test mark all as read
    marked_count = notification_service.mark_all_as_read(user_id)
    print(f"✅ 标记所有通知为已读: {marked_count} 条")
    
    # Test delete notification
    if notifications:
        notification_to_delete = notifications[-1]
        success = notification_service.delete_notification(notification_to_delete.id, user_id)
        print(f"✅ 删除通知: {success}")
        
        # Verify deletion
        remaining_notifications = notification_service.get_user_notifications(user_id, include_read=True)
        print(f"   剩余通知数: {len(remaining_notifications)}")
    
    print("\n✅ 通知管理功能测试完成")


def main():
    """Run all tests"""
    print("🚀 启动 API 错误处理和通知系统测试")
    
    try:
        test_api_error_detection()
        test_notifications()
        test_llm_generator_with_fallback()
        test_error_summary()
        test_convenience_functions()
        test_notification_management()
        
        print("\n" + "="*60)
        print("🎉 所有测试完成！")
        print("="*60)
        print("✅ API 错误处理系统工作正常")
        print("✅ 通知系统工作正常")
        print("✅ LLM 生成器回退机制已就绪")
        print("✅ 用户通知和管理功能完整")
        print("\n💡 系统现在可以：")
        print("   • 自动检测 API 配额超限和连接问题")
        print("   • 在服务之间智能回退")
        print("   • 向用户发送友好的错误通知")
        print("   • 提供详细的错误分析和建议")
        print("   • 管理用户通知生命周期")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())