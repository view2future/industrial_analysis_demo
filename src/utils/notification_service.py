#!/usr/bin/env python3
"""
User Notification Service for API Issues
Provides user-friendly notifications about API problems through various channels
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications"""
    API_QUOTA_EXCEEDED = "api_quota_exceeded"
    API_CONNECTION_ERROR = "api_connection_error"
    API_SERVICE_UNAVAILABLE = "api_service_unavailable"
    API_FALLBACK_SUCCESS = "api_fallback_success"
    API_FALLBACK_FAILED = "api_fallback_failed"
    REPORT_GENERATION_SUCCESS = "report_generation_success"
    REPORT_GENERATION_FAILED = "report_generation_failed"


class NotificationSeverity(Enum):
    """Notification severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class Notification:
    """Represents a user notification"""
    id: str
    type: NotificationType
    severity: NotificationSeverity
    title: str
    message: str
    details: Optional[Dict]
    timestamp: datetime
    expires_at: Optional[datetime]
    user_id: Optional[str]
    read: bool = False
    action_url: Optional[str] = None
    action_text: Optional[str] = None


class NotificationService:
    """Service for managing user notifications about API issues"""
    
    def __init__(self, storage_path: str = "data/notifications.json"):
        self.storage_path = storage_path
        self.notifications: List[Notification] = []
        self.load_notifications()
    
    def load_notifications(self):
        """Load notifications from storage"""
        try:
            import os
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.notifications = [
                    Notification(
                        id=item['id'],
                        type=NotificationType(item['type']),
                        severity=NotificationSeverity(item['severity']),
                        title=item['title'],
                        message=item['message'],
                        details=item.get('details'),
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        expires_at=datetime.fromisoformat(item['expires_at']) if item.get('expires_at') else None,
                        user_id=item.get('user_id'),
                        read=item.get('read', False),
                        action_url=item.get('action_url'),
                        action_text=item.get('action_text')
                    )
                    for item in data
                ]
        except (FileNotFoundError, json.JSONDecodeError):
            self.notifications = []
    
    def save_notifications(self):
        """Save notifications to storage"""
        try:
            import os
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            data = []
            for notification in self.notifications:
                notification_data = {
                    'id': notification.id,
                    'type': notification.type.value,
                    'severity': notification.severity.value,
                    'title': notification.title,
                    'message': notification.message,
                    'details': notification.details,
                    'timestamp': notification.timestamp.isoformat(),
                    'expires_at': notification.expires_at.isoformat() if notification.expires_at else None,
                    'user_id': notification.user_id,
                    'read': notification.read,
                    'action_url': notification.action_url,
                    'action_text': notification.action_text
                }
                data.append(notification_data)
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save notifications: {e}")
    
    def create_notification(self, notification_type: NotificationType, 
                          severity: NotificationSeverity,
                          title: str, message: str,
                          details: Optional[Dict] = None,
                          user_id: Optional[str] = None,
                          expires_in_minutes: Optional[int] = None,
                          action_url: Optional[str] = None,
                          action_text: Optional[str] = None) -> Notification:
        """Create a new notification"""
        
        notification_id = f"notif_{datetime.now().timestamp()}_{hash(message) % 10000}"
        
        expires_at = None
        if expires_in_minutes:
            expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        
        notification = Notification(
            id=notification_id,
            type=notification_type,
            severity=severity,
            title=title,
            message=message,
            details=details,
            timestamp=datetime.now(),
            expires_at=expires_at,
            user_id=user_id,
            action_url=action_url,
            action_text=action_text
        )
        
        self.notifications.append(notification)
        self.save_notifications()
        
        logger.info(f"Created notification: {notification_type.value} - {title}")
        return notification
    
    def notify_api_quota_exceeded(self, service_name: str, user_id: Optional[str] = None,
                                suggested_action: str = "") -> Notification:
        """Notify user about API quota exceeded"""
        
        service_display_names = {
            'kimi': 'Kimi (月之暗面)',
            'gemini': 'Google Gemini',
            'doubao': '豆包大模型'
        }
        
        service_name_display = service_display_names.get(service_name, service_name.upper())
        
        title = f"🚫 {service_name_display} API 配额已用完！"
        message = f"您使用的 {service_name_display} 服务的免费配额已经用完。"
        
        if suggested_action:
            message += f"\n\n建议操作：{suggested_action}"
        
        details = {
            'service': service_name,
            'service_display_name': service_name_display,
            'error_type': 'quota_exceeded',
            'suggested_services': [s for s in ['kimi', 'gemini', 'doubao'] if s != service_name]
        }
        
        return self.create_notification(
            NotificationType.API_QUOTA_EXCEEDED,
            NotificationSeverity.ERROR,
            title,
            message,
            details=details,
            user_id=user_id,
            expires_in_minutes=1440,  # 24 hours
            action_url="/settings",
            action_text="前往设置"
        )
    
    def notify_api_connection_error(self, service_name: str, error_message: str,
                                  user_id: Optional[str] = None) -> Notification:
        """Notify user about API connection error"""
        
        service_display_names = {
            'kimi': 'Kimi (月之暗面)',
            'gemini': 'Google Gemini',
            'doubao': '豆包大模型'
        }
        
        service_name_display = service_display_names.get(service_name, service_name.upper())
        
        title = f"❌ 无法连接到 {service_name_display}"
        message = f"连接 {service_name_display} 服务时遇到问题：{error_message}"
        
        details = {
            'service': service_name,
            'service_display_name': service_name_display,
            'error_type': 'connection_error',
            'error_message': error_message
        }
        
        return self.create_notification(
            NotificationType.API_CONNECTION_ERROR,
            NotificationSeverity.WARNING,
            title,
            message,
            details=details,
            user_id=user_id,
            expires_in_minutes=60,  # 1 hour
            action_url="/settings",
            action_text="检查设置"
        )
    
    def notify_service_fallback(self, original_service: str, fallback_service: str,
                              success: bool, user_id: Optional[str] = None) -> Notification:
        """Notify user about service fallback"""
        
        service_display_names = {
            'kimi': 'Kimi',
            'gemini': 'Google Gemini',
            'doubao': '豆包大模型'
        }
        
        original_display = service_display_names.get(original_service, original_service.upper())
        fallback_display = service_display_names.get(fallback_service, fallback_service.upper())
        
        if success:
            title = f"✅ 已自动切换到 {fallback_display}"
            message = f"由于 {original_display} 服务不可用，系统已自动切换到 {fallback_display} 继续为您生成报告。"
            notification_type = NotificationType.API_FALLBACK_SUCCESS
            severity = NotificationSeverity.INFO
        else:
            title = f"⚠️ 服务切换失败"
            message = f"{original_display} 和 {fallback_display} 服务都不可用，请检查设置或稍后再试。"
            notification_type = NotificationType.API_FALLBACK_FAILED
            severity = NotificationSeverity.ERROR
        
        details = {
            'original_service': original_service,
            'fallback_service': fallback_service,
            'success': success
        }
        
        return self.create_notification(
            notification_type,
            severity,
            title,
            message,
            details=details,
            user_id=user_id,
            expires_in_minutes=120,  # 2 hours
            action_url="/settings",
            action_text="查看服务状态"
        )
    
    def notify_report_generation_result(self, success: bool, city: str, industry: str,
                                      service_used: str, user_id: Optional[str] = None,
                                      error_message: Optional[str] = None) -> Notification:
        """Notify user about report generation result"""
        
        service_display_names = {
            'kimi': 'Kimi',
            'gemini': 'Google Gemini',
            'doubao': '豆包大模型'
        }
        
        service_display = service_display_names.get(service_used, service_used.upper())
        
        if success:
            title = f"✅ 报告生成成功！"
            message = f"您的 {city} {industry} 产业分析报告已使用 {service_display} 生成完成。"
            notification_type = NotificationType.REPORT_GENERATION_SUCCESS
            severity = NotificationSeverity.SUCCESS
            details = {
                'city': city,
                'industry': industry,
                'service_used': service_used,
                'success': True
            }
        else:
            title = f"❌ 报告生成失败"
            message = f"生成 {city} {industry} 产业分析报告时遇到问题：{error_message or '未知错误'}"
            notification_type = NotificationType.REPORT_GENERATION_FAILED
            severity = NotificationSeverity.ERROR
            details = {
                'city': city,
                'industry': industry,
                'service_used': service_used,
                'success': False,
                'error_message': error_message
            }
        
        return self.create_notification(
            notification_type,
            severity,
            title,
            message,
            details=details,
            user_id=user_id,
            expires_in_minutes=1440 if success else 60,  # 24 hours for success, 1 hour for failure
            action_url="/reports" if success else "/generate-report",
            action_text="查看报告" if success else "重新生成"
        )
    
    def get_user_notifications(self, user_id: str, include_read: bool = False) -> List[Notification]:
        """Get notifications for a specific user"""
        
        # Clean up expired notifications first
        self.cleanup_expired_notifications()
        
        user_notifications = [
            notification for notification in self.notifications
            if notification.user_id == user_id and (include_read or not notification.read)
        ]
        
        # Sort by timestamp (newest first)
        user_notifications.sort(key=lambda x: x.timestamp, reverse=True)
        
        return user_notifications
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        for notification in self.notifications:
            if notification.id == notification_id and notification.user_id == user_id:
                notification.read = True
                self.save_notifications()
                return True
        return False
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read"""
        count = 0
        for notification in self.notifications:
            if notification.user_id == user_id and not notification.read:
                notification.read = True
                count += 1
        
        if count > 0:
            self.save_notifications()
        
        return count
    
    def cleanup_expired_notifications(self):
        """Remove expired notifications"""
        now = datetime.now()
        original_count = len(self.notifications)
        
        self.notifications = [
            notification for notification in self.notifications
            if notification.expires_at is None or notification.expires_at > now
        ]
        
        removed_count = original_count - len(self.notifications)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired notifications")
            self.save_notifications()
    
    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        original_count = len(self.notifications)
        
        self.notifications = [
            notification for notification in self.notifications
            if not (notification.id == notification_id and notification.user_id == user_id)
        ]
        
        deleted = original_count != len(self.notifications)
        if deleted:
            self.save_notifications()
        
        return deleted
    
    def get_notification_stats(self, user_id: str) -> Dict:
        """Get notification statistics for a user"""
        user_notifications = self.get_user_notifications(user_id, include_read=True)
        
        total = len(user_notifications)
        unread = len([n for n in user_notifications if not n.read])
        
        by_severity = {}
        by_type = {}
        
        for notification in user_notifications:
            by_severity[notification.severity.value] = by_severity.get(notification.severity.value, 0) + 1
            by_type[notification.type.value] = by_type.get(notification.type.value, 0) + 1
        
        return {
            'total': total,
            'unread': unread,
            'by_severity': by_severity,
            'by_type': by_type,
            'has_recent_errors': any(
                n.severity in [NotificationSeverity.ERROR, NotificationSeverity.WARNING] and
                not n.read and
                (datetime.now() - n.timestamp).days <= 1
                for n in user_notifications
            )
        }


# Global notification service instance
notification_service = NotificationService()


def notify_api_issue(error_type: str, service_name: str, user_id: Optional[str] = None,
                    error_message: Optional[str] = None, context: Optional[Dict] = None):
    """Convenience function to notify about API issues"""
    
    if error_type == 'quota_exceeded':
        suggested_action = context.get('suggested_action', '') if context else ''
        return notification_service.notify_api_quota_exceeded(service_name, user_id, suggested_action)
    
    elif error_type == 'connection_error':
        error_msg = error_message or '连接失败'
        return notification_service.notify_api_connection_error(service_name, error_msg, user_id)
    
    elif error_type == 'service_fallback':
        original_service = context.get('original_service', service_name) if context else service_name
        fallback_service = context.get('fallback_service', '') if context else ''
        success = context.get('success', False) if context else False
        return notification_service.notify_service_fallback(original_service, fallback_service, success, user_id)
    
    else:
        logger.warning(f"Unknown API issue type: {error_type}")
        return None