#!/usr/bin/env python3
"""
API Routes for User Notifications and API Status
Handles user notifications about API issues and system status
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.utils.notification_service import notification_service
from src.utils.api_error_handler import api_error_handler
import logging

logger = logging.getLogger(__name__)

# Create blueprint for notification routes
notification_bp = Blueprint('notifications', __name__)


@notification_bp.route('/api/notifications')
@login_required
def api_get_notifications():
    """Get current user's notifications"""
    try:
        include_read = request.args.get('include_read', 'false').lower() == 'true'
        notifications = notification_service.get_user_notifications(str(current_user.id), include_read)
        
        # Convert notifications to JSON-serializable format
        notification_data = []
        for notification in notifications:
            notification_data.append({
                'id': notification.id,
                'type': notification.type.value,
                'severity': notification.severity.value,
                'title': notification.title,
                'message': notification.message,
                'details': notification.details,
                'timestamp': notification.timestamp.isoformat(),
                'expires_at': notification.expires_at.isoformat() if notification.expires_at else None,
                'read': notification.read,
                'action_url': notification.action_url,
                'action_text': notification.action_text
            })
        
        return jsonify({
            'success': True,
            'notifications': notification_data,
            'count': len(notification_data),
            'unread_count': len([n for n in notifications if not n.read])
        })
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'notifications': [],
            'count': 0,
            'unread_count': 0
        }), 500


@notification_bp.route('/api/notifications/stats')
@login_required
def api_get_notification_stats():
    """Get notification statistics for current user"""
    try:
        stats = notification_service.get_notification_stats(str(current_user.id))
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'stats': {'total': 0, 'unread': 0, 'has_recent_errors': False}
        }), 500


@notification_bp.route('/api/notifications/<notification_id>/read', methods=['POST'])
@login_required
def api_mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        success = notification_service.mark_as_read(notification_id, str(current_user.id))
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification marked as read'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Notification not found or access denied'
            }), 404
            
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/notifications/read-all', methods=['POST'])
@login_required
def api_mark_all_notifications_read():
    """Mark all notifications as read for current user"""
    try:
        count = notification_service.mark_all_as_read(str(current_user.id))
        
        return jsonify({
            'success': True,
            'message': f'{count} notifications marked as read',
            'count': count
        })
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/notifications/<notification_id>', methods=['DELETE'])
@login_required
def api_delete_notification(notification_id):
    """Delete a notification"""
    try:
        success = notification_service.delete_notification(notification_id, str(current_user.id))
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification deleted'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Notification not found or access denied'
            }), 404
            
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/api-status')
@login_required
def api_get_api_status():
    """Get current API status and error summary"""
    try:
        error_summary = api_error_handler.get_error_summary()
        
        # Get recent API errors
        recent_errors = []
        if hasattr(api_error_handler, 'error_history') and api_error_handler.error_history:
            # Get last 5 errors
            for error in api_error_handler.error_history[-5:]:
                recent_errors.append({
                    'type': error.error_type.value,
                    'service': error.service.value,
                    'message': error.user_friendly_message,
                    'timestamp': error.timestamp.isoformat(),
                    'retry_after': error.retry_after
                })
        
        return jsonify({
            'success': True,
            'error_summary': error_summary,
            'recent_errors': recent_errors,
            'has_recent_issues': len(recent_errors) > 0
        })
        
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_summary': {'status': 'error', 'message': 'Unable to get API status'},
            'recent_errors': [],
            'has_recent_issues': False
        }), 500


@notification_bp.route('/api/api-status/clear', methods=['POST'])
@login_required
def api_clear_api_errors():
    """Clear API error history (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        
        # Clear error history
        if hasattr(api_error_handler, 'error_history'):
            api_error_handler.clear_error_history()
        
        return jsonify({
            'success': True,
            'message': 'API error history cleared'
        })
        
    except Exception as e:
        logger.error(f"Error clearing API errors: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Template context processor for notifications
def inject_notification_context():
    """Inject notification context into templates"""
    if not current_user or not current_user.is_authenticated:
        return {}
    
    try:
        # Get unread notification count
        notifications = notification_service.get_user_notifications(str(current_user.id))
        unread_count = len([n for n in notifications if not n.read])
        
        # Get API status
        error_summary = api_error_handler.get_error_summary()
        has_api_issues = error_summary.get('status') == 'error_summary' and error_summary.get('recent_errors', 0) > 0
        
        return {
            'unread_notification_count': unread_count,
            'has_api_issues': has_api_issues,
            'api_error_summary': error_summary
        }
    except Exception as e:
        logger.error(f"Error injecting notification context: {e}")
        return {
            'unread_notification_count': 0,
            'has_api_issues': False,
            'api_error_summary': {'status': 'ok'}
        }


# Register the blueprint
def register_notification_routes(app):
    """Register notification routes with the Flask app"""
    app.register_blueprint(notification_bp)
    
    # Register context processor
    app.context_processor(inject_notification_context)