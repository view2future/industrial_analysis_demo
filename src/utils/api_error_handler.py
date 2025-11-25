#!/usr/bin/env python3
"""
API Error Handler for managing quota limits and connection issues
Provides comprehensive error detection, user notifications, and fallback mechanisms
"""

import re
import logging
import time
from typing import Dict, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class APIErrorType(Enum):
    """Types of API errors that can occur"""
    QUOTA_EXCEEDED = "quota_exceeded"
    RATE_LIMITED = "rate_limited"
    CONNECTION_TIMEOUT = "connection_timeout"
    CONNECTION_REFUSED = "connection_refused"
    SERVICE_UNAVAILABLE = "service_unavailable"
    AUTHENTICATION_ERROR = "authentication_error"
    INVALID_REQUEST = "invalid_request"
    UNKNOWN_ERROR = "unknown_error"


class APIService(Enum):
    """Supported API services"""
    KIMI = "kimi"
    GEMINI = "gemini"
    DOUBAO = "doubao"


@dataclass
class APIError:
    """Represents an API error with context"""
    error_type: APIErrorType
    service: APIService
    message: str
    original_error: Exception
    timestamp: datetime
    retry_after: Optional[int] = None  # seconds to wait before retry
    suggested_action: Optional[str] = None
    user_friendly_message: Optional[str] = None


@dataclass
class APIQuotaInfo:
    """Information about API quota status"""
    service: APIService
    quota_used: int
    quota_limit: int
    quota_remaining: int
    reset_time: Optional[datetime]
    last_request_time: Optional[datetime]


