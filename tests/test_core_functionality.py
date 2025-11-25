#!/usr/bin/env python3
"""
Test core API error handling functionality without importing the full LLM generator
This tests the error handler and notification service independently
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.api_error_handler import api_error_handler, APIErrorType, APIService, handle_api_error
from src.utils.notification_service import notification_service, notify_api_issue
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
    
    success_count = 0
    for error, service, expected_type in test_errors:
        api_error = api_error_handler.detect_error_type(error, service)
        result = "✅" if api_error.error_type.value == expected_type else "❌"
        if api_error.error_type.value == expected_type:
            success_count += 1
        
        print(f"{result} {service.value.upper()} - {str(error)[:50]}... -> {api_error.error_type.value}")
        
        if api_error.error_type.value == expected_type:
            print(f"   📝 用户消息: {api_error.user_friendly_message}")
            print(f"   💡 建议操作: {api_error.suggested_action}")
    
    print(f"\n✅ API 错误检测测试完成 - 成功率: {success_count}/{len(test_errors)}")
    return success_count == len(test_errors)


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
    
    success = len(notifications) >= 5  # We created 5 notifications
    print(f"\n✅ 通知系统测试完成 - {'成功' if success else '失败'}")
    return success


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
    
    success = summary['total_errors'] >= 5
    print(f"\n✅ 错误摘要功能测试完成 - {'成功' if success else '失败'}")
    return success


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
    print(f"✅ notify_api_issue (quota): {notification1.title if notification1 else 'None'}")
    
    notification2 = notify_api_issue('connection_error', 'kimi', 'test_user',
                                   'Connection timeout after 30s')
    print(f"✅ notify_api_issue (connection): {notification2.title if notification2 else 'None'}")
    
    notification3 = notify_api_issue('service_fallback', 'doubao', 'test_user',
                                   context={'original_service': 'kimi', 
                                          'fallback_service': 'gemini', 
                                          'success': True})
    print(f"✅ notify_api_issue (fallback): {notification3.title if notification3 else 'None'}")
    
    success = api_error.error_type.value == 'quota_exceeded'
    print(f"\n✅ 便捷函数测试完成 - {'成功' if success else '失败'}")
    return success


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
    success = True
    if notifications:
        first_notification = notifications[0]
        mark_success = notification_service.mark_as_read(first_notification.id, user_id)
        print(f"✅ 标记通知为已读: {mark_success}")
        success = success and mark_success
        
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
        delete_success = notification_service.delete_notification(notification_to_delete.id, user_id)
        print(f"✅ 删除通知: {delete_success}")
        success = success and delete_success
        
        # Verify deletion
        remaining_notifications = notification_service.get_user_notifications(user_id, include_read=True)
        print(f"   剩余通知数: {len(remaining_notifications)}")
    
    print(f"\n✅ 通知管理功能测试完成 - {'成功' if success else '失败'}")
    return success


def test_fallback_mechanism():
    """Test service fallback mechanism logic"""
    print("\n" + "="*60)
    print("🔄 测试服务回退机制逻辑")
    print("="*60)
    
    # Test fallback service selection
    available_services = [APIService.KIMI, APIService.GEMINI, APIService.DOUBAO]
    
    # Test fallback from Kimi
    fallback_service = api_error_handler.get_fallback_service(APIService.KIMI, available_services)
    expected_fallback = APIService.GEMINI
    success1 = fallback_service == expected_fallback
    print(f"✅ Kimi -> 回退服务: {fallback_service.value if fallback_service else 'None'} (期望: {expected_fallback.value})")
    
    # Test fallback from Gemini
    fallback_service = api_error_handler.get_fallback_service(APIService.GEMINI, available_services)
    # Should skip Kimi (failed) and try Doubao
    expected_fallback = APIService.KIMI
    success2 = fallback_service == expected_fallback
    print(f"✅ Gemini -> 回退服务: {fallback_service.value if fallback_service else 'None'} (期望: {expected_fallback.value})")
    
    # Test fallback with limited services
    limited_services = [APIService.KIMI, APIService.GEMINI]
    fallback_service = api_error_handler.get_fallback_service(APIService.KIMI, limited_services)
    expected_fallback = APIService.GEMINI
    success3 = fallback_service == expected_fallback
    print(f"✅ 有限服务回退: {fallback_service.value if fallback_service else 'None'} (期望: {expected_fallback.value})")
    
    # Test no available fallback
    no_fallback_services = [APIService.KIMI]  # Only the failed service
    fallback_service = api_error_handler.get_fallback_service(APIService.KIMI, no_fallback_services)
    success4 = fallback_service is None
    print(f"✅ 无可用回退: {fallback_service} (期望: None)")
    
    success = success1 and success2 and success3 and success4
    print(f"\n✅ 服务回退机制逻辑测试完成 - {'成功' if success else '失败'}")
    return success


def main():
    """Run all tests"""
    print("🚀 启动核心功能测试（不依赖 LLM 生成器）")
    
    test_results = []
    
    try:
        test_results.append(test_api_error_detection())
        test_results.append(test_notifications())
        test_results.append(test_error_summary())
        test_results.append(test_convenience_functions())
        test_results.append(test_notification_management())
        test_results.append(test_fallback_mechanism())
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print("\n" + "="*60)
        print(f"🎉 核心功能测试完成！通过率: {passed_tests}/{total_tests}")
        print("="*60)
        
        if passed_tests == total_tests:
            print("✅ 所有核心功能测试通过！")
            print("\n💡 系统核心功能已就绪：")
            print("   • API 错误检测和分类")
            print("   • 用户通知系统")
            print("   • 错误摘要和统计")
            print("   • 服务回退机制逻辑")
            print("   • 通知管理功能")
            print("\n🔄 下一步：测试完整的 LLM 生成器集成")
            return 0
        else:
            print(f"❌ {total_tests - passed_tests} 个测试失败")
            return 1
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())