class APIErrorHandler:
    """Handles API errors with intelligent detection and user notifications"""
    
    # Error patterns for different services
    ERROR_PATTERNS = {
        APIService.KIMI: {
            APIErrorType.QUOTA_EXCEEDED: [
                r'quota.*exceeded',
                r'rate.*limit.*exceeded',
                r'insufficient.*quota',
                r'配额.*已用完',
                r'配额.*不足',
                r'超出.*配额',
                r'余额.*不足'
            ],
            APIErrorType.RATE_LIMITED: [
                r'too.*many.*requests',
                r'rate.*limit',
                r'request.*limit'
            ],
            APIErrorType.CONNECTION_TIMEOUT: [
                r'timeout',
                r'timed.*out',
                r'connection.*timeout'
            ],
            APIErrorType.CONNECTION_REFUSED: [
                r'connection.*refused',
                r'refused.*connection',
                r'unable.*to.*connect'
            ],
            APIErrorType.SERVICE_UNAVAILABLE: [
                r'service.*unavailable',
                r'server.*error',
                r'internal.*error',
                r'maintenance'
            ],
            APIErrorType.AUTHENTICATION_ERROR: [
                r'authentication.*failed',
                r'invalid.*api.*key',
                r'unauthorized',
                r'认证.*失败',
                r'无效.*密钥'
            ]
        },
        APIService.GEMINI: {
            APIErrorType.QUOTA_EXCEEDED: [
                r'quota.*exceeded',
                r'project.*quota',
                r'user.*quota',
                r'quota.*limit',
                r'配额.*已用完',
                r'配额.*不足',
                r'超出.*配额',
                r'余额.*不足'
            ],
            APIErrorType.RATE_LIMITED: [
                r'too.*many.*requests',
                r'rate.*limit.*exceeded',
                r'rate.*limit',
                r'quota.*per.*minute'
            ],
            APIErrorType.CONNECTION_TIMEOUT: [
                r'timeout',
                r'deadline.*exceeded',
                r'connection.*timeout'
            ],
            APIErrorType.CONNECTION_REFUSED: [
                r'connection.*refused',
                r'unreachable',
                r'network.*error'
            ],
            APIErrorType.SERVICE_UNAVAILABLE: [
                r'service.*unavailable',
                r'internal.*server.*error',
                r'temporarily.*unavailable'
            ],
            APIErrorType.AUTHENTICATION_ERROR: [
                r'api.*key.*not.*valid',
                r'permission.*denied',
                r'authentication.*failed'
            ]
        },
        APIService.DOUBAO: {
            APIErrorType.QUOTA_EXCEEDED: [
                r'quota.*exceeded',
                r'insufficient.*balance',
                r'余额.*不足'
            ],
            APIErrorType.RATE_LIMITED: [
                r'rate.*limit',
                r'too.*many.*requests'
            ],
            APIErrorType.CONNECTION_TIMEOUT: [
                r'timeout',
                r'connection.*timeout'
            ],
            APIErrorType.CONNECTION_REFUSED: [
                r'connection.*refused',
                r'unable.*to.*connect'
            ],
            APIErrorType.SERVICE_UNAVAILABLE: [
                r'service.*unavailable',
                r'server.*error'
            ],
            APIErrorType.AUTHENTICATION_ERROR: [
                r'authentication.*failed',
                r'invalid.*credentials'
            ]
        }
    }
    
    def __init__(self):
        self.quota_cache: Dict[APIService, APIQuotaInfo] = {}
        self.error_history: List[APIError] = []
        self.service_fallback_order = [APIService.KIMI, APIService.GEMINI, APIService.DOUBAO]
        
    def detect_error_type(self, error: Exception, service: APIService) -> APIError:
        """Intelligently detect the type of API error"""
        error_message = str(error).lower()
        error_type = APIErrorType.UNKNOWN_ERROR
        
        # Check against known patterns for the service
        service_patterns = self.ERROR_PATTERNS.get(service, {})
        
        for api_error_type, patterns in service_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    error_type = api_error_type
                    break
            if error_type != APIErrorType.UNKNOWN_ERROR:
                break
        
        # Additional heuristics for common error types
        if error_type == APIErrorType.UNKNOWN_ERROR:
            error_type = self._classify_error_by_heuristics(error, error_message)
        
        # Generate user-friendly message and suggested actions
        user_message = self._generate_user_message(error_type, service)
        suggested_action = self._generate_suggested_action(error_type, service)
        retry_after = self._calculate_retry_after(error_type, error)
        
        api_error = APIError(
            error_type=error_type,
            service=service,
            message=str(error),
            original_error=error,
            timestamp=datetime.now(),
            retry_after=retry_after,
            suggested_action=suggested_action,
            user_friendly_message=user_message
        )
        
        # Store in history
        self.error_history.append(api_error)
        
        return api_error
    
    def _classify_error_by_heuristics(self, error: Exception, error_message: str) -> APIErrorType:
        """Classify errors using additional heuristics"""
        # Connection-related errors
        if any(keyword in error_message for keyword in ['connection', 'network', 'timeout', 'refused']):
            if 'timeout' in error_message:
                return APIErrorType.CONNECTION_TIMEOUT
            elif 'refused' in error_message:
                return APIErrorType.CONNECTION_REFUSED
            else:
                return APIErrorType.SERVICE_UNAVAILABLE
        
        # Check for specific exception types
        error_type_name = type(error).__name__.lower()
        
        if 'timeout' in error_type_name:
            return APIErrorType.CONNECTION_TIMEOUT
        elif 'connection' in error_type_name:
            return APIErrorType.CONNECTION_REFUSED
        elif any(auth_word in error_type_name for auth_word in ['auth', 'permission', 'unauthorized']):
            return APIErrorType.AUTHENTICATION_ERROR
        
        return APIErrorType.UNKNOWN_ERROR
    
    def _generate_user_message(self, error_type: APIErrorType, service: APIService) -> str:
        """Generate user-friendly error messages"""
        messages = {
            APIErrorType.QUOTA_EXCEEDED: {
                APIService.KIMI: "🚫 Kimi API 配额已用完！本月免费额度已耗尽，请考虑以下选项：",
                APIService.GEMINI: "🚫 Google Gemini API 配额已用完！请检查您的 Google Cloud 配额设置：",
                APIService.DOUBAO: "🚫 豆包大模型 API 余额不足！请充值或更换其他服务："
            },
            APIErrorType.RATE_LIMITED: {
                APIService.KIMI: "⏳ Kimi API 请求过于频繁！请稍后再试：",
                APIService.GEMINI: "⏳ Google Gemini API 请求过于频繁！请稍后再试：",
                APIService.DOUBAO: "⏳ 豆包大模型 API 请求过于频繁！请稍后再试："
            },
            APIErrorType.CONNECTION_TIMEOUT: "⏰ 连接超时！请检查网络连接或稍后再试。",
            APIErrorType.CONNECTION_REFUSED: "❌ 无法连接到 AI 服务！请检查网络设置或防火墙配置。",
            APIErrorType.SERVICE_UNAVAILABLE: "🔧 AI 服务暂时不可用！服务可能正在维护中，请稍后再试。",
            APIErrorType.AUTHENTICATION_ERROR: "🔑 API 密钥验证失败！请检查配置文件中的 API 密钥是否正确。",
            APIErrorType.UNKNOWN_ERROR: "❓ 发生未知错误！请查看日志详情或联系技术支持。"
        }
        
        service_messages = messages.get(error_type, messages[APIErrorType.UNKNOWN_ERROR])
        if isinstance(service_messages, dict):
            return service_messages.get(service, service_messages[APIService.KIMI])
        return service_messages
    
    def _generate_suggested_action(self, error_type: APIErrorType, service: APIService) -> str:
        """Generate suggested actions for users"""
        actions = {
            APIErrorType.QUOTA_EXCEEDED: {
                APIService.KIMI: "建议：1) 切换到 Gemini 或豆包大模型 2) 等待下个月配额重置 3) 购买付费套餐",
                APIService.GEMINI: "建议：1) 切换到 Kimi 或豆包大模型 2) 在 Google Cloud Console 中增加配额 3) 使用其他 Google 项目",
                APIService.DOUBAO: "建议：1) 切换到 Kimi 或 Gemini 2) 为豆包大模型账户充值 3) 使用其他服务"
            },
            APIErrorType.RATE_LIMITED: "建议：等待几分钟后重试，或切换到其他 AI 服务。",
            APIErrorType.CONNECTION_TIMEOUT: "建议：检查网络连接，刷新页面，或稍后再试。",
            APIErrorType.CONNECTION_REFUSED: "建议：检查防火墙设置，确认网络可以访问外部服务，或联系网络管理员。",
            APIErrorType.SERVICE_UNAVAILABLE: "建议：等待服务恢复，或切换到其他可用的 AI 服务。",
            APIErrorType.AUTHENTICATION_ERROR: "建议：检查 config.json 文件中的 API 密钥配置，确保密钥有效且未过期。",
            APIErrorType.UNKNOWN_ERROR: "建议：查看详细错误日志，尝试重新操作，或联系技术支持。"
        }
        
        service_actions = actions.get(error_type, actions[APIErrorType.UNKNOWN_ERROR])
        if isinstance(service_actions, dict):
            return service_actions.get(service, service_actions[APIService.KIMI])
        return service_actions
    
    def _calculate_retry_after(self, error_type: APIErrorType, error: Exception) -> Optional[int]:
        """Calculate recommended retry delay"""
        if error_type == APIErrorType.RATE_LIMITED:
            return 60  # 1 minute for rate limiting
        elif error_type == APIErrorType.CONNECTION_TIMEOUT:
            return 30  # 30 seconds for connection issues
        elif error_type == APIErrorType.SERVICE_UNAVAILABLE:
            return 300  # 5 minutes for service issues
        elif error_type == APIErrorType.QUOTA_EXCEEDED:
            return 3600  # 1 hour for quota issues (or next day)
        
        # Try to extract retry-after from error message
        retry_match = re.search(r'retry.*after.*(\d+)', str(error), re.IGNORECASE)
        if retry_match:
            return int(retry_match.group(1))
        
        return None
    
    def get_fallback_service(self, failed_service: APIService, 
                           available_services: List[APIService]) -> Optional[APIService]:
        """Get the next best available service"""
        # Remove the failed service from fallback order
        fallback_order = [s for s in self.service_fallback_order if s != failed_service]
        
        # Return the first available service
        for service in fallback_order:
            if service in available_services:
                return service
        
        return None
    
    def is_quota_exceeded(self, service: APIService, error: Exception) -> bool:
        """Check if the error is specifically a quota exceeded error"""
        api_error = self.detect_error_type(error, service)
        return api_error.error_type == APIErrorType.QUOTA_EXCEEDED
    
    def is_connection_issue(self, service: APIService, error: Exception) -> bool:
        """Check if the error is a connection-related issue"""
        api_error = self.detect_error_type(error, service)
        connection_errors = [
            APIErrorType.CONNECTION_TIMEOUT,
            APIErrorType.CONNECTION_REFUSED,
            APIErrorType.SERVICE_UNAVAILABLE
        ]
        return api_error.error_type in connection_errors
    
    def get_error_summary(self) -> Dict[str, any]:
        """Get a summary of recent errors"""
        if not self.error_history:
            return {"status": "ok", "message": "No recent errors"}
        
        recent_errors = self.error_history[-10:]  # Last 10 errors
        
        error_counts = {}
        service_counts = {}
        
        for error in recent_errors:
            error_counts[error.error_type.value] = error_counts.get(error.error_type.value, 0) + 1
            service_counts[error.service.value] = service_counts.get(error.service.value, 0) + 1
        
        return {
            "status": "error_summary",
            "total_errors": len(self.error_history),
            "recent_errors": len(recent_errors),
            "error_types": error_counts,
            "affected_services": service_counts,
            "last_error": {
                "type": recent_errors[-1].error_type.value,
                "service": recent_errors[-1].service.value,
                "message": recent_errors[-1].user_friendly_message,
                "timestamp": recent_errors[-1].timestamp.isoformat()
            }
        }
    
    def clear_error_history(self):
        """Clear the error history"""
        self.error_history.clear()
    
    def should_retry_immediately(self, error: APIError) -> bool:
        """Determine if the error warrants immediate retry"""
        # Don't retry quota exceeded errors immediately
        if error.error_type == APIErrorType.QUOTA_EXCEEDED:
            return False
        
        # Don't retry authentication errors immediately
        if error.error_type == APIErrorType.AUTHENTICATION_ERROR:
            return False
        
        # Retry connection issues and temporary failures
        retryable_errors = [
            APIErrorType.CONNECTION_TIMEOUT,
            APIErrorType.CONNECTION_REFUSED,
            APIErrorType.SERVICE_UNAVAILABLE,
            APIErrorType.RATE_LIMITED
        ]
        
        return error.error_type in retryable_errors


# Global error handler instance
api_error_handler = APIErrorHandler()


def handle_api_error(error: Exception, service: str, context: str = "") -> APIError:
    """Convenience function to handle API errors"""
    try:
        service_enum = APIService(service.lower())
    except ValueError:
        service_enum = APIService.KIMI  # Default fallback
    
    api_error = api_error_handler.detect_error_type(error, service_enum)
    
    logger.error(f"API Error in {context}: {api_error.user_friendly_message}")
    logger.error(f"Original error: {api_error.message}")
    logger.error(f"Suggested action: {api_error.suggested_action}")
    
    return api_